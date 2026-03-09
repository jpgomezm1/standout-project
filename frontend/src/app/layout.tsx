import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import { ToastProvider } from '@/components/shared/Toast';

export const metadata: Metadata = {
  title: 'StandOut - Panel de Operaciones',
  description: 'Panel de monitoreo de operaciones para alquileres de corta estancia',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="font-sans">
        <ToastProvider>
          <Sidebar />
          <main className="ml-72 min-h-screen bg-page">
            <div className="mx-auto max-w-6xl px-10 py-8">
              {children}
            </div>
          </main>
        </ToastProvider>
      </body>
    </html>
  );
}
