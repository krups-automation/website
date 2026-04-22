import imageUrlBuilder from '@sanity/image-url';
import type { ImageUrlBuilder } from '@sanity/image-url/lib/types/builder';
import type { SanityImageSource } from '@sanity/image-url/lib/types/types';

const builder = imageUrlBuilder({
  projectId: '8075qdie',
  dataset: 'production',
});

/** Returns a Sanity image URL builder for chaining (e.g. `urlFor(img).width(800).auto('format')`). */
export function urlFor(source: SanityImageSource): ImageUrlBuilder {
  return builder.image(source);
}

/** Default widths for responsive srcset (covers mobile → 4K displays). */
export const DEFAULT_WIDTHS = [400, 640, 800, 1024, 1280, 1600, 2000, 2560];

interface SrcSetOptions {
  widths?: number[];
  /** 'webp' | 'jpg' | 'avif' | 'png' — defaults to 'webp' for broad support + small files. */
  format?: 'webp' | 'jpg' | 'avif' | 'png';
  /** 0-100. Sanity default ~75. */
  quality?: number;
  /** Cap the max dimension; useful when the image is rendered at ≤1280px regardless of viewport. */
  maxWidth?: number;
}

/**
 * Returns a srcset string with multiple widths for a Sanity image.
 * Pair with a `sizes` attribute that describes the layout (e.g. `"(min-width: 900px) 50vw, 100vw"`).
 */
export function imageSrcSet(source: SanityImageSource, opts: SrcSetOptions = {}): string {
  const { widths = DEFAULT_WIDTHS, format = 'webp', quality = 80, maxWidth } = opts;
  const effective = maxWidth
    ? widths.filter((w) => w <= maxWidth).concat(maxWidth).sort((a, b) => a - b)
    : widths;
  const unique = Array.from(new Set(effective));
  return unique
    .map((w) => `${urlFor(source).width(w).format(format).quality(quality).url()} ${w}w`)
    .join(', ');
}

/** Convenience: a single URL at a target width, auto format, default quality. */
export function imageUrl(source: SanityImageSource, width: number, format: 'webp' | 'jpg' | 'avif' = 'webp'): string {
  return urlFor(source).width(width).format(format).quality(80).url();
}

/** Tiny low-quality placeholder (~20px wide, blurry) for progressive loading / skeletons. */
export function lqipUrl(source: SanityImageSource): string {
  return urlFor(source).width(24).quality(30).blur(20).format('jpg').url();
}

/** Extract the Sanity-provided LQIP data URL if present on the asset metadata. */
export function assetLqip(
  source: SanityImageSource & { asset?: { metadata?: { lqip?: string } } }
): string | undefined {
  return source?.asset?.metadata?.lqip;
}
