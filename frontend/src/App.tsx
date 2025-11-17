import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { UIProvider } from './context/UIContext';
import { AlertProvider } from './context/AlertContext';
import { TenantProvider } from './context/TenantContext';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import OutputQuality from './pages/OutputQuality';
import Performance from './pages/Performance';
import Robustness from './pages/Robustness';
import Safety from './pages/Safety';
import UserExperience from './pages/UserExperience';
import Compliance from './pages/Compliance';
import History from './pages/History';
import Compare from './pages/Compare';
import Reports from './pages/Reports';
import Attribution from './pages/Attribution';
import Reasoning from './pages/Reasoning';
import Monitoring from './pages/Monitoring';
import WhatIfAnalysis from './pages/WhatIfAnalysis';
import EnterpriseDashboard from './pages/EnterpriseDashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <UIProvider>
        <TenantProvider>
          <AlertProvider>
            <BrowserRouter>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/enterprise" element={<EnterpriseDashboard />} />
                  <Route path="/output-quality" element={<OutputQuality />} />
                  <Route path="/performance" element={<Performance />} />
                  <Route path="/robustness" element={<Robustness />} />
                  <Route path="/safety" element={<Safety />} />
                  <Route path="/user-experience" element={<UserExperience />} />
                  <Route path="/compliance" element={<Compliance />} />
                  <Route path="/attribution" element={<Attribution />} />
                  <Route path="/reasoning" element={<Reasoning />} />
                  <Route path="/monitoring" element={<Monitoring />} />
                  <Route path="/whatif" element={<WhatIfAnalysis />} />
                  <Route path="/history" element={<History />} />
                  <Route path="/compare" element={<Compare />} />
                  <Route path="/reports" element={<Reports />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </BrowserRouter>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#1e293b',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 4000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </AlertProvider>
        </TenantProvider>
      </UIProvider>
    </QueryClientProvider>
  );
}

export default App;
