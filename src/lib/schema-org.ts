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
  href: string;
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
    foundingDate: '1985',
    address: {
      '@type': 'PostalAddress',
      streetAddress: 'Im Hülsenfeld 10',
      addressLocality: 'Hilden',
      postalCode: '40721',
      addressCountry: 'DE',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'sales',
      telephone: '+49 2103 2507-0',
      email: 'info@krups-automation.com',
      areaServed: ['DE', 'US', 'CN', 'EU'],
      availableLanguage: ['German', 'English'],
    },
    sameAs: [
      'https://www.linkedin.com/company/krups-automation-gmbh/',
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
    itemListElement: crumbs.map((crumb, idx) => ({
      '@type': 'ListItem',
      position: idx + 1,
      name: crumb.label,
      item: crumb.href.startsWith('http') ? crumb.href : `${CANONICAL_URL}${crumb.href}`,
    })),
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
