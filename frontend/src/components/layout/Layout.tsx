import { ReactNode } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useUI } from '../../context/UIContext';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { sidebarCollapsed } = useUI();

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main
          className={`flex-1 transition-all duration-300 ${
            sidebarCollapsed ? 'ml-16' : 'ml-64'
          } mt-16 p-8`}
        >
          <div className="max-w-[1800px] mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
}
