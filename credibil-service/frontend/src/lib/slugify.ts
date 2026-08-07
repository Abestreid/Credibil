export function slugify(text: string): string {
  const map: Record<string, string> = {
    'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ş': 's',
    'ț': 't', 'ţ': 't', 'Ă': 'a', 'Â': 'a', 'Î': 'i',
    'Ș': 's', 'Ş': 's', 'Ț': 't', 'Ţ': 't',
  };
  const normalized = text.replace(/[ăâîșşțţĂÂÎȘŞȚŢ]/g, (c) => map[c] ?? c);
  return normalized
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
