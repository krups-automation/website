import { createClient } from '@sanity/client';

const SANITY_PROJECT_ID = '8075qdie';
const SANITY_DATASET = 'production';

const token = import.meta.env.SANITY_API_READ_TOKEN;

export const draftClient = createClient({
  projectId: SANITY_PROJECT_ID,
  dataset: SANITY_DATASET,
  apiVersion: '2024-01-01',
  token,
  useCdn: false,
  perspective: 'drafts',
});

export function hasDraftToken(): boolean {
  return Boolean(token);
}
