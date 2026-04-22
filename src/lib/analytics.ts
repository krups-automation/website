/**
 * Thin wrapper around the PostHog snippet that may or may not be loaded on
 * the current page. All methods no-op if PostHog hasn't been initialized,
 * so callers never have to guard for consent state.
 */

type PostHogLike = {
  capture: (event: string, properties?: Record<string, unknown>) => void;
  identify: (distinctId: string, properties?: Record<string, unknown>) => void;
  reset: () => void;
  opt_in_capturing: () => void;
  opt_out_capturing: () => void;
};

function getPH(): PostHogLike | null {
  if (typeof window === 'undefined') return null;
  const ph = (window as unknown as { posthog?: PostHogLike }).posthog;
  return ph && typeof ph.capture === 'function' ? ph : null;
}

export function track(event: string, properties?: Record<string, unknown>): void {
  getPH()?.capture(event, properties);
}

export function identify(distinctId: string, properties?: Record<string, unknown>): void {
  getPH()?.identify(distinctId, properties);
}

export function resetIdentity(): void {
  getPH()?.reset();
}

/** User revokes consent → clear stored flag + request PostHog to stop. */
export function revokeConsent(): void {
  try {
    localStorage.setItem('krups-consent', 'rejected');
  } catch (_) {
    /* ignore */
  }
  getPH()?.opt_out_capturing();
}
