import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';

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
        <Sidebar />
        <main className="ml-72 min-h-screen bg-brand-50 px-10 py-8">
          <div className="mx-auto max-w-6xl">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
