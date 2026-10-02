import { createHmac, timingSafeEqual } from 'node:crypto';

export const DRAFT_COOKIE = 'krups-draft';
export const DRAFT_TTL_SECONDS = 60 * 60;

function sign(expiry: string, secret: string): string {
  return createHmac('sha256', secret).update(expiry).digest('hex');
}

/** Cookie value `<expiry-unix>.<hmac>` so the cookie cannot be forged without the preview secret. */
export function createDraftToken(secret: string): string {
  const expiry = String(Math.floor(Date.now() / 1000) + DRAFT_TTL_SECONDS);
  return `${expiry}.${sign(expiry, secret)}`;
}

export function verifyDraftToken(token: string | undefined, secret: string | undefined): boolean {
  if (!token || !secret) return false;
  const [expiry, mac] = token.split('.');
  if (!expiry || !mac || Number(expiry) < Date.now() / 1000) return false;
  const expected = Buffer.from(sign(expiry, secret));
  const given = Buffer.from(mac);
  return expected.length === given.length && timingSafeEqual(expected, given);
}
