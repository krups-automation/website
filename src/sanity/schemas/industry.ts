import { defineType, defineField } from 'sanity';

export const industry = defineType({
  name: 'industry',
  title: 'Industry',
  type: 'document',
  groups: [
    { name: 'meta', title: 'Meta' },
    { name: 'hero', title: 'Hero', default: true },
    { name: 'content', title: 'Content' },
    { name: 'solution', title: 'Solution' },
    { name: 'proof', title: 'Proof' },
    { name: 'cta', title: 'CTA' },
  ],
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      group: 'hero',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      group: 'meta',
      options: { source: 'name', maxLength: 96 },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'tagline',
      title: 'Tagline',
      type: 'string',
      group: 'hero',
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
      name: 'heroImage',
      title: 'Hero image',
      type: 'image',
      group: 'hero',
      options: { hotspot: true },
      fields: [
        { name: 'alt', type: 'string', title: 'Alt text' },
        { name: 'caption', type: 'string', title: 'Caption' },
      ],
    }),
    defineField({
      name: 'characterBar',
      title: 'Character bar (3-4 key stats)',
      type: 'array',
      group: 'hero',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'label', type: 'string', title: 'Label' },
            { name: 'value', type: 'string', title: 'Value' },
          ],
          preview: { select: { title: 'value', subtitle: 'label' } },
        },
      ],
      validation: (rule) => rule.max(4),
    }),
    defineField({
      name: 'whatMoves',
      title: 'What moves (materials, weights, cycles)',
      type: 'blockContent',
      group: 'content',
    }),
    defineField({
      name: 'bottleneck',
      title: 'Why a bottleneck today',
      type: 'blockContent',
      group: 'content',
    }),
    defineField({
      name: 'requirements',
      title: 'Requirements (core-6)',
      type: 'array',
      group: 'content',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'label', type: 'string', title: 'Label' },
            { name: 'value', type: 'string', title: 'Value' },
            { name: 'notes', type: 'string', title: 'Notes' },
          ],
          preview: {
            select: { title: 'label', subtitle: 'value' },
          },
        },
      ],
      validation: (rule) => rule.max(6),
    }),
    defineField({
      name: 'alternatives',
      title: 'Alternatives (external only)',
      type: 'blockContent',
      group: 'content',
    }),
    defineField({
      name: 'solutionRouting',
      title: 'Solution routing (how KRUPS solves it)',
      type: 'blockContent',
      group: 'solution',
    }),
    defineField({
      name: 'recommendedProducts',
      title: 'Recommended products',
      type: 'array',
      group: 'solution',
      of: [{ type: 'reference', to: [{ type: 'product' }] }],
    }),
    defineField({
      name: 'proof',
      title: 'Proof (case studies)',
      type: 'array',
      group: 'proof',
      of: [{ type: 'reference', to: [{ type: 'caseStudy' }] }],
    }),
    defineField({
      name: 'faq',
      title: 'FAQ',
      type: 'array',
      group: 'content',
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
      name: 'cta',
      title: 'Call to action',
      type: 'object',
      group: 'cta',
      fields: [
        { name: 'headline', type: 'string', title: 'Headline' },
        { name: 'description', type: 'text', title: 'Description', rows: 2 },
        { name: 'buttonLabel', type: 'string', title: 'Button label' },
        { name: 'buttonUrl', type: 'string', title: 'Button URL' },
      ],
    }),
  ],
  preview: {
    select: { title: 'name', subtitle: 'tagline', media: 'heroImage' },
  },
});
