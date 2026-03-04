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
      <span className="inline-flex items-center rounded-pill bg-badge-resolved-bg px-3 py-0.5 text-xs font-medium text-badge-resolved-text">
        Normal
      </span>
    );
  }

  const isCritical = currentQuantity <= Math.floor(lowStockThreshold / 2);

  return (
    <span
      className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
        isCritical
          ? 'bg-badge-danger-bg text-badge-danger-text'
          : 'bg-teal-subtle text-teal-600'
      }`}
    >
      {isCritical ? 'Crítico' : 'Bajo'}
    </span>
  );
}
