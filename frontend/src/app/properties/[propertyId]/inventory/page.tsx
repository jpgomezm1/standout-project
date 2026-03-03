'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useProperty } from '@/hooks/useProperty';
import { useInventory } from '@/hooks/useInventory';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import StockAlert from '@/components/status/StockAlert';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import type { InventoryItem } from '@/types/inventory';

const columns: Column<InventoryItem>[] = [
  {
    key: 'item_name',
    header: 'Nombre del Ítem',
    render: (item) => (
      <span className="font-medium text-brand-950">{item.item_name}</span>
    ),
  },
  {
    key: 'category',
    header: 'Categoría',
    render: (item) => (
      <span className="text-sm text-brand-600">{item.category}</span>
    ),
  },
  {
    key: 'current_quantity',
    header: 'Cant. Actual',
    render: (item) => (
      <span
        className={`text-sm font-medium ${
          item.is_low_stock ? 'text-status-danger' : 'text-brand-950'
        }`}
      >
        {item.current_quantity}
      </span>
    ),
  },
  {
    key: 'expected_quantity',
    header: 'Cant. Esperada',
    render: (item) => (
      <span className="text-sm text-brand-600">{item.expected_quantity}</span>
    ),
  },
  {
    key: 'status',
    header: 'Estado',
    render: (item) => (
      <StockAlert
        currentQuantity={item.current_quantity}
        lowStockThreshold={item.low_stock_threshold}
      />
    ),
  },
];

export default function InventoryPage() {
  const params = useParams();
  const propertyId = params.propertyId as string;

  const { data: property } = useProperty(propertyId);
  const { data: inventory, isLoading, error, mutate } = useInventory(propertyId);

  const propertyName = property?.name || 'Propiedad';

  return (
    <div>
      <PageHeader
        title={`Inventario - ${propertyName}`}
        subtitle="Niveles actuales de inventario y alertas de stock"
        actions={
          <Link
            href={`/properties/${propertyId}`}
            className="rounded-pill border border-brand-300 bg-white px-4 py-2 text-sm font-medium text-brand-700 transition-colors hover:border-brand-500 hover:shadow-card"
          >
            Volver a Propiedad
          </Link>
        }
      />

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar datos de inventario."
            onRetry={() => mutate()}
          />
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={6} cols={5} />
      ) : (
        <DataTable<InventoryItem>
          columns={columns}
          data={inventory || []}
          emptyMessage="No se encontraron ítems de inventario"
          rowClassName={(item) =>
            item.is_low_stock ? 'bg-status-danger-light' : ''
          }
        />
      )}
    </div>
  );
}
