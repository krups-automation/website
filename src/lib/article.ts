import { toHTML, escapeHTML } from '@portabletext/to-html';
import { imageSrcSet, imageUrl } from '../sanity/image';

/** "20. Januar 2021", or "2022" when only the year is known. */
export function formatArticleDate(publishedAt?: string, precision?: 'day' | 'year'): string {
  if (!publishedAt) return '';
  if (precision === 'year') return publishedAt.slice(0, 4);
  return new Date(publishedAt).toLocaleDateString('de-DE', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  });
}

/** Machine-readable value for <time datetime>. */
export function articleDateAttr(publishedAt?: string, precision?: 'day' | 'year'): string {
  if (!publishedAt) return '';
  return precision === 'year' ? publishedAt.slice(0, 4) : publishedAt.slice(0, 10);
}

/** Article body to HTML, including the image and callout blocks of blockContent. */
export function articleBodyHtml(body: unknown[] | undefined): string {
  if (!body) return '';
  return toHTML(body as any, {
    components: {
      types: {
        image: ({ value }: { value: any }) => {
          if (!value?.asset) return '';
          const alt = escapeHTML(value.alt ?? '');
          const caption = value.caption ? `<figcaption>${escapeHTML(value.caption)}</figcaption>` : '';
          return `<figure class="article-figure"><img src="${imageUrl(value, 1200)}" srcset="${imageSrcSet(value, { maxWidth: 1600 })}" sizes="(min-width: 900px) 720px, 100vw" alt="${alt}" loading="lazy" decoding="async" />${caption}</figure>`;
        },
        callout: ({ value }: { value: any }) => {
          const tone = ['info', 'note', 'warning', 'success'].includes(value?.tone) ? value.tone : 'info';
          const title = value?.title ? `<p class="callout-title">${escapeHTML(value.title)}</p>` : '';
          const text = value?.body ? `<p>${escapeHTML(value.body)}</p>` : '';
          return `<aside class="callout callout-${tone}">${title}${text}</aside>`;
        },
      },
      marks: {
        link: ({ children, value }: { children: string; value?: any }) => {
          const href = escapeHTML(value?.href ?? '#');
          const external = /^https?:\/\//.test(value?.href ?? '');
          const rel = external ? ' target="_blank" rel="noopener"' : '';
          return `<a href="${href}"${rel}>${children}</a>`;
        },
      },
    },
  });
}
