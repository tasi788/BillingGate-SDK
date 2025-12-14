export interface PaymentPayload {
    product_name: string;
    /** Amount in TWD */
    amount: number;
    source: string;
    callback_url?: string;
    photo_url?: string;
    query_path?: string;
}

export interface PaymentResponse {
    id: string;
    url: string;
}
