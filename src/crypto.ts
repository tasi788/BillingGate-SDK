import { pbkdf2Sync, randomBytes, createCipheriv } from 'crypto';

/**
 * Encrypt payload using AES-256-GCM with a key derived from PBKDF2.
 * Consistent with Python's cryptography.hazmat.primitives.ciphers.aead.AESGCM
 */
export function encryptPayload(payload: object, keyStr: string, salt: string | Buffer = 'billinggate_salt'): string {
    // 1. Derive Key using PBKDF2
    const key = pbkdf2Sync(
        keyStr,
        salt,
        100000,
        32,
        'sha256'
    );

    // 2. Encrypt using AES-256-GCM
    const iv = randomBytes(12);
    const cipher = createCipheriv('aes-256-gcm', key, iv);

    const data = JSON.stringify(payload);
    let ciphertext = cipher.update(data, 'utf8');
    ciphertext = Buffer.concat([ciphertext, cipher.final()]);
    const authTag = cipher.getAuthTag();

    // Combine ciphertext and authTag to match Python's AESGCM behavior
    const finalCiphertext = Buffer.concat([ciphertext, authTag]);

    // 3. Combine IV + Ciphertext
    const combined = Buffer.concat([iv, finalCiphertext]);

    // 4. Base64Url Encode
    return combined.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}
