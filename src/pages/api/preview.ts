import type { APIRoute } from 'astro';
import { validatePreviewUrl } from '@sanity/preview-url-secret';
import { DRAFT_COOKIE, DRAFT_TTL_SECONDS, createDraftToken } from '../../lib/preview-auth';
import { draftClient, hasDraftToken } from '../../sanity/draft-client';

export const prerender = false;

const SECRET = import.meta.env.SANITY_PREVIEW_SECRET;

const VALID_TYPES = new Set(['page', 'product', 'productFamily', 'industry', 'service']);

export const GET: APIRoute = async ({ request, cookies, redirect }) => {
  const url = new URL(request.url);
  const slug = url.searchParams.get('slug') ?? '';
  const lang = url.searchParams.get('lang') ?? 'de';
  const type = url.searchParams.get('type') ?? 'page';

  if (!SECRET || !hasDraftToken()) {
    return new Response('Invalid preview secret', { status: 401 });
  }

  // The URL carries a short-lived secret the Studio minted in the dataset, so nothing
  // long-lived has to reach the public Studio bundle.
  const { isValid } = await validatePreviewUrl(draftClient, request.url);
  if (!isValid) {
    return new Response('Invalid preview secret', { status: 401 });
  }

  if (!VALID_TYPES.has(type)) {
    return new Response('Invalid preview type', { status: 400 });
  }

  cookies.set(DRAFT_COOKIE, createDraftToken(SECRET), {
    path: '/',
    httpOnly: true,
    sameSite: 'lax',
    secure: import.meta.env.PROD,
    maxAge: DRAFT_TTL_SECONDS,
  });

  const prefix = lang === 'en' ? '/preview/en' : '/preview';
  return redirect(`${prefix}/${type}/${slug}`, 307);
};
