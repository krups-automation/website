import { defineType, defineField } from 'sanity';

export const product = defineType({
  name: 'product',
  title: 'Product',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: { source: 'name', maxLength: 96 },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'productFamily',
      title: 'Product family',
      type: 'reference',
      to: [{ type: 'productFamily' }],
    }),
    defineField({
      name: 'tagline',
      title: 'Tagline',
      type: 'string',
    }),
    defineField({
      name: 'metaTitle',
      title: 'Meta title',
      type: 'string',
    }),
    defineField({
      name: 'metaDescription',
      title: 'Meta description',
      type: 'text',
      rows: 2,
    }),
    defineField({
      name: 'heroImage',
      title: 'Hero image',
      type: 'image',
      options: { hotspot: true },
      fields: [
        { name: 'alt', type: 'string', title: 'Alt text' },
        { name: 'caption', type: 'string', title: 'Caption' },
      ],
    }),
    defineField({
      name: 'intro',
      title: 'Intro',
      type: 'blockContent',
    }),
    defineField({
      name: 'specs',
      title: 'Specifications',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'label', type: 'string', title: 'Label' },
            { name: 'value', type: 'string', title: 'Value' },
            { name: 'unit', type: 'string', title: 'Unit' },
            { name: 'notes', type: 'string', title: 'Notes' },
          ],
          preview: {
            select: { title: 'label', value: 'value', unit: 'unit' },
            prepare({ title, value, unit }) {
              return { title, subtitle: [value, unit].filter(Boolean).join(' ') };
            },
          },
        },
      ],
    }),
    defineField({
      name: 'keyFeatures',
      title: 'Key features',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'title', type: 'string', title: 'Title' },
            { name: 'description', type: 'text', title: 'Description', rows: 2 },
          ],
          preview: { select: { title: 'title', subtitle: 'description' } },
        },
      ],
    }),
    defineField({
      name: 'useCases',
      title: 'Use cases (industries)',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'industry' }] }],
    }),
    defineField({
      name: 'technicalDrawings',
      title: 'Technical drawings',
      type: 'array',
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
      name: 'faq',
      title: 'FAQ',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'question', type: 'string', title: 'Question' },
            { name: 'answer', type: 'text', title: 'Answer', rows: 3 },
          ],
          preview: { select: { title: 'question', subtitle: 'answer' } },
        },
      ],
    }),
    defineField({
      name: 'downloads',
      title: 'Downloads',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'download' }] }],
    }),
    defineField({
      name: 'relatedProducts',
      title: 'Related products',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'product' }] }],
    }),
    defineField({
      name: 'body',
      title: 'Body',
      type: 'blockContent',
    }),
  ],
  preview: {
    select: {
      title: 'name',
      subtitle: 'tagline',
      media: 'heroImage',
      family: 'productFamily.name',
    },
    prepare({ title, subtitle, media, family }) {
      return {
        title,
        subtitle: [family, subtitle].filter(Boolean).join(' · '),
        media,
      };
    },
  },
});
