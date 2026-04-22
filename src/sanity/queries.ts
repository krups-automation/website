import { sanityClient } from 'sanity:client';
import { draftClient } from './draft-client';

function pickClient(draft = false) {
  return draft ? draftClient : sanityClient;
}

async function safeFetch<T>(
  client: ReturnType<typeof pickClient>,
  query: string,
  params: Record<string, unknown>,
  fallback: T
): Promise<T> {
  try {
    return (await client.fetch<T>(query, params)) ?? fallback;
  } catch (err) {
    console.warn('[sanity] fetch failed:', err);
    return fallback;
  }
}

export type Locale = 'de' | 'en';

// ---------------------------------------------------------------------------
// Shared types
// ---------------------------------------------------------------------------

export interface SanityImage {
  _type: 'image';
  asset?: { _ref: string };
  alt?: string;
  caption?: string;
}

export interface NavItem {
  label: string;
  href: string;
}

export interface FAQ {
  question: string;
  answer: string;
}

export interface SpecRow {
  label: string;
  value?: string;
  unit?: string;
  notes?: string;
}

export interface KeyFeature {
  title: string;
  description?: string;
}

// ---------------------------------------------------------------------------
// Site settings
// ---------------------------------------------------------------------------

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
  return safeFetch(sanityClient, SITE_SETTINGS_QUERY, { lang }, null);
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export interface PageDoc {
  _id: string;
  title: string;
  slug: { current: string };
  metaDescription?: string;
  body?: unknown[];
  language: Locale;
}

export async function getAllPageSlugs(lang: Locale) {
  return safeFetch<Array<{ slug: string }>>(
    sanityClient,
    `*[_type == "page" && language == $lang && defined(slug.current)] { "slug": slug.current }`,
    { lang },
    []
  );
}

export async function getPageBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<PageDoc | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "page" && language == $lang && slug.current == $slug][0]`,
    { slug, lang },
    null
  );
}

// ---------------------------------------------------------------------------
// Products + product families + downloads
// ---------------------------------------------------------------------------

export interface ProductFamily {
  _id: string;
  name: string;
  slug: { current: string };
  tagline?: string;
  metaTitle?: string;
  metaDescription?: string;
  heroImage?: SanityImage;
  intro?: unknown[];
  keyFeatures?: KeyFeature[];
  body?: unknown[];
}

export interface Product {
  _id: string;
  name: string;
  slug: { current: string };
  productFamily?: { _ref: string; name?: string; slug?: { current: string } };
  tagline?: string;
  metaTitle?: string;
  metaDescription?: string;
  heroImage?: SanityImage;
  intro?: unknown[];
  specs?: SpecRow[];
  keyFeatures?: KeyFeature[];
  useCases?: Array<{ _ref: string; name?: string; slug?: { current: string } }>;
  technicalDrawings?: SanityImage[];
  faq?: FAQ[];
  downloads?: Array<{ _ref: string }>;
  body?: unknown[];
}

export interface Download {
  _id: string;
  title: string;
  slug: { current: string };
  fileType: 'pdf' | 'step' | 'dxf' | 'zip' | 'other';
  language: 'de' | 'en' | 'fr' | 'multilingual';
  description?: string;
  gated?: boolean;
  file?: { asset?: { _ref: string; url?: string } };
}

const PRODUCT_PROJECTION = `{
  _id, name, slug, tagline, metaTitle, metaDescription, heroImage,
  intro, specs, keyFeatures, technicalDrawings, faq, body,
  "productFamily": productFamily->{_id, name, slug},
  "useCases": useCases[]->{_id, name, slug},
  "downloads": downloads[]->{_id, title, slug, fileType, language, description, gated, file}
}`;

export async function getAllProductSlugs(lang: Locale) {
  return safeFetch<Array<{ slug: string }>>(
    sanityClient,
    `*[_type == "product" && language == $lang && defined(slug.current)] { "slug": slug.current }`,
    { lang },
    []
  );
}

export async function getAllProducts(lang: Locale, opts: { draft?: boolean } = {}) {
  return safeFetch<Product[]>(
    pickClient(opts.draft),
    `*[_type == "product" && language == $lang] | order(name asc) ${PRODUCT_PROJECTION}`,
    { lang },
    []
  );
}

export async function getProductBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<Product | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "product" && language == $lang && slug.current == $slug][0] ${PRODUCT_PROJECTION}`,
    { slug, lang },
    null
  );
}

