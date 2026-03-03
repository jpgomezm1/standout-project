'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';

interface NavLinkProps {
  href: string;
  icon: ReactNode;
  label: string;
}

export default function NavLink({ href, icon, label }: NavLinkProps) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname.startsWith(`${href}/`);

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium tracking-wide transition-all duration-200 ${
        isActive
          ? 'bg-brand-500/15 text-white'
          : 'text-brand-400 hover:bg-brand-800/40 hover:text-brand-200'
      }`}
    >
      <span className="h-5 w-5 flex-shrink-0">{icon}</span>
      <span>{label}</span>
    </Link>
  );
}
