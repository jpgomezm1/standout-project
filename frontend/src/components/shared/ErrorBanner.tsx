interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="rounded-card border border-badge-danger-border bg-badge-danger-bg px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="h-5 w-5 text-badge-danger-text"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
            />
          </svg>
          <p className="text-sm font-medium text-badge-danger-text">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="rounded-pill bg-badge-danger-text/10 px-3 py-1 text-xs font-medium text-badge-danger-text transition-colors hover:bg-badge-danger-text/20"
          >
            Reintentar
          </button>
        )}
      </div>
    </div>
  );
}