export async function getAllProductFamilies(lang: Locale, opts: { draft?: boolean } = {}) {
  return safeFetch<ProductFamily[]>(
    pickClient(opts.draft),
    `*[_type == "productFamily" && language == $lang] | order(name asc) {
      _id, name, slug, tagline, metaTitle, metaDescription, heroImage, intro, keyFeatures, body
    }`,
    { lang },
    []
  );
}

export async function getProductFamilyBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<(ProductFamily & { members: Product[] }) | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "productFamily" && language == $lang && slug.current == $slug][0] {
      _id, name, slug, tagline, metaTitle, metaDescription, heroImage, intro, keyFeatures, body,
      "members": members[]->{_id, name, slug, tagline, heroImage}
    }`,
    { slug, lang },
    null
  );
}

// ---------------------------------------------------------------------------
// Industries
// ---------------------------------------------------------------------------

export interface Industry {
  _id: string;
  name: string;
  slug: { current: string };
  tagline?: string;
  metaTitle?: string;
  metaDescription?: string;
  heroImage?: SanityImage;
  characterBar?: Array<{ label: string; value: string }>;
  whatMoves?: unknown[];
  bottleneck?: unknown[];
  requirements?: Array<{ label: string; value?: string; notes?: string }>;
  alternatives?: unknown[];
  solutionRouting?: unknown[];
  recommendedProducts?: Product[];
  proof?: Array<{ _ref: string }>;
  faq?: FAQ[];
  cta?: {
    headline?: string;
    description?: string;
    buttonLabel?: string;
    buttonUrl?: string;
  };
}

const INDUSTRY_PROJECTION = `{
  _id, name, slug, tagline, metaTitle, metaDescription, heroImage,
  characterBar, whatMoves, bottleneck, requirements, alternatives, solutionRouting,
  faq, cta,
  "recommendedProducts": recommendedProducts[]->{_id, name, slug, tagline, heroImage},
  "proof": proof[]->{_id, title, slug, heroImage, anonymizedName, "customer": customer->{name, logo}}
}`;

export async function getAllIndustrySlugs(lang: Locale) {
  return safeFetch<Array<{ slug: string }>>(
    sanityClient,
    `*[_type == "industry" && language == $lang && defined(slug.current)] { "slug": slug.current }`,
    { lang },
    []
  );
}

export async function getAllIndustries(lang: Locale, opts: { draft?: boolean } = {}) {
  return safeFetch<Industry[]>(
    pickClient(opts.draft),
    `*[_type == "industry" && language == $lang] | order(name asc) ${INDUSTRY_PROJECTION}`,
    { lang },
    []
  );
}

export async function getIndustryBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<Industry | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "industry" && language == $lang && slug.current == $slug][0] ${INDUSTRY_PROJECTION}`,
    { slug, lang },
    null
  );
}

// ---------------------------------------------------------------------------
// Services
// ---------------------------------------------------------------------------

export interface Service {
  _id: string;
  name: string;
  slug: { current: string };
  metaTitle?: string;
  metaDescription?: string;
  summary?: string;
  heroImage?: SanityImage;
  processSteps?: Array<{ stepNumber?: number; title: string; description?: string }>;
  deliverables?: string[];
  body?: unknown[];
  faq?: FAQ[];
}

const SERVICE_PROJECTION = `{
  _id, name, slug, metaTitle, metaDescription, summary, heroImage,
  processSteps, deliverables, body, faq
}`;

export async function getAllServiceSlugs(lang: Locale) {
  return safeFetch<Array<{ slug: string }>>(
    sanityClient,
    `*[_type == "service" && language == $lang && defined(slug.current)] { "slug": slug.current }`,
    { lang },
    []
  );
}

export async function getAllServices(lang: Locale, opts: { draft?: boolean } = {}) {
  return safeFetch<Service[]>(
    pickClient(opts.draft),
    `*[_type == "service" && language == $lang] | order(name asc) ${SERVICE_PROJECTION}`,
    { lang },
    []
  );
}

