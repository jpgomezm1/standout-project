'use client';

interface RelativeTimeProps {
  dateString: string;
}

function getRelativeTime(dateString: string): string {
  const now = Date.now();
  const date = new Date(dateString).getTime();
  const diffMs = now - date;

  if (diffMs < 0) return 'justo ahora';

  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return 'justo ahora';
  if (minutes < 60) return `hace ${minutes}m`;
  if (hours < 24) return `hace ${hours}h`;
  if (days < 7) return `hace ${days}d`;

  return new Date(dateString).toLocaleDateString('es-CO');
}

export default function RelativeTime({ dateString }: RelativeTimeProps) {
  const fullDate = new Date(dateString).toLocaleString('es-CO');

  return (
    <time dateTime={dateString} title={fullDate} className="text-sm font-light text-brand-500">
      {getRelativeTime(dateString)}
    </time>
  );
}
