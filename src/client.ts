import { PaymentPayload, PaymentResponse } from './types';
import { encryptPayload } from './crypto';

export interface BillingGateClientOptions {
    workerUrl?: string;
    encryptionKey?: string;
    apiKey?: string;
    salt?: string;
}

export class BillingGateClient {
    private workerUrl?: string;
    private encryptionKey?: string;
    private apiKey?: string;
    private salt: string;

    constructor(options: BillingGateClientOptions = {}) {
        this.workerUrl = options.workerUrl || process.env.BILLINGGATE_WORKER_URL;
        this.encryptionKey = options.encryptionKey || process.env.BILLINGGATE_ENCRYPTION_KEY;
        this.apiKey = options.apiKey || process.env.BILLINGGATE_API_KEY;
        this.salt = options.salt || 'billinggate_salt';

        if (this.workerUrl) {
            this.workerUrl = this.workerUrl.replace(/\/+$/, '');
        }
    }

    /**
     * Method 1: Generate an encrypted URL for redirect flow.
     */
    generateRedirectUrl(payload: PaymentPayload): string {
        if (!this.encryptionKey) {
            throw new Error("Encryption Key is required for Redirect Flow");
        }
        if (!this.workerUrl) {
            throw new Error("Worker URL is required for Redirect Flow");
        }

        const token = encryptPayload(payload, this.encryptionKey, this.salt);
        return `${this.workerUrl}/${token}`;
    }

    /**
     * Method 2: Create payment request via API.
     */
    async createPaymentApi(payload: PaymentPayload): Promise<PaymentResponse> {
        if (!this.apiKey) {
            throw new Error("API Key is required for API Flow");
        }
        if (!this.workerUrl) {
            throw new Error("Worker URL is required for API Flow");
        }

        const response = await fetch(`${this.workerUrl}/api/payment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(`API Error: ${text}`);
        }

        const data = await response.json() as PaymentResponse;
        return data;
    }

    /**
     * Verify the status of a transaction.
     * Returns True if the transaction is valid/paid, False otherwise.
     */
    async verifyTransaction(transactionId: string): Promise<boolean> {
        if (!this.apiKey) {
            throw new Error("API Key is required for Verification");
        }
        if (!this.workerUrl) {
            throw new Error("Worker URL is required for Verification");
        }

        const url = new URL(`${this.workerUrl}/api/verify`);
        url.searchParams.append('transaction', transactionId);

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`
            }
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Verification Check Failed: ${text}`);
        }

        const data = await response.json();
        return Boolean(data);
    }
}
