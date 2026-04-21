import type { APIRoute } from 'astro';
import { draftClient, hasDraftToken } from '../../sanity/draft-client';
import { sanityClient } from 'sanity:client';

export const prerender = false;

export const GET: APIRoute = async ({ url }) => {
  const slug = url.searchParams.get('slug') ?? 'uber-krups';

  const results: Record<string, unknown> = {
    hasDraftToken: hasDraftToken(),
    slug,
  };

  try {
    results.publishedByType = await sanityClient.fetch(
      `*[_type == "page"]{_id, _type, title, language, "slug": slug.current}`
    );
  } catch (e) {
    results.publishedByTypeError = String(e);
  }

  try {
    results.draftsByType = await draftClient.fetch(
      `*[_type == "page"]{_id, _originalId, _type, title, language, "slug": slug.current}`
    );
  } catch (e) {
    results.draftsByTypeError = String(e);
  }

  try {
    results.draftBySlug = await draftClient.fetch(
      `*[_type == "page" && slug.current == $slug][0]`,
      { slug }
    );
  } catch (e) {
    results.draftBySlugError = String(e);
  }

  return new Response(JSON.stringify(results, null, 2), {
    headers: { 'content-type': 'application/json' },
  });
};
