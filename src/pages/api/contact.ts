import type { APIRoute } from 'astro';

export const prerender = false;

const N8N_WEBHOOK = 'http://46.225.88.11:5678/webhook/contact-form';

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

  const { name, email, message } = body;
  if (!name?.trim() || !email?.trim() || !message?.trim()) {
    return new Response(JSON.stringify({ ok: false, error: 'Pflichtfelder fehlen' }), {
      status: 422,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const res = await fetch(N8N_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
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
