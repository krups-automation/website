import { defineConfig } from 'sanity';
import { structureTool } from 'sanity/structure';
import { visionTool } from '@sanity/vision';
import { documentInternationalization } from '@sanity/document-internationalization';
import { sanityClient } from 'sanity:client';
import { schemaTypes } from './src/sanity/schemas';

const { projectId, dataset } = sanityClient.config();

export default defineConfig({
  name: 'krups-website',
  title: 'KRUPS Website',
  projectId: projectId!,
  dataset: dataset!,
  basePath: '/admin',
  plugins: [
    structureTool(),
    visionTool(),
    documentInternationalization({
      supportedLanguages: [
        { id: 'de', title: 'Deutsch' },
        { id: 'en', title: 'English' },
      ],
      schemaTypes: ['page', 'siteSettings'],
    }),
  ],
  schema: {
    types: schemaTypes,
  },
});
