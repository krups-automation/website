import { sanityClient } from 'sanity:client';

export type Locale = 'de' | 'en';

export interface NavItem {
  label: string;
  href: string;
}

export interface SiteSettings {
  siteTitle: string;
  siteTagline?: string;
  primaryNav?: NavItem[];
  ctaLabel?: string;
  ctaHref?: string;
  footerCopyright?: string;
}

const SITE_SETTINGS_QUERY = `*[_type == "siteSettings" && language == $lang][0] {
  siteTitle,
  siteTagline,
  primaryNav,
  ctaLabel,
  ctaHref,
  footerCopyright
}`;

export async function getSiteSettings(lang: Locale): Promise<SiteSettings | null> {
  try {
    const result = await sanityClient.fetch<SiteSettings | null>(SITE_SETTINGS_QUERY, { lang });
    return result ?? null;
  } catch (err) {
    console.warn('[sanity] siteSettings fetch failed:', err);
    return null;
  }
}

export const SITE_SETTINGS_FALLBACK: Record<Locale, SiteSettings> = {
  de: {
    siteTitle: 'KRUPS Automation',
    siteTagline: 'Schienengeführte Fördersysteme für Präzisionsmontage.',
    primaryNav: [
      { label: 'Produkte', href: '/produkte' },
      { label: 'Branchen', href: '/branchen' },
      { label: 'Leistungen', href: '/leistungen' },
      { label: 'Ressourcen', href: '/ressourcen' },
      { label: 'Unternehmen', href: '/unternehmen' },
    ],
    ctaLabel: 'Projekt anfragen',
    ctaHref: '/kontakt',
    footerCopyright: '© 2026 KRUPS Automation GmbH · Hilden, Deutschland',
  },
  en: {
    siteTitle: 'KRUPS Automation',
    siteTagline: 'Rail-guided conveyor systems for precision assembly.',
    primaryNav: [
      { label: 'Products', href: '/en/products' },
      { label: 'Industries', href: '/en/industries' },
      { label: 'Services', href: '/en/services' },
      { label: 'Resources', href: '/en/resources' },
      { label: 'Company', href: '/en/company' },
    ],
    ctaLabel: 'Request a Project',
    ctaHref: '/en/contact',
    footerCopyright: '© 2026 KRUPS Automation GmbH · Hilden, Germany',
  },
};
