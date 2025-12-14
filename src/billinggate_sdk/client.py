
import os
import json
import base64
import httpx
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class PaymentPayload(BaseModel):
    product_name: str
    amount: int = Field(..., description="Amount in TWD")
    source: str
    callback_url: Optional[str] = None
    photo_url: Optional[str] = None
    query_path: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    url: str

class BillingGateClient:
    def __init__(
        self, 
        worker_url: Optional[str] = None, 
        encryption_key: Optional[str] = None, 
        api_key: Optional[str] = None,
        salt: bytes = b"billinggate_salt"
    ):
        """
        Initialize the BillingGate Client.
        
        Args:
            worker_url: The URL of your BillingGate Worker (e.g. https://example.com).
                        Defaults to env 'BILLINGGATE_WORKER_URL'.
            encryption_key: 32-byte hex string key for encryption (Method 1).
                            Defaults to env 'BILLINGGATE_ENCRYPTION_KEY'.
            api_key: API Key for authentication (Method 2).
                     Defaults to env 'BILLINGGATE_API_KEY'.
            salt: Salt used for key derivation. Must match server.
        """
        self.worker_url = worker_url or os.getenv("BILLINGGATE_WORKER_URL")
        self.encryption_key = encryption_key or os.getenv("BILLINGGATE_ENCRYPTION_KEY")
        self.api_key = api_key or os.getenv("BILLINGGATE_API_KEY")
        self.salt = salt
        
        if self.worker_url:
            self.worker_url = self.worker_url.rstrip("/")

    def generate_redirect_url(self, payload: PaymentPayload) -> str:
        """
        Method 1: Generate an encrypted URL for redirect flow.
        """
        if not self.encryption_key:
            raise ValueError("Encryption Key is required for Redirect Flow")
        
        if not self.worker_url:
            raise ValueError("Worker URL is required for Redirect Flow")

        token = self._encrypt_payload(payload.model_dump(), self.encryption_key)
        return f"{self.worker_url}/{token}"

    async def create_payment_api(self, payload: PaymentPayload) -> PaymentResponse:
        """
        Method 2: Create payment request via API.
        """
        if not self.api_key:
            raise ValueError("API Key is required for API Flow")
            
        if not self.worker_url:
            raise ValueError("Worker URL is required for API Flow")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.worker_url}/api/payment",
                    json=payload.model_dump(),
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                data = response.json()
                return PaymentResponse(**data)
            except httpx.HTTPStatusError as e:
                raise Exception(f"API Error: {e.response.text}") from e
            except Exception as e:
                raise Exception(f"Payment Creation Failed: {e}") from e

    async def verify_transaction(self, transaction_id: str) -> bool:
        """
        Verify the status of a transaction.
        Returns True if the transaction is valid/paid, False otherwise.
        """
        if not self.api_key:
            raise ValueError("API Key is required for Verification")
            
        if not self.worker_url:
            raise ValueError("Worker URL is required for Verification")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.worker_url}/api/verify",
                    params={"transaction": transaction_id},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                # Assuming the API returns a boolean or "true"/"false" string
                data = response.json()
                return bool(data)
            except httpx.HTTPStatusError as e:
                # If 404/etc, consider it failed verification or handle differently?
                # For now, let's treat non-200 as an exception unless it's a "false" result logic
                # But requirement says "confirm returns false". 
                # If the API returns JSON "false", it's a 200 OK.
                raise Exception(f"Verification Check Failed: {e.response.text}") from e
            except Exception as e:
                raise Exception(f"Verification Error: {e}") from e

    def _encrypt_payload(self, payload: dict, key_str: str) -> str:
        # 1. Derive Key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = kdf.derive(key_str.encode('utf-8'))

        # 2. Encrypt using AES-256-GCM
        iv = os.urandom(12)
        aesgcm = AESGCM(key)
        
        data = json.dumps(payload).encode('utf-8')
        ciphertext = aesgcm.encrypt(iv, data, None)

        # 3. Combine IV + Ciphertext
        combined = iv + ciphertext

        # 4. Base64Url Encode
        return base64.urlsafe_b64encode(combined).decode('utf-8').rstrip("=")
