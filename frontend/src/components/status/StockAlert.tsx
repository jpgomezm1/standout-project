interface StockAlertProps {
  currentQuantity: number;
  lowStockThreshold: number;
}

export default function StockAlert({
  currentQuantity,
  lowStockThreshold,
}: StockAlertProps) {
  if (currentQuantity >= lowStockThreshold) {
    return (
      <span className="inline-flex items-center rounded-pill bg-status-success-light px-3 py-0.5 text-xs font-medium text-status-success-dark">
        Normal
      </span>
    );
  }

  const isCritical = currentQuantity <= Math.floor(lowStockThreshold / 2);

  return (
    <span
      className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
        isCritical
          ? 'bg-status-danger-light text-status-danger-dark'
          : 'bg-status-warning-light text-status-warning-dark'
      }`}
    >
      {isCritical ? 'Crítico' : 'Bajo'}
    </span>
  );
}
