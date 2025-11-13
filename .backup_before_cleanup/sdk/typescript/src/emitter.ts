/**
 * Production-grade EventEmitter for TypeScript/JavaScript
 * Supports browser (sendBeacon/fetch) and Node.js runtimes
 */

import { BaseEvent, RAIAEvent, Env } from './types';
import { Redactor } from './redactor';
import { EventSigner } from './signer';

export enum TransportType {
  HTTP = 'http',
  BEACON = 'beacon', // Browser-only: navigator.sendBeacon
}

export interface EmitterConfig {
  // Identity
  tenant: string;
  project: string;
  agent_id: string;
  region?: string;
  deployment?: 'dev' | 'staging' | 'prod';

  // Transport
  transport: TransportType;
  endpoint: string;
  apiKey?: string;

  // Batching
  batchSize?: number;
  maxBatchBytes?: number;
  flushIntervalMs?: number;
  maxQueueSize?: number;

  // Retry
  maxRetries?: number;
  retryBaseDelayMs?: number;
  retryMaxDelayMs?: number;

  // Security
  hmacSecret?: string;
  enableSigning?: boolean;

  // Schema
  schemaVersion?: string;
  sdkVersion?: string;

  // LLM defaults
  llm?: string;
  llmVersion?: string;
  seed?: number;
  temperature?: number;
}

interface QueuedEvent {
  event: Partial<RAIAEvent>;
  timestamp: number;
}

export class EventEmitter {
  private config: Required<EmitterConfig>;
  private redactor?: Redactor;
  private signer?: EventSigner;

  private queue: QueuedEvent[] = [];
  private batch: Partial<RAIAEvent>[] = [];
  private batchBytes = 0;
  private flushTimer?: any;
  private isBrowser: boolean;

  // Metrics
  private eventsEmitted = 0;
  private eventsDropped = 0;
  private batchesSent = 0;
  private batchesFailed = 0;

  constructor(config: EmitterConfig, redactor?: Redactor, signer?: EventSigner) {
    // Set defaults
    this.config = {
      ...config,
      region: config.region ?? 'us-east-1',
      deployment: config.deployment ?? 'prod',
      batchSize: config.batchSize ?? 100,
      maxBatchBytes: config.maxBatchBytes ?? 1_000_000,
      flushIntervalMs: config.flushIntervalMs ?? 5000,
      maxQueueSize: config.maxQueueSize ?? 10000,
      maxRetries: config.maxRetries ?? 3,
      retryBaseDelayMs: config.retryBaseDelayMs ?? 100,
      retryMaxDelayMs: config.retryMaxDelayMs ?? 10000,
      enableSigning: config.enableSigning ?? true,
      schemaVersion: config.schemaVersion ?? '1.0.0',
      sdkVersion: config.sdkVersion ?? '1.0.0',
    } as Required<EmitterConfig>;

    this.redactor = redactor;
    this.signer = signer;

    // Detect environment
    this.isBrowser = typeof window !== 'undefined' && typeof window.document !== 'undefined';

    this.startPeriodicFlush();
  }

  /**
   * Emit an event (non-blocking).
   */
  emit(event: Partial<RAIAEvent>): void {
    try {
      // Enrich event
      event = this.enrichEvent(event);

      // Redact PII/PHI
      if (this.redactor) {
        const [redactedEvent, redactionMetadata] = this.redactor.redact(event);
        event = redactedEvent;
        if (redactionMetadata.applied) {
          event.redaction = redactionMetadata;
        }
      }

      // Sign
      if (this.signer && this.config.enableSigning) {
        const signature = this.signer.sign(event);
        event._signature = signature;
      }

      // Add to queue
      if (this.queue.length >= this.config.maxQueueSize) {
        this.eventsDropped++;
        console.warn('RAIA: Queue full, dropping event');
        return;
      }

      this.queue.push({ event, timestamp: Date.now() });
      this.eventsEmitted++;

      // Process queue
      this.processQueue();
    } catch (error) {
      console.error('RAIA: Failed to emit event:', error);
      this.eventsDropped++;
    }
  }

  /**
   * Flush pending events immediately.
   */
  async flush(): Promise<void> {
    // Process remaining queue
    while (this.queue.length > 0) {
      this.processQueue();
    }

    // Send current batch
    if (this.batch.length > 0) {
      await this.sendBatch(this.batch);
      this.batch = [];
      this.batchBytes = 0;
    }
  }

