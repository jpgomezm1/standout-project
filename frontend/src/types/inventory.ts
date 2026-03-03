export interface InventoryItem {
  id: string;
  property_id: string;
  item_name: string;
  category: string;
  expected_quantity: number;
  current_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
}
