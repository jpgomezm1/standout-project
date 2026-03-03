import { ReactNode } from 'react';

interface TimelineEntryProps {
  dotColor?: string;
  isLast?: boolean;
  children: ReactNode;
}

export default function TimelineEntry({
  dotColor = 'bg-brand-400',
  isLast = false,
  children,
}: TimelineEntryProps) {
  return (
    <div className="relative flex gap-4 pb-6">
      <div className="flex flex-col items-center">
        <div
          className={`relative z-10 h-2.5 w-2.5 rounded-full ring-4 ring-white ${dotColor}`}
        />
        {!isLast && (
          <div className="w-px flex-1 bg-brand-200" />
        )}
      </div>
      <div className="flex-1 pb-2">{children}</div>
    </div>
  );
}
