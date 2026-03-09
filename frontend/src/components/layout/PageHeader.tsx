import { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export default function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="animate-fade-up mb-8 flex items-end justify-between border-b border-card-border pb-6">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-text-primary">{title}</h1>
        {subtitle && (
          <p className="mt-1.5 text-sm font-light text-text-muted">{subtitle}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
}
