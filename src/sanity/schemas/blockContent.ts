import { defineType, defineArrayMember } from 'sanity';

export const blockContent = defineType({
  name: 'blockContent',
  title: 'Block content',
  type: 'array',
  of: [
    defineArrayMember({
      type: 'block',
      styles: [
        { title: 'Normal', value: 'normal' },
        { title: 'H2', value: 'h2' },
        { title: 'H3', value: 'h3' },
        { title: 'H4', value: 'h4' },
        { title: 'Quote', value: 'blockquote' },
      ],
      lists: [
        { title: 'Bullet', value: 'bullet' },
        { title: 'Numbered', value: 'number' },
      ],
      marks: {
        decorators: [
          { title: 'Strong', value: 'strong' },
          { title: 'Emphasis', value: 'em' },
          { title: 'Code', value: 'code' },
        ],
        annotations: [
          {
            name: 'link',
            type: 'object',
            title: 'Link',
            fields: [
              {
                name: 'href',
                type: 'url',
                title: 'URL',
                validation: (rule) =>
                  rule.uri({ scheme: ['http', 'https', 'mailto', 'tel'] }),
              },
              {
                name: 'blank',
                type: 'boolean',
                title: 'Open in new tab',
              },
            ],
          },
        ],
      },
    }),
    defineArrayMember({
      type: 'image',
      options: { hotspot: true },
      fields: [
        { name: 'alt', type: 'string', title: 'Alt text' },
        { name: 'caption', type: 'string', title: 'Caption' },
      ],
    }),
    defineArrayMember({
      type: 'object',
      name: 'callout',
      title: 'Callout',
      fields: [
        {
          name: 'tone',
          type: 'string',
          title: 'Tone',
          options: {
            list: [
              { title: 'Info', value: 'info' },
              { title: 'Note', value: 'note' },
              { title: 'Warning', value: 'warning' },
              { title: 'Success', value: 'success' },
            ],
            layout: 'radio',
          },
          initialValue: 'info',
        },
        { name: 'title', type: 'string', title: 'Title' },
        { name: 'body', type: 'text', title: 'Body', rows: 3 },
      ],
      preview: {
        select: { title: 'title', subtitle: 'body', tone: 'tone' },
        prepare({ title, subtitle, tone }) {
          return {
            title: `[${tone ?? 'info'}] ${title ?? 'Callout'}`,
            subtitle,
          };
        },
      },
    }),
    defineArrayMember({
      type: 'object',
      name: 'pullQuote',
      title: 'Pull quote',
      fields: [
        { name: 'quote', type: 'text', title: 'Quote', rows: 3 },
        { name: 'attribution', type: 'string', title: 'Attribution' },
      ],
      preview: {
        select: { title: 'quote', subtitle: 'attribution' },
      },
    }),
    defineArrayMember({
      type: 'object',
      name: 'codeBlock',
      title: 'Code block',
      fields: [
        {
          name: 'language',
          type: 'string',
          title: 'Language',
          options: {
            list: [
              'text',
              'bash',
              'js',
              'ts',
              'json',
              'html',
              'css',
              'python',
              'yaml',
              'sql',
            ].map((l) => ({ title: l, value: l })),
          },
          initialValue: 'text',
        },
        { name: 'code', type: 'text', title: 'Code', rows: 6 },
      ],
      preview: {
        select: { title: 'language', subtitle: 'code' },
      },
    }),
  ],
});
