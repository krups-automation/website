import type { APIRoute } from 'astro';
import {
  getAllProducts,
  getAllProductFamilies,
  getAllIndustrySlugs,
  getAllServiceSlugs,
  getAllPageSlugs,
} from '../sanity/queries';
import { CANONICAL_URL } from '../lib/schema-org';

export const prerender = false;

function urlEntry(
  path: string,
  priority: string,
  changefreq: string,
  alternatePath?: string
): string {
  const loc = `${CANONICAL_URL}${path}`;
  const altLoc = alternatePath ? `${CANONICAL_URL}${alternatePath}` : null;

  const hreflang = altLoc
    ? `    <xhtml:link rel="alternate" hreflang="de" href="${loc}"/>
    <xhtml:link rel="alternate" hreflang="en" href="${altLoc}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${loc}"/>
`
    : '';

  return `  <url>
    <loc>${loc}</loc>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
${hreflang}  </url>`;
}

function enOnlyEntry(path: string, priority: string, changefreq: string): string {
  const loc = `${CANONICAL_URL}${path}`;
  return `  <url>
    <loc>${loc}</loc>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`;
}

export const GET: APIRoute = async () => {
  const [products, families, industries, services, dePages, enPages] = await Promise.all([
    getAllProducts('de'),
    getAllProductFamilies('de'),
    getAllIndustrySlugs('de'),
    getAllServiceSlugs('de'),
    getAllPageSlugs('de'),
    getAllPageSlugs('en'),
  ]);

  const enPageSlugs = new Set(enPages.map((p) => p.slug));

  const staticUrls = [
    urlEntry('/', '1.0', 'weekly', '/en/'),
    urlEntry('/produkte', '0.9', 'weekly'),
    urlEntry('/leistungen', '0.8', 'weekly'),
    urlEntry('/branchen', '0.8', 'weekly'),
    urlEntry('/planung', '0.7', 'monthly'),
    urlEntry('/unternehmen', '0.6', 'monthly'),
    urlEntry('/kontakt', '0.7', 'monthly'),
  ];

  const familyUrls = families
    .filter((f) => f.slug?.current)
    .map((f) => urlEntry(`/produkte/${f.slug.current}`, '0.85', 'weekly'));

  const productUrls = products
    .filter((p) => p.slug?.current && p.productFamily?.slug?.current)
    .map((p) =>
      urlEntry(
        `/produkte/${p.productFamily!.slug!.current}/${p.slug.current}`,
        '0.8',
        'monthly'
      )
    );

  const industryUrls = industries
    .filter((i) => i.slug)
    .map((i) => urlEntry(`/branchen/${i.slug}`, '0.75', 'monthly'));

  const serviceUrls = services
    .filter((s) => s.slug)
    .map((s) => urlEntry(`/leistungen/${s.slug}`, '0.7', 'monthly'));

  // Generic CMS pages: pair DE+EN by slug if both exist, otherwise include each standalone
  const pairedDeSlugs = new Set<string>();
  const genericPageUrls: string[] = [];

  for (const { slug } of dePages) {
    if (enPageSlugs.has(slug)) {
      genericPageUrls.push(urlEntry(`/${slug}`, '0.6', 'monthly', `/en/${slug}`));
      pairedDeSlugs.add(slug);
    } else {
      genericPageUrls.push(urlEntry(`/${slug}`, '0.6', 'monthly'));
    }
  }

  // EN-only pages that have no DE counterpart
  for (const { slug } of enPages) {
    if (!pairedDeSlugs.has(slug)) {
      genericPageUrls.push(enOnlyEntry(`/en/${slug}`, '0.6', 'monthly'));
    }
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${[...staticUrls, ...familyUrls, ...productUrls, ...industryUrls, ...serviceUrls, ...genericPageUrls].join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=86400',
    },
  });
};
