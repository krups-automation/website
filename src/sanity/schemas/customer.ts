import { defineType, defineField } from 'sanity';

export const customer = defineType({
  name: 'customer',
  title: 'Customer',
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
      name: 'logo',
      title: 'Logo',
      type: 'image',
      options: { hotspot: true },
      fields: [{ name: 'alt', type: 'string', title: 'Alt text' }],
    }),
    defineField({
      name: 'industry',
      title: 'Industry',
      type: 'reference',
      to: [{ type: 'industry' }],
    }),
    defineField({
      name: 'country',
      title: 'Country',
      type: 'string',
    }),
    defineField({
      name: 'publiclyReferenceable',
      title: 'Publicly referenceable',
      description:
        'When enabled, this customer may be displayed publicly on the marketing site. Default off until Philipp confirms per customer.',
      type: 'boolean',
      initialValue: false,
    }),
    defineField({
      name: 'description',
      title: 'Internal description',
      description: 'Not rendered publicly.',
      type: 'text',
      rows: 3,
    }),
  ],
  preview: {
    select: {
      title: 'name',
      subtitle: 'country',
      media: 'logo',
      publiclyReferenceable: 'publiclyReferenceable',
    },
    prepare({ title, subtitle, media, publiclyReferenceable }) {
      const prefix = publiclyReferenceable ? '● ' : '○ ';
      return { title: `${prefix}${title}`, subtitle, media };
    },
  },
});
