import type { APIRoute } from 'astro';
import { rateLimited } from '../../lib/rate-limit';

export const prerender = false;

const json = (data: object, status = 200, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  });

export const POST: APIRoute = async ({ request, clientAddress }) => {
  if (rateLimited(`contact:${clientAddress}`, 5, 10 * 60 * 1000)) {
    return json({ ok: false, error: 'Zu viele Anfragen' }, 429, { 'Retry-After': '600' });
  }

  let body: Record<string, string>;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ ok: false, error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Honeypot: bots fill hidden fields, real users don't
  if (body.website) {
    return new Response(JSON.stringify({ ok: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const { name, email, message } = body;
  const tooLong = [name, email, message, body.company, body.phone].some(
    (v) => typeof v === 'string' && v.length > (v === message ? 5000 : 300)
  );
  if (tooLong) {
    return json({ ok: false, error: 'Eingabe zu lang' }, 422);
  }
  if (!name?.trim() || !email?.trim() || !message?.trim()) {
    return new Response(JSON.stringify({ ok: false, error: 'Pflichtfelder fehlen' }), {
      status: 422,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const webhook = import.meta.env.N8N_CONTACT_WEBHOOK;
  if (!webhook) {
    console.error('N8N_CONTACT_WEBHOOK is not set');
    return new Response(JSON.stringify({ ok: false, error: 'Konfigurationsfehler' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const res = await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, message, company: body.company, phone: body.phone }),
    });

    if (!res.ok) {
      throw new Error(`n8n returned ${res.status}`);
    }

    return new Response(JSON.stringify({ ok: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    console.error('Contact form forward failed:', err);
    return new Response(JSON.stringify({ ok: false, error: 'Serverfehler' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
