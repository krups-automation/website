import { defineConfig, type SanityClient } from 'sanity';
import { structureTool } from 'sanity/structure';
import { visionTool } from '@sanity/vision';
import { documentInternationalization } from '@sanity/document-internationalization';
import { sanityClient } from 'sanity:client';
import { createPreviewSecret } from '@sanity/preview-url-secret/create-secret';
import { urlSearchParamPreviewSecret } from '@sanity/preview-url-secret/constants';
import { schemaTypes } from './src/sanity/schemas';
import { deskStructure } from './src/sanity/structure';

const { projectId, dataset } = sanityClient.config();

// productionUrl re-runs on every document change, so reuse one secret instead of writing a
// new document each time. Refresh well inside the 1 h TTL so a resolved URL stays valid.
const SECRET_REUSE_MS = 30 * 60 * 1000;
let cachedSecret: { secret: Promise<string>; refreshAt: number } | undefined;

function previewSecret(client: SanityClient, origin: string, userId?: string): Promise<string> {
  if (!cachedSecret || Date.now() > cachedSecret.refreshAt) {
    const secret = createPreviewSecret(client, 'krups-website', `${origin}/admin`, userId).then(
      (result) => result.secret,
    );
    cachedSecret = { secret, refreshAt: Date.now() + SECRET_REUSE_MS };
    secret.catch(() => {
      cachedSecret = undefined;
    });
  }
  return cachedSecret.secret;
}

export default defineConfig({
  name: 'krups-website',
  title: 'KRUPS Website',
  projectId: projectId!,
  dataset: dataset!,
  basePath: '/admin',
  plugins: [
    structureTool({ structure: deskStructure }),
    // GROQ playground is a dev aid; keep it out of the production Studio
    ...(import.meta.env.DEV ? [visionTool()] : []),
    documentInternationalization({
      supportedLanguages: [
        { id: 'de', title: 'Deutsch' },
        { id: 'en', title: 'English' },
      ],
      schemaTypes: [
        'page',
        'siteSettings',
        'product',
        'productFamily',
        'download',
        'industry',
        'service',
        'caseStudy',
        'article',
      ],
    }),
  ],
  schema: {
    types: schemaTypes,
  },
  document: {
    productionUrl: async (prev, context) => {
      const { document } = context as unknown as {
        document: { _type?: string; slug?: { current?: string }; language?: string };
      };
      const PREVIEWABLE = new Set(['page', 'product', 'productFamily', 'industry', 'service']);
      if (!document._type || !PREVIEWABLE.has(document._type) || !document.slug?.current) {
        return prev;
      }
      const origin = typeof window !== 'undefined' ? window.location.origin : '';
      let secret: string;
      try {
        const client = context.getClient({ apiVersion: '2024-01-01' });
        secret = await previewSecret(client, origin, context.currentUser?.id);
      } catch {
        // A throw here takes down the document pane; users who can't write just get no preview
        return prev;
      }
      const params = new URLSearchParams({
        [urlSearchParamPreviewSecret]: secret,
        type: document._type,
        slug: document.slug.current,
        lang: document.language ?? 'de',
      });
      return `${origin}/api/preview?${params.toString()}`;
    },
  },
});
