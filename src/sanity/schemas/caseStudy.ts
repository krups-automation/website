import { defineType, defineField } from 'sanity';

export const caseStudy = defineType({
  name: 'caseStudy',
  title: 'Case study',
  type: 'document',
  groups: [
    { name: 'meta', title: 'Meta' },
    { name: 'identity', title: 'Identity', default: true },
    { name: 'content', title: 'Content' },
    { name: 'proof', title: 'Results' },
    { name: 'media', title: 'Media' },
  ],
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      group: 'identity',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      group: 'meta',
      options: { source: 'title', maxLength: 96 },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'metaTitle',
      title: 'Meta title',
      type: 'string',
      group: 'meta',
    }),
    defineField({
      name: 'metaDescription',
      title: 'Meta description',
      type: 'text',
      rows: 2,
      group: 'meta',
    }),
    defineField({
      name: 'customer',
      title: 'Customer',
      description: 'Either a customer reference OR an anonymized name is required.',
      type: 'reference',
      group: 'identity',
      to: [{ type: 'customer' }],
    }),
    defineField({
      name: 'anonymizedName',
      title: 'Anonymized name',
      description:
        'Used when the customer cannot be named publicly (e.g. "German OEM, Bavaria"). Required if no customer reference is set.',
      type: 'string',
      group: 'identity',
    }),
    defineField({
      name: 'industry',
      title: 'Industry',
      type: 'reference',
      group: 'identity',
      to: [{ type: 'industry' }],
    }),
    defineField({
      name: 'products',
      title: 'Products used',
      type: 'array',
      group: 'identity',
      of: [{ type: 'reference', to: [{ type: 'product' }] }],
    }),
    defineField({
      name: 'publishedAt',
      title: 'Published at',
      type: 'datetime',
      group: 'meta',
    }),
    defineField({
      name: 'challenge',
      title: 'Challenge',
      type: 'blockContent',
      group: 'content',
    }),
    defineField({
      name: 'solution',
      title: 'Solution',
      type: 'blockContent',
      group: 'content',
    }),
    defineField({
      name: 'results',
      title: 'Results (metrics)',
      type: 'array',
      group: 'proof',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'metric', type: 'string', title: 'Metric' },
            { name: 'value', type: 'string', title: 'Value' },
            { name: 'unit', type: 'string', title: 'Unit' },
          ],
          preview: {
            select: { title: 'metric', value: 'value', unit: 'unit' },
            prepare({ title, value, unit }) {
              return { title, subtitle: [value, unit].filter(Boolean).join(' ') };
            },
          },
        },
      ],
    }),
    defineField({
      name: 'heroImage',
      title: 'Hero image',
      type: 'image',
      group: 'media',
      options: { hotspot: true },
      fields: [
        { name: 'alt', type: 'string', title: 'Alt text' },
        { name: 'caption', type: 'string', title: 'Caption' },
      ],
    }),
    defineField({
      name: 'gallery',
      title: 'Gallery',
      type: 'array',
      group: 'media',
      of: [
        {
          type: 'image',
          options: { hotspot: true },
          fields: [
            { name: 'alt', type: 'string', title: 'Alt text' },
            { name: 'caption', type: 'string', title: 'Caption' },
          ],
        },
      ],
    }),
    defineField({
      name: 'body',
      title: 'Body',
      type: 'blockContent',
      group: 'content',
    }),
  ],
  validation: (rule) =>
    rule.custom((doc) => {
      if (!doc) return true;
      const d = doc as { customer?: unknown; anonymizedName?: string };
      const hasCustomer = Boolean(d.customer);
      const hasAnon = Boolean(d.anonymizedName && d.anonymizedName.trim());
      if (!hasCustomer && !hasAnon) {
        return 'Either a customer reference or an anonymized name is required.';
      }
      return true;
    }),
  preview: {
    select: {
      title: 'title',
      customer: 'customer.name',
      anon: 'anonymizedName',
      media: 'heroImage',
    },
    prepare({ title, customer, anon, media }) {
      return {
        title,
        subtitle: customer || anon || '(no customer)',
        media,
      };
    },
  },
});
