/**
 * Basic usage example for RAIA TypeScript SDK
 */

import { EventEmitter, EmitterConfig, Redactor, EventSigner, TransportType } from '@raia/sdk';

async function main() {
  // 1. Configure emitter
  const config: EmitterConfig = {
    tenant: 'acme-corp',
    project: 'customer-service',
    agent_id: 'support-agent-v1.0',
    region: 'us-east-1',
    deployment: 'prod',
    transport: TransportType.HTTP,
    endpoint: 'http://localhost:8000/ingest',
    apiKey: 'your-api-key-here',
    batchSize: 10,
    flushIntervalMs: 1000,
    enableSigning: true,
    hmacSecret: 'your-secret-key',
    llm: 'openai/gpt-4',
    seed: 42,
  };

  // 2. Create redactor and signer
  const redactor = Redactor.forDomain('general');
  const signer = new EventSigner('your-secret-key');

  // 3. Initialize emitter
  const emitter = new EventEmitter(config, redactor, signer);

  try {
    // Generate session IDs
    const sessionId = crypto.randomUUID();
    const runId = crypto.randomUUID();

    // Emit session_start event
    emitter.emit({
      event: 'session_start',
      session_id: sessionId,
      run_id: runId,
      agent_id: config.agent_id,
      user_id: 'user_12345',
      task: 'Customer asking about order status',
      domain: 'retail',
      constraints: ['professional_tone', 'no_personal_info_disclosure'],
      env: {} as any, // Will be enriched automatically
    });

    // Emit plan_created event
    emitter.emit({
      event: 'plan_created',
      session_id: sessionId,
      run_id: runId,
      agent_id: config.agent_id,
      plan: {
        steps: [
          { id: '1', description: 'Look up order by ID', tool: 'order_lookup' },
          { id: '2', description: 'Get shipping status', tool: 'shipping_status' },
          { id: '3', description: 'Format response for customer', tool: 'format_response' },
        ],
        rationale: 'Standard order status inquiry flow',
      },
      plan_depth: 3,
      revision_count: 0,
      env: {} as any,
    });

    // Emit tool_call event
    const toolEventId = crypto.randomUUID();
    emitter.emit({
      event: 'tool_call',
      event_id: toolEventId,
      session_id: sessionId,
      run_id: runId,
      agent_id: config.agent_id,
      tool_name: 'order_lookup',
      tool_args: { order_id: 'ORD-123456' },
      is_retry: false,
      retry_count: 0,
      env: {} as any,
    });

    // Emit observation event
    emitter.emit({
      event: 'observation',
      session_id: sessionId,
      run_id: runId,
      agent_id: config.agent_id,
      parent_event_id: toolEventId,
      observation: 'Order found: Status = Shipped, Expected delivery: 2025-01-20',
      success: true,
      grounded: true,
      evidence_refs: [
        { source: 'order_db', id: 'ORD-123456', relevance_score: 1.0 },
      ],
      latency_ms: 145.2,
      env: {} as any,
    });

    // Emit finalized event
    emitter.emit({
      event: 'finalized',
      session_id: sessionId,
      run_id: runId,
      agent_id: config.agent_id,
      final_answer: 'Your order ORD-123456 has been shipped and is expected to arrive on January 20th.',
      success: true,
      constraints_met: true,
      total_steps: 3,
      total_tool_calls: 2,
      latency_ms: 2345.6,
      env: {} as any,
    });

    console.log('Emitted events successfully');

    // Flush immediately
    await emitter.flush();
    console.log('Flushed all events');

    // Check health
    const health = emitter.getHealth();
    console.log('Health status:', health);

  } finally {
    // Graceful shutdown
    await emitter.shutdown(10000);
    console.log('Emitter shutdown complete');
  }
}

// Run in browser or Node.js
if (typeof window === 'undefined') {
  // Node.js
  main().catch(console.error);
} else {
  // Browser
  window.addEventListener('DOMContentLoaded', () => {
    main().catch(console.error);
  });
}
