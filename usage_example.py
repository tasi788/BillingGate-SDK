
import asyncio
import os
from src.billinggate_sdk import BillingGateClient, PaymentPayload

# Assuming environment variables are set:
# export BILLINGGATE_WORKER_URL=""
# export BILLINGGATE_ENCRYPTION_KEY="..."
# export BILLINGGATE_API_KEY="..."

async def main():
    # Initialize Client (automatically reads env vars)
    client = BillingGateClient() 

    # Shared Payload
    payload = PaymentPayload(
        product_name="SDK Test Product",
        amount=600,
        source="PythonSDK_Example",
        callback_url="https://example.com/callback"
    )

    # Method 1: URL Redirect
    try:
        url = client.generate_redirect_url(payload)
        print(f"--- Method 1: Redirect URL ---\n{url}")
    except ValueError as e:
        print(f"Skipping Method 1: {e}")

    # Method 2: API Request
    try:
        response = await client.create_payment_api(payload)
        print(f"\n--- Method 2: API Response ---")
        print(f"ID: {response.id}")
        print(f"URL: {response.url}")
    except Exception as e:
        print(f"\nSkipping Method 2: {e}")

if __name__ == "__main__":
    # For demo purposes, you can manually set env here if not set in shell
    # os.environ["BILLINGGATE_WORKER_URL"] = ""
    # os.environ["BILLINGGATE_ENCRYPTION_KEY"] = "..."
    # os.environ["BILLINGGATE_API_KEY"] = "..."
    
    asyncio.run(main())
