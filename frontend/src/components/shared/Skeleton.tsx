interface SkeletonProps {
  className?: string;
  rows?: number;
}

function SkeletonLine({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded bg-brand-200 ${className}`}
    />
  );
}

export default function Skeleton({ className, rows = 1 }: SkeletonProps) {
  if (rows === 1) {
    return <SkeletonLine className={className || 'h-4 w-full'} />;
  }

  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonLine
          key={i}
          className={className || 'h-4 w-full'}
        />
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="overflow-hidden rounded-card border border-brand-200 bg-white shadow-card">
      <div className="bg-brand-50 px-6 py-3">
        <div className="flex gap-6">
          {Array.from({ length: cols }).map((_, i) => (
            <SkeletonLine key={i} className="h-3 w-24" />
          ))}
        </div>
      </div>
      <div className="divide-y divide-brand-100">
        {Array.from({ length: rows }).map((_, rowIdx) => (
          <div key={rowIdx} className="flex gap-6 px-6 py-4">
            {Array.from({ length: cols }).map((_, colIdx) => (
              <SkeletonLine key={colIdx} className="h-4 w-24" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
