const FOOTER_LINKS = {
  Продукт: [
    { label: 'Поиск', href: '#poisk' },
    { label: 'Карточка компании', href: '#kartochka' },
    { label: 'Корпоративные связи', href: '#svyazi' },
    { label: 'Мониторинг', href: '#monitoring' },
    { label: 'Отчёты', href: '#otchyoty' },
  ],
  Информация: [
    { label: 'Источники данных', href: '#istochniki' },
    { label: 'Важные ограничения', href: '#' },
  ],
};

export function Footer() {
  return (
    <footer className="bg-navy border-t border-white/10">
      <div className="mx-auto max-w-7xl px-5 sm:px-8 py-16">
        <div className="grid gap-12 lg:grid-cols-3">
          {/* Brand */}
          <div className="lg:col-span-1">
            <a href="#top" className="flex items-center gap-2.5 mb-4" aria-label="Credibil — на главную">
              <svg viewBox="0 0 36 36" className="h-9 w-9" aria-hidden="true">
                <circle cx="18" cy="18" r="16" fill="none" stroke="#2A9C6F" strokeWidth="2" />
                <circle cx="18" cy="10" r="3" fill="#2A9C6F" />
                <circle cx="10" cy="24" r="3" fill="#FFFFFF" />
                <circle cx="26" cy="24" r="3" fill="#FFFFFF" />
                <line x1="18" y1="10" x2="10" y2="24" stroke="#2A9C6F" strokeWidth="1.5" opacity="0.6" />
                <line x1="18" y1="10" x2="26" y2="24" stroke="#2A9C6F" strokeWidth="1.5" opacity="0.6" />
                <line x1="10" y1="24" x2="26" y2="24" stroke="#FFFFFF" strokeWidth="1" opacity="0.3" />
              </svg>
              <span className="text-white font-bold text-lg tracking-tight" translate="no">Credibil</span>
            </a>
            <p className="text-white/40 text-sm leading-relaxed max-w-xs">
              Сервис проверки компаний, контрагентов и связанных лиц в Республике Молдова.
            </p>
          </div>

          {/* Links */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-8">
            {Object.entries(FOOTER_LINKS).map(([title, links]) => (
              <div key={title}>
                <h3 className="text-white/80 font-semibold text-sm mb-4">{title}</h3>
                <ul className="space-y-3">
                  {links.map((link) => (
                    <li key={link.label}>
                      <a
                        href={link.href}
                        className="text-white/40 hover:text-white text-sm transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green rounded"
                      >
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-white/30 text-xs">
            Credibil не является государственным реестром и не заменяет юридическое заключение.
          </p>
          <p className="text-white/30 text-xs">
            Республика Молдова
          </p>
        </div>
      </div>
    </footer>
  );
}
