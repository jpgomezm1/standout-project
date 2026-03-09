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
      className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium tracking-wide transition-all duration-200 ${
        isActive
          ? 'bg-sidebar-active-bg text-sidebar-active-text'
          : 'text-sidebar-text hover:text-sidebar-text-hover hover:bg-white/5'
      }`}
    >
      <span className={`h-5 w-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-110 ${isActive ? 'text-indigo-300' : ''}`}>{icon}</span>
      <span>{label}</span>
      {isActive && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-300" />}
    </Link>
  );
}