export async function getServiceBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<Service | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "service" && language == $lang && slug.current == $slug][0] ${SERVICE_PROJECTION}`,
    { slug, lang },
    null
  );
}

// ---------------------------------------------------------------------------
// Customers + case studies
// ---------------------------------------------------------------------------

export interface Customer {
  _id: string;
  name: string;
  slug: { current: string };
  logo?: SanityImage;
  country?: string;
  publiclyReferenceable: boolean;
}

export interface CaseStudy {
  _id: string;
  title: string;
  slug: { current: string };
  metaTitle?: string;
  metaDescription?: string;
  customer?: Customer;
  anonymizedName?: string;
  industry?: { _id: string; name: string; slug: { current: string } };
  products?: Product[];
  publishedAt?: string;
  challenge?: unknown[];
  solution?: unknown[];
  results?: Array<{ metric: string; value?: string; unit?: string }>;
  heroImage?: SanityImage;
  gallery?: SanityImage[];
  body?: unknown[];
}

export async function getPublicCustomers() {
  return safeFetch<Customer[]>(
    sanityClient,
    `*[_type == "customer" && publiclyReferenceable == true] | order(name asc) {
      _id, name, slug, logo, country, publiclyReferenceable
    }`,
    {},
    []
  );
}

const CASE_STUDY_PROJECTION = `{
  _id, title, slug, metaTitle, metaDescription,
  anonymizedName, publishedAt, challenge, solution, results, heroImage, gallery, body,
  "customer": customer->{_id, name, slug, logo, country, publiclyReferenceable},
  "industry": industry->{_id, name, slug},
  "products": products[]->{_id, name, slug, tagline, heroImage}
}`;

export async function getAllCaseStudies(lang: Locale, opts: { draft?: boolean } = {}) {
  return safeFetch<CaseStudy[]>(
    pickClient(opts.draft),
    `*[_type == "caseStudy" && language == $lang] | order(publishedAt desc) ${CASE_STUDY_PROJECTION}`,
    { lang },
    []
  );
}

export async function getCaseStudyBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<CaseStudy | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "caseStudy" && language == $lang && slug.current == $slug][0] ${CASE_STUDY_PROJECTION}`,
    { slug, lang },
    null
  );
}

export async function getCaseStudiesByIndustry(
  industrySlug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
) {
  return safeFetch<CaseStudy[]>(
    pickClient(opts.draft),
    `*[_type == "caseStudy" && language == $lang && industry->slug.current == $industrySlug]
       | order(publishedAt desc) ${CASE_STUDY_PROJECTION}`,
    { industrySlug, lang },
    []
  );
}

// ---------------------------------------------------------------------------
// Articles
// ---------------------------------------------------------------------------

export interface Article {
  _id: string;
  title: string;
  slug: { current: string };
  metaTitle?: string;
  metaDescription?: string;
  summary?: string;
  heroImage?: SanityImage;
  author?: { _id: string; name: string; role?: string; photo?: SanityImage };
  publishedAt?: string;
  pillar?: { _id: string; name: string; slug: { current: string } };
  tags?: Array<{ _id: string; name: string; slug: { current: string } }>;
  body?: unknown[];
}

const ARTICLE_PROJECTION = `{
  _id, title, slug, metaTitle, metaDescription, summary, heroImage, publishedAt, body,
  "author": author->{_id, name, role, photo},
  "pillar": pillar->{_id, name, slug},
  "tags": tags[]->{_id, name, slug}
}`;

export async function getAllArticleSlugs(lang: Locale) {
  return safeFetch<Array<{ slug: string }>>(
    sanityClient,
    `*[_type == "article" && language == $lang && defined(slug.current)] { "slug": slug.current }`,
    { lang },
    []
  );
}

export async function getAllArticles(lang: Locale, opts: { draft?: boolean } = {}) {
  return safeFetch<Article[]>(
    pickClient(opts.draft),
    `*[_type == "article" && language == $lang] | order(publishedAt desc) ${ARTICLE_PROJECTION}`,
    { lang },
    []
  );
}

export async function getArticleBySlug(
  slug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
): Promise<Article | null> {
  return safeFetch(
    pickClient(opts.draft),
    `*[_type == "article" && language == $lang && slug.current == $slug][0] ${ARTICLE_PROJECTION}`,
    { slug, lang },
    null
  );
}

export async function getArticlesByPillar(
  pillarSlug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
) {
  return safeFetch<Article[]>(
    pickClient(opts.draft),
    `*[_type == "article" && language == $lang && pillar->slug.current == $pillarSlug]
       | order(publishedAt desc) ${ARTICLE_PROJECTION}`,
    { pillarSlug, lang },
    []
  );
}

export async function getArticlesByTag(
  tagSlug: string,
  lang: Locale,
  opts: { draft?: boolean } = {}
) {
  return safeFetch<Article[]>(
    pickClient(opts.draft),
    `*[_type == "article" && language == $lang && $tagSlug in tags[]->slug.current]
       | order(publishedAt desc) ${ARTICLE_PROJECTION}`,
    { tagSlug, lang },
    []
  );
}

// ---------------------------------------------------------------------------
// Fallback site settings (used when Sanity is unreachable or the doc is missing)
// ---------------------------------------------------------------------------

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
