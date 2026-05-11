import type { Locale } from '../sanity/queries';

const SITE_URL = 'https://krups-website.vercel.app';
const CANONICAL_DOMAIN = 'https://www.krups-automation.com';

/** The production domain the site will live on once migrated. Used as `@id` anchors so
 * structured data stays stable across preview deploys. */
export const CANONICAL_URL = CANONICAL_DOMAIN;

export function siteOrigin(): string {
  return SITE_URL;
}

export interface Crumb {
  label: string;
  href?: string;
}

export function organizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${CANONICAL_URL}/#organization`,
    name: 'KRUPS Automation',
    legalName: 'KRUPS Automation GmbH',
    url: CANONICAL_URL,
    logo: `${CANONICAL_URL}/favicon.svg`,
    description:
      'Rail-guided conveyor systems for precision automotive and industrial assembly — LOGO!MAT eCart and friction roller conveyors for 300–2.000 kg payloads.',
    foundingDate: '1983',
    address: {
      '@type': 'PostalAddress',
      streetAddress: 'Ringstr. 13',
      addressLocality: 'Dernbach',
      postalCode: '56307',
      addressCountry: 'DE',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'sales',
      telephone: '+49-2689-9435-0',
      email: 'info@krups-automation.com',
      areaServed: ['DE', 'US', 'CN', 'EU'],
      availableLanguage: ['German', 'English'],
    },
    sameAs: [
      'https://www.linkedin.com/company/krups-automation-gmbh/',
      'https://www.wikidata.org/wiki/Q139742524',
    ],
  };
}

export function websiteSchema(locale: Locale) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${CANONICAL_URL}/#website`,
    url: CANONICAL_URL,
    name: 'KRUPS Automation',
    inLanguage: locale,
    publisher: { '@id': `${CANONICAL_URL}/#organization` },
  };
}

export function breadcrumbSchema(crumbs: Crumb[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: crumbs.map((crumb, idx) => {
      const entry: Record<string, unknown> = {
        '@type': 'ListItem',
        position: idx + 1,
        name: crumb.label,
      };
      if (crumb.href) {
        entry.item = crumb.href.startsWith('http')
          ? crumb.href
          : `${CANONICAL_URL}${crumb.href}`;
      }
      return entry;
    }),
  };
}

export interface ProductSchemaInput {
  name: string;
  description?: string;
  url: string;
  category?: string;
  specs?: Array<{ label: string; value: string; unit?: string }>;
}

export function productSchema(input: ProductSchemaInput) {
  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: input.name,
    url: input.url.startsWith('http') ? input.url : `${CANONICAL_URL}${input.url}`,
    brand: { '@type': 'Brand', name: 'KRUPS Automation' },
    manufacturer: { '@id': `${CANONICAL_URL}/#organization` },
  };
  if (input.description) schema.description = input.description;
  if (input.category) schema.category = input.category;
  if (input.specs && input.specs.length > 0) {
    schema.additionalProperty = input.specs.map((s) => ({
      '@type': 'PropertyValue',
      name: s.label,
      value: s.unit ? `${s.value} ${s.unit}` : s.value,
    }));
  }
  return schema;
}

export interface ServiceSchemaInput {
  name: string;
  description?: string;
  url: string;
}

export function serviceSchema(input: ServiceSchemaInput) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: input.name,
    url: input.url.startsWith('http') ? input.url : `${CANONICAL_URL}${input.url}`,
    provider: { '@id': `${CANONICAL_URL}/#organization` },
    ...(input.description ? { description: input.description } : {}),
  };
}

export interface FAQ {
  question: string;
  answer: string;
}

export function faqSchema(items: FAQ[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  };
}
