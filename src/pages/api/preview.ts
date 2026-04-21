import type { APIRoute } from 'astro';

export const prerender = false;

const SECRET = import.meta.env.SANITY_PREVIEW_SECRET;
const DRAFT_COOKIE = 'krups-draft';

export const GET: APIRoute = async ({ request, cookies, redirect }) => {
  const url = new URL(request.url);
  const secret = url.searchParams.get('secret');
  const slug = url.searchParams.get('slug') ?? '';
  const lang = url.searchParams.get('lang') ?? 'de';

  if (!SECRET || secret !== SECRET) {
    return new Response('Invalid preview secret', { status: 401 });
  }

  cookies.set(DRAFT_COOKIE, '1', {
    path: '/',
    httpOnly: true,
    sameSite: 'lax',
    secure: import.meta.env.PROD,
    maxAge: 60 * 60, // 1 hour
  });

  const target = lang === 'en' ? `/preview/en/${slug}` : `/preview/${slug}`;
  return redirect(target, 307);
};
