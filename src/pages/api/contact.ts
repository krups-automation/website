import type { APIRoute } from 'astro';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
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
