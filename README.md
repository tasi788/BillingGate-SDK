# BillingGate SDK

BillingGate SDK 提供 Python 與 TypeScript 雙語系支援，方便開發者與 BillingGate 支付閘道進行整合。本 SDK 支援「重導向支付 (Redirect Mode)」與「API 直接支付 (API Mode)」兩種流程，並提供交易驗證功能。

## 目錄 (Table of Contents)

- [TypeScript SDK](#typescript-sdk)
  - [安裝 (Installation)](#安裝-installation)
  - [初始化 (Initialization)](#初始化-initialization)
  - [使用方法 (Usage)](#使用方法-usage)
    - [1. 產生支付連結 (Redirect Mode)](#1-產生支付連結-redirect-mode)
    - [2. 建立 API 支付 (API Mode)](#2-建立-api-支付-api-mode)
    - [3. 驗證交易 (Verify Transaction)](#3-驗證交易-verify-transaction)
  - [型別定義 (Types)](#型別定義-types)
- [Python SDK](#python-sdk)
  - [安裝 (Installation)](#安裝-installation-1)
  - [使用方法 (Usage)](#使用方法-usage-1)
- [開發與貢獻 (Development)](#開發與貢獻-development)

---

## TypeScript SDK

專為 Node.js 環境設計 (Node 18+ 推薦)。

### 安裝 (Installation)

由於本 SDK 未上架至 npm，請使用 Git URL 安裝：

```bash
# 透過 HTTPS
npm install git+https://github.com/tasi788/BillingGate-SDK.git

# 或者透過 SSH (需設定金鑰)
npm install git+ssh://git@github.com/tasi788/BillingGate-SDK.git
```

### 初始化 (Initialization)

```typescript
import { BillingGateClient } from 'billinggate-sdk';

const client = new BillingGateClient({
    // 您的 Cloudflare Worker 網址 (必填)
    workerUrl: 'https://billing.example.com',
    
    // 加密金鑰 (Redirect Mode 必填) - 32-byte hex string
    encryptionKey: process.env.BILLINGGATE_ENCRYPTION_KEY,
    
    // API Key (API Mode 必填)
    apiKey: process.env.BILLINGGATE_API_KEY,
    
    // Salt (選填，需與 Server 端一致，預設為 'billinggate_salt')
    salt: 'your_salt' 
});
```

### 使用方法 (Usage)

#### 1. 產生支付連結 (Redirect Mode)

適用於不想在 Server 端處理複雜邏輯，直接將 User 引導至 BillingGate 頁面的場景。

```typescript
import { PaymentPayload } from 'billinggate-sdk';

const payload: PaymentPayload = {
    product_name: "VIP Membership",
    amount: 100, // 台幣金額
    source: "discord-bot",
    callback_url: "https://your-site.com/callback",
    // photo_url: "https://..." (選填)
    // query_path: "user_123" (選填，用於回傳識別)
};

const redirectUrl = client.generateRedirectUrl(payload);
console.log(redirectUrl); 
// Output: https://billing.example.com/EncryptedToken...
```

#### 2. 建立 API 支付 (API Mode)

適用於 Server-to-Server 溝通，直接取得支付連結與 ID。

```typescript
try {
    const response = await client.createPaymentApi(payload);
    console.log(`Payment ID: ${response.id}`);
    console.log(`Payment URL: ${response.url}`);
} catch (error) {
    console.error("建立支付失敗:", error);
}
```

#### 3. 驗證交易 (Verify Transaction)

驗證某筆交易是否已完成。

```typescript
const isPaid = await client.verifyTransaction("transaction_id_or_payment_id");

if (isPaid) {
    console.log("交易成功！");
} else {
    console.log("交易未完成或不存在。");
}
```

### 型別定義 (Types)

```typescript
interface PaymentPayload {
    product_name: string;
    amount: number;
    source: string;
    callback_url?: string;
    photo_url?: string;
    query_path?: string;
}

interface PaymentResponse {
    id: string;
    url: string;
}
```

---

## Python SDK

### 安裝 (Installation)

```bash
pip install git+https://github.com/tasi788/BillingGate-SDK.git
```
*(或使用 poetry/pdm 等工具)*

### 使用方法 (Usage)

```python
from billinggate_sdk.client import BillingGateClient, PaymentPayload

client = BillingGateClient(
    worker_url="https://billing.example.com",
    encryption_key="...",
    api_key="..."
)

# 1. Redirect Mode
payload = PaymentPayload(
    product_name="Test Product",
    amount=100,
    source="python-client"
)
url = client.generate_redirect_url(payload)

# 2. API Mode
# asyncContext needed
# response = await client.create_payment_api(payload)

# 3. Verify
# is_valid = await client.verify_transaction("tx_id")
```

---

## 開發與貢獻 (Development)

本專案為 Hybrid Repo，同時包含 Python 與 TypeScript 原始碼。

### TypeScript

位於根目錄 (主要設定於 `package.json`).

```bash
# 安裝依賴
npm install

# 編譯 (輸出至 dist/)
npm run build

# 執行測試
npx ts-node test/test_sdk.ts
```

### Python

位於 `src/billinggate_sdk` (設定於 `pyproject.toml`).

```bash
# 安裝依賴 (建議使用 venv)
pip install -e .

# 測試
pytest
```
