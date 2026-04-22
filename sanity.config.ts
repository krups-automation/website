import { defineConfig } from 'sanity';
import { structureTool } from 'sanity/structure';
import { visionTool } from '@sanity/vision';
import { documentInternationalization } from '@sanity/document-internationalization';
import { sanityClient } from 'sanity:client';
import { schemaTypes } from './src/sanity/schemas';
import { deskStructure } from './src/sanity/structure';

const { projectId, dataset } = sanityClient.config();

export default defineConfig({
  name: 'krups-website',
  title: 'KRUPS Website',
  projectId: projectId!,
  dataset: dataset!,
  basePath: '/admin',
  plugins: [
    structureTool({ structure: deskStructure }),
    visionTool(),
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
      const { document } = context as {
        document: { _type?: string; slug?: { current?: string }; language?: string };
      };
      const secret = import.meta.env.PUBLIC_PREVIEW_SECRET;
      if (!secret || document._type !== 'page' || !document.slug?.current) {
        return prev;
      }
      const origin = typeof window !== 'undefined' ? window.location.origin : '';
      const params = new URLSearchParams({
        secret,
        slug: document.slug.current,
        lang: document.language ?? 'de',
      });
      return `${origin}/api/preview?${params.toString()}`;
    },
  },
});
