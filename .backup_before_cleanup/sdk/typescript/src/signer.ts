/**
 * HMAC-SHA256 Event Signer for TypeScript
 * Supports both browser (Web Crypto API) and Node.js (crypto module)
 */

export class EventSigner {
  private secret: string;
  private isBrowser: boolean;

  constructor(secret: string) {
    if (!secret) {
      throw new Error('HMAC secret cannot be empty');
    }
    this.secret = secret;
    this.isBrowser = typeof window !== 'undefined' && typeof window.crypto !== 'undefined';
  }

  /**
   * Generate HMAC signature for event.
   */
  async sign(event: any): Promise<string> {
    const canonical = this.canonicalize(event);

    if (this.isBrowser) {
      return this.signBrowser(canonical);
    } else {
      return this.signNode(canonical);
    }
  }

  /**
   * Synchronous signing (Node.js only).
   * In browser, use async sign() instead.
   */
  signSync(event: any): string {
    if (this.isBrowser) {
      throw new Error('Synchronous signing not supported in browser. Use async sign() instead.');
    }
    const canonical = this.canonicalize(event);
    return this.signNode(canonical);
  }

  /**
   * Verify event signature.
   */
  async verify(event: any, signature: string): Promise<boolean> {
    const expected = await this.sign(event);
    return this.constantTimeEqual(expected, signature);
  }

  private canonicalize(event: any): string {
    // Remove signature field and sort keys
    const eventCopy = { ...event };
    delete eventCopy._signature;

    return JSON.stringify(eventCopy, Object.keys(eventCopy).sort());
  }

  private async signBrowser(data: string): Promise<string> {
    const encoder = new TextEncoder();
    const keyData = encoder.encode(this.secret);
    const messageData = encoder.encode(data);

    const key = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );

    const signature = await crypto.subtle.sign('HMAC', key, messageData);

    // Convert ArrayBuffer to hex string
    return Array.from(new Uint8Array(signature))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }

  private signNode(data: string): string {
    // Dynamic import for Node.js crypto
    const crypto = require('crypto');
    const hmac = crypto.createHmac('sha256', this.secret);
    hmac.update(data);
    return hmac.digest('hex');
  }

  private constantTimeEqual(a: string, b: string): boolean {
    if (a.length !== b.length) {
      return false;
    }

    let result = 0;
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i);
    }

    return result === 0;
  }
}
