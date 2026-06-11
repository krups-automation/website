import { defineType, defineField } from 'sanity';

export const page = defineType({
  name: 'page',
  title: 'Page',
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
      name: 'metaDescription',
      title: 'Meta description',
      type: 'text',
      rows: 2,
    }),
    defineField({
      name: 'body',
      title: 'Body',
      type: 'blockContent',
    }),
  ],
  preview: {
    select: { title: 'title', slug: 'slug.current', language: 'language' },
    prepare({ title, slug, language }: { title?: string; slug?: string; language?: string }) {
      const lang = language ? `[${language.toUpperCase()}]` : '';
      const path = slug ? `/${slug}` : '';
      return { title, subtitle: [lang, path].filter(Boolean).join(' ') };
    },
  },
});
