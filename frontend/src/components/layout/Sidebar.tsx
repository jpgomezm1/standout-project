'use client';

import NavLink from './NavLink';

function BuildingIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      className="h-5 w-5"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Z"
      />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      className="h-5 w-5"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z"
      />
    </svg>
  );
}

function ExclamationIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      className="h-5 w-5"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
      />
    </svg>
  );
}

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-brand-950 shadow-sidebar">
      <div className="flex h-20 items-center gap-3 border-b border-brand-800/50 px-6">
        <img
          src="https://standout.com.co/cdn/shop/files/logo-standout-wt_150x.png?v=1733296563"
          alt="StandOut"
          className="h-8 w-auto"
        />
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-3 px-3 text-[11px] font-medium uppercase tracking-[0.15em] text-brand-500">
          Gestión
        </p>
        <NavLink
          href="/properties"
          icon={<BuildingIcon />}
          label="Propiedades"
        />
        <NavLink
          href="/staff"
          icon={<UsersIcon />}
          label="Personal"
        />
        <NavLink
          href="/incidents"
          icon={<ExclamationIcon />}
          label="Incidentes"
        />
      </nav>

      <div className="border-t border-brand-800/50 px-6 py-4">
        <p className="text-xs font-light tracking-wide text-brand-600">
          Panel de Operaciones
        </p>
      </div>
    </aside>
  );
}
