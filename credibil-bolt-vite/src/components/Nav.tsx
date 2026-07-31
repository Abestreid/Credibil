import { useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';

const NAV_LINKS = [
  { href: '#poisk', label: 'Поиск' },
  { href: '#kartochka', label: 'Карточка' },
  { href: '#svyazi', label: 'Связи' },
  { href: '#monitoring', label: 'Мониторинг' },
  { href: '#otchyoty', label: 'Отчёты' },
  { href: '#istochniki', label: 'Источники' },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-300 ${
        scrolled ? 'bg-navy/90 backdrop-blur-md border-b border-white/10' : 'bg-transparent'
      }`}
    >
      <nav className="mx-auto max-w-7xl px-5 sm:px-8 h-16 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2.5 group" aria-label="Credibil — на главную">
          <span className="relative inline-flex h-9 w-9 items-center justify-center">
            <svg viewBox="0 0 36 36" className="h-9 w-9" aria-hidden="true">
              <circle cx="18" cy="18" r="16" fill="none" stroke="#2A9C6F" strokeWidth="2" />
              <circle cx="18" cy="10" r="3" fill="#2A9C6F" />
              <circle cx="10" cy="24" r="3" fill="#FFFFFF" />
              <circle cx="26" cy="24" r="3" fill="#FFFFFF" />
              <line x1="18" y1="10" x2="10" y2="24" stroke="#2A9C6F" strokeWidth="1.5" opacity="0.6" />
              <line x1="18" y1="10" x2="26" y2="24" stroke="#2A9C6F" strokeWidth="1.5" opacity="0.6" />
              <line x1="10" y1="24" x2="26" y2="24" stroke="#FFFFFF" strokeWidth="1" opacity="0.3" />
            </svg>
          </span>
          <span className="text-white font-bold text-lg tracking-tight" translate="no">Credibil</span>
        </a>

        <ul className="hidden md:flex items-center gap-7">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm text-white/70 hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green rounded-sm"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden md:flex items-center gap-3">
          <a
            href="#demo"
            className="inline-flex items-center gap-2 rounded-full bg-green px-5 py-2 text-sm font-semibold text-white hover:bg-green-dark transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green focus-visible:ring-offset-2 focus-visible:ring-offset-navy"
          >
            Проверить компанию
          </a>
        </div>

        <button
          className="md:hidden inline-flex items-center justify-center h-10 w-10 text-white hover:bg-white/10 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green"
          aria-label={open ? 'Закрыть меню' : 'Открыть меню'}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden bg-navy border-t border-white/10">
          <ul className="px-5 py-4 space-y-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block py-2.5 text-white/80 hover:text-white transition-colors"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li>
              <a
                href="#demo"
                onClick={() => setOpen(false)}
                className="mt-2 inline-flex items-center rounded-full bg-green px-5 py-2.5 text-sm font-semibold text-white"
              >
                Проверить компанию
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
