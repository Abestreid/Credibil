import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/lib/auth';
import { useCallback, useState } from 'react';
import { appPath } from '@/lib/path';
import { useUnreadCount } from '@/lib/hooks';

const icons: Record<string, JSX.Element> = {
  grid: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>,
  search: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
  certificate: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" /></svg>,
  bell: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>,
};

export default function Layout() {
  const { t, i18n } = useTranslation();
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { data: unreadData } = useUnreadCount();
  const unread = unreadData?.data?.unread ?? 0;

  const nav = [
    { to: appPath('/dashboard'), label: t('nav.dashboard'), icon: 'grid' },
    { to: appPath('/search'), label: t('nav.search'), icon: 'search' },
    { to: appPath('/accreditations'), label: t('nav.acreditări'), icon: 'certificate' },
    { to: appPath('/monitoring'), label: t('nav.monitoring'), icon: 'bell', badge: unread },
  ];

  const handleLanguageChange = useCallback((newLang: string) => {
    const current = location.pathname.match(/^\/(ro|ru)\b/);
    if (current) {
      const newPath = location.pathname.replace(/^\/(ro|ru)\b/, `/${newLang}`);
      navigate(`${newPath}${location.search}${location.hash}`, { replace: true });
    }
    i18n.changeLanguage(newLang);
  }, [location.pathname, location.search, location.hash, navigate, i18n]);

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {sidebarOpen && (
        <div className="fixed inset-0 z-30 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:z-auto ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <span className="text-lg font-bold text-primary-600">Credibil</span>
        </div>
        <nav className="p-4 space-y-1">
          {nav.map((item) => {
            const active = location.pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${active ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}
              >
                {icons[item.icon]}
                <span className="flex-1">{item.label}</span>
                {item.badge ? (
                  <span className="text-xs font-semibold text-white bg-primary-600 rounded-full px-1.5 min-w-[1.25rem] text-center tabular-nums">
                    {item.badge}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 lg:px-6 shrink-0">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden p-2 -ml-2 text-gray-500">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
          <div className="flex-1" />
          <Link
            to={appPath('/monitoring')}
            className="relative mr-4 p-2 text-gray-500 hover:text-gray-700"
            aria-label={t('nav.monitoring')}
          >
            {icons.bell}
            {unread > 0 && (
              <span className="absolute -top-0.5 -right-0.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white tabular-nums">
                {unread > 99 ? '99+' : unread}
              </span>
            )}
          </Link>
          <select
            value={i18n.language?.startsWith('ru') ? 'ru' : 'ro'}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="mr-4 px-2 py-1 text-xs font-medium border border-gray-300 rounded bg-white text-gray-600 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="ro">Română</option>
            <option value="ru">Русский</option>
          </select>
          <button onClick={() => { logout(); navigate(appPath('/login')); }} className="text-sm text-gray-500 hover:text-gray-700">
            {t('nav.signOut')}
          </button>
        </header>
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
