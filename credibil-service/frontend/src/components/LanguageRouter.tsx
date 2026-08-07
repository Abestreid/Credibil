import { useEffect, type ReactNode } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import i18n, { detectLanguage } from '@/i18n';

const LOCALE_KEY = 'i18nextLng';

function setStoredLanguage(lng: 'ro' | 'ru') {
  try { localStorage.setItem(LOCALE_KEY, lng); } catch { /* noop */ }
}

function stripLang(pathname: string): { lang: 'ro' | 'ru'; rest: string } | null {
  const match = pathname.match(/^\/(ro|ru)(\/.*)?$/);
  if (!match) return null;
  return { lang: match[1] as 'ro' | 'ru', rest: match[2] || '/' };
}

export default function LanguageRouter({ children }: { children: ReactNode }) {
  const { pathname, search, hash } = useLocation();
  const navigate = useNavigate();

  const parsed = stripLang(pathname);

  useEffect(() => {
    if (parsed) {
      if (i18n.language !== parsed.lang) {
        i18n.changeLanguage(parsed.lang);
        setStoredLanguage(parsed.lang);
      }
    } else {
      const detected = detectLanguage();
      setStoredLanguage(detected);
      const target = `/${detected}${pathname === '/' ? '' : pathname}${search}${hash}`;
      navigate(target, { replace: true });
    }
  }, [pathname]);

  if (!parsed) return null;

  return <>{children}</>;
}
