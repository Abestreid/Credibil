import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/lib/auth';
import LanguageRouter from '@/components/LanguageRouter';
import Layout from '@/components/Layout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import SearchPage from '@/pages/SearchPage';
import CompanyDetailPage from '@/pages/CompanyDetailPage';
import PersonDetailPage from '@/pages/PersonDetailPage';
import AccreditationsPage from '@/pages/AccreditationsPage';
import MonitoringPage from '@/pages/MonitoringPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { lang } = useParams<{ lang: string }>();
  const { authenticated, loading } = useAuth();
  if (loading) return null;
  if (!authenticated) return <Navigate to={`/${lang || 'ro'}/login`} replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/:lang/login" element={<LoginPage />} />
      <Route path="/:lang" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="companies/:id" element={<CompanyDetailPage />} />
        <Route path="companies/:id/:slug" element={<CompanyDetailPage />} />
        <Route path="persons/:id" element={<PersonDetailPage />} />
        <Route path="persons/:id/:slug" element={<PersonDetailPage />} />
        <Route path="accreditations" element={<AccreditationsPage />} />
        <Route path="monitoring" element={<MonitoringPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <LanguageRouter>
            <AppRoutes />
          </LanguageRouter>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
