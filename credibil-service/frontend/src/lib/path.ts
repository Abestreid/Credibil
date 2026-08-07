export function appPath(path: string): string {
  let lang = 'ro';
  try {
    const match = window.location.pathname.match(/^\/(ro|ru)\b/);
    if (match) lang = match[1];
  } catch { /* noop */ }
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `/${lang}${normalized}`;
}
