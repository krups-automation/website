import type { APIRoute } from 'astro';

export const prerender = false;

const SECRET = import.meta.env.SANITY_PREVIEW_SECRET;
const DRAFT_COOKIE = 'krups-draft';

const VALID_TYPES = new Set(['page', 'product', 'productFamily', 'industry', 'service']);

export const GET: APIRoute = async ({ request, cookies, redirect }) => {
  const url = new URL(request.url);
  const secret = url.searchParams.get('secret');
  const slug = url.searchParams.get('slug') ?? '';
  const lang = url.searchParams.get('lang') ?? 'de';
  const type = url.searchParams.get('type') ?? 'page';

  if (!SECRET || secret !== SECRET) {
    return new Response('Invalid preview secret', { status: 401 });
  }

  if (!VALID_TYPES.has(type)) {
    return new Response('Invalid preview type', { status: 400 });
  }

  cookies.set(DRAFT_COOKIE, '1', {
    path: '/',
    httpOnly: true,
    sameSite: 'lax',
    secure: import.meta.env.PROD,
    maxAge: 60 * 60,
  });

  const prefix = lang === 'en' ? '/preview/en' : '/preview';
  return redirect(`${prefix}/${type}/${slug}`, 307);
};
