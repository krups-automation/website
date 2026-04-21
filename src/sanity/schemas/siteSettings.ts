import { defineType, defineField } from 'sanity';

export const siteSettings = defineType({
  name: 'siteSettings',
  title: 'Site Settings',
  type: 'document',
  // Singleton — only one instance per locale
  __experimental_formPreviewTitle: false,
  fields: [
    defineField({
      name: 'siteTitle',
      title: 'Site title',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'siteTagline',
      title: 'Site tagline',
      type: 'string',
      description: 'Short positioning line, used in meta descriptions and hero fallbacks',
    }),
    defineField({
      name: 'primaryNav',
      title: 'Primary navigation',
      type: 'array',
      of: [
        {
          type: 'object',
          name: 'navItem',
          title: 'Nav item',
          fields: [
            { name: 'label', type: 'string', title: 'Label', validation: (r) => r.required() },
            { name: 'href', type: 'string', title: 'Href (path)', validation: (r) => r.required() },
          ],
          preview: {
            select: { title: 'label', subtitle: 'href' },
          },
        },
      ],
    }),
    defineField({
      name: 'ctaLabel',
      title: 'Header CTA label',
      type: 'string',
    }),
    defineField({
      name: 'ctaHref',
      title: 'Header CTA href',
      type: 'string',
    }),
    defineField({
      name: 'footerCopyright',
      title: 'Footer copyright line',
      type: 'string',
    }),
  ],
  preview: {
    select: { title: 'siteTitle' },
    prepare({ title }) {
      return { title: title || 'Site settings' };
    },
  },
});
