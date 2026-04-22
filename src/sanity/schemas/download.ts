import { defineType, defineField } from 'sanity';

export const download = defineType({
  name: 'download',
  title: 'Download',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: { source: 'title', maxLength: 96 },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'file',
      title: 'File',
      type: 'file',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'fileType',
      title: 'File type',
      type: 'string',
      options: {
        list: [
          { title: 'PDF', value: 'pdf' },
          { title: 'STEP', value: 'step' },
          { title: 'DXF', value: 'dxf' },
          { title: 'ZIP', value: 'zip' },
          { title: 'Other', value: 'other' },
        ],
        layout: 'radio',
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'language',
      title: 'Language',
      type: 'string',
      options: {
        list: [
          { title: 'Deutsch', value: 'de' },
          { title: 'English', value: 'en' },
          { title: 'Français', value: 'fr' },
          { title: 'Multilingual', value: 'multilingual' },
        ],
        layout: 'radio',
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 3,
    }),
    defineField({
      name: 'gated',
      title: 'Gated (requires lead form)',
      type: 'boolean',
      initialValue: false,
    }),
    defineField({
      name: 'relatedProducts',
      title: 'Related products',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'product' }] }],
    }),
    defineField({
      name: 'relatedIndustries',
      title: 'Related industries',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'industry' }] }],
    }),
  ],
  preview: {
    select: {
      title: 'title',
      fileType: 'fileType',
      language: 'language',
      gated: 'gated',
    },
    prepare({ title, fileType, language, gated }) {
      const parts = [fileType?.toUpperCase(), language?.toUpperCase()].filter(Boolean);
      if (gated) parts.push('gated');
      return { title, subtitle: parts.join(' · ') };
    },
  },
});