  /**
   * Gracefully shutdown, flushing pending events.
   */
  async shutdown(timeoutMs: number = 30000): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    const flushPromise = this.flush();
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Shutdown timeout')), timeoutMs)
    );

    try {
      await Promise.race([flushPromise, timeoutPromise]);
    } catch (error) {
      console.error('RAIA: Shutdown error:', error);
    }

    console.log(
      `RAIA: Shutdown complete. Stats: emitted=${this.eventsEmitted}, ` +
        `dropped=${this.eventsDropped}, sent=${this.batchesSent}, failed=${this.batchesFailed}`
    );
  }

  /**
   * Get health status.
   */
  getHealth() {
    return {
      status: this.batchesFailed > this.batchesSent * 0.1 ? 'degraded' : 'healthy',
      queueSize: this.queue.length,
      batchSize: this.batch.length,
      eventsEmitted: this.eventsEmitted,
      eventsDropped: this.eventsDropped,
      batchesSent: this.batchesSent,
      batchesFailed: this.batchesFailed,
    };
  }

  private enrichEvent(event: Partial<RAIAEvent>): Partial<RAIAEvent> {
    // Generate IDs if missing
    if (!event.event_id) {
      event.event_id = this.generateUUID();
    }
    if (!event.ts) {
      event.ts = new Date().toISOString();
    }

    // Add env metadata
    if (!event.env) {
      event.env = {} as Env;
    }

    const env = event.env;
    env.sdk_version = this.config.sdkVersion;
    env.schema_version = this.config.schemaVersion;
    env.tenant = this.config.tenant;
    env.project = this.config.project;
    env.region = this.config.region;
    env.deployment = this.config.deployment;

    if (this.config.llm) env.llm = this.config.llm;
    if (this.config.llmVersion) env.llm_version = this.config.llmVersion;
    if (this.config.seed !== undefined) env.seed = this.config.seed;
    if (this.config.temperature !== undefined) env.temperature = this.config.temperature;

    return event;
  }

  private processQueue(): void {
    while (this.queue.length > 0) {
      const queued = this.queue[0];
      const eventJson = JSON.stringify(queued.event);
      const eventBytes = new Blob([eventJson]).size;

      // Check if adding this event would exceed limits
      const wouldExceed =
        this.batch.length >= this.config.batchSize || this.batchBytes + eventBytes > this.config.maxBatchBytes;

      if (wouldExceed && this.batch.length > 0) {
        // Send current batch first
        this.sendBatch([...this.batch]);
        this.batch = [];
        this.batchBytes = 0;
      }

      // Add to batch
      this.queue.shift();
      this.batch.push(queued.event);
      this.batchBytes += eventBytes;

      // If batch is now full, send immediately
      if (this.batch.length >= this.config.batchSize) {
        this.sendBatch([...this.batch]);
        this.batch = [];
        this.batchBytes = 0;
        break;
      }
    }
  }

  private startPeriodicFlush(): void {
    this.flushTimer = setInterval(() => {
      if (this.batch.length > 0) {
        this.sendBatch([...this.batch]);
        this.batch = [];
        this.batchBytes = 0;
      }
    }, this.config.flushIntervalMs);

    // Handle page unload in browser
    if (this.isBrowser) {
      window.addEventListener('beforeunload', () => {
        if (this.batch.length > 0) {
          this.sendBatchSync(this.batch);
        }
      });
    }
  }

  private async sendBatch(batch: Partial<RAIAEvent>[]): Promise<void> {
    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        if (this.config.transport === TransportType.BEACON && this.isBrowser) {
          this.sendBatchSync(batch);
        } else {
          await this.sendBatchHTTP(batch);
        }
        this.batchesSent++;
        return;
      } catch (error) {
        console.warn(`RAIA: Batch send failed (attempt ${attempt + 1}/${this.config.maxRetries + 1}):`, error);

        if (attempt < this.config.maxRetries) {
          const delay = Math.min(
            this.config.retryBaseDelayMs * Math.pow(2, attempt),
            this.config.retryMaxDelayMs
          );
          const jitter = Math.random() * delay * 0.1;
          await this.sleep(delay + jitter);
        } else {
          this.batchesFailed++;
          console.error('RAIA: Batch send failed after retries');
        }
      }
    }
  }

  private async sendBatchHTTP(batch: Partial<RAIAEvent>[]): Promise<void> {
    const ndjson = batch.map((e) => JSON.stringify(e)).join('\n');

    const headers: Record<string, string> = {
      'Content-Type': 'application/x-ndjson',
      'X-RAIA-Tenant': this.config.tenant,
      'X-RAIA-Project': this.config.project,
    };

    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    const response = await fetch(this.config.endpoint, {
      method: 'POST',
      headers,
      body: ndjson,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }
  }

  private sendBatchSync(batch: Partial<RAIAEvent>[]): void {
    if (!this.isBrowser || !navigator.sendBeacon) {
      console.warn('RAIA: sendBeacon not available, cannot send sync');
      return;
    }

    const ndjson = batch.map((e) => JSON.stringify(e)).join('\n');
    const blob = new Blob([ndjson], { type: 'application/x-ndjson' });

    // sendBeacon has limited header support, so we append tenant/project to URL
    const url = new URL(this.config.endpoint);
    url.searchParams.set('tenant', this.config.tenant);
    url.searchParams.set('project', this.config.project);

    const success = navigator.sendBeacon(url.toString(), blob);
    if (success) {
      this.batchesSent++;
    } else {
      this.batchesFailed++;
    }
  }

  private generateUUID(): string {
    // Simple UUID v4 generator
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
