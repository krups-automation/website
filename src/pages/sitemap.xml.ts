import type { APIRoute } from 'astro';
import {
  getAllProducts,
  getAllProductFamilies,
  getAllIndustrySlugs,
  getAllServiceSlugs,
} from '../sanity/queries';
import { CANONICAL_URL } from '../lib/schema-org';

export const prerender = false;

function url(path: string, priority: string, changefreq: string): string {
  return `  <url>
    <loc>${CANONICAL_URL}${path}</loc>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`;
}

export const GET: APIRoute = async () => {
  const [products, families, industries, services] = await Promise.all([
    getAllProducts('de'),
    getAllProductFamilies('de'),
    getAllIndustrySlugs('de'),
    getAllServiceSlugs('de'),
  ]);

  const staticUrls = [
    url('/', '1.0', 'weekly'),
    url('/produkte', '0.9', 'weekly'),
    url('/leistungen', '0.8', 'weekly'),
    url('/branchen', '0.8', 'weekly'),
    url('/planung', '0.7', 'monthly'),
    url('/unternehmen', '0.6', 'monthly'),
    url('/kontakt', '0.7', 'monthly'),
  ];

  const familyUrls = families
    .filter((f) => f.slug?.current)
    .map((f) => url(`/produkte/${f.slug.current}`, '0.85', 'weekly'));

  const productUrls = products
    .filter((p) => p.slug?.current && p.productFamily?.slug?.current)
    .map((p) =>
      url(
        `/produkte/${p.productFamily!.slug!.current}/${p.slug.current}`,
        '0.8',
        'monthly'
      )
    );

  const industryUrls = industries
    .filter((i) => i.slug)
    .map((i) => url(`/branchen/${i.slug}`, '0.75', 'monthly'));

  const serviceUrls = services
    .filter((s) => s.slug)
    .map((s) => url(`/leistungen/${s.slug}`, '0.7', 'monthly'));

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...staticUrls, ...familyUrls, ...productUrls, ...industryUrls, ...serviceUrls].join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=86400',
    },
  });
};
