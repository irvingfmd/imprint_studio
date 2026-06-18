// Tipos compartidos de la aplicación Imprint Studio

export interface User {
  id: string
  phone: string
  email: string
  first_name: string
  last_name: string
  role: 'CUSTOMER' | 'ADMIN'
}

export interface AuthTokens {
  access: string
  refresh: string
}

export type OrderStatus =
  | 'RECEIVED'
  | 'PENDING_ANALYSIS'
  | 'QUOTED'
  | 'APPROVED'
  | 'PENDING_DEPOSIT'
  | 'DEPOSIT_PAID'
  | 'PRINTING'
  | 'POST_PROCESSING'
  | 'READY'
  | 'PENDING_BALANCE'
  | 'FULLY_PAID'
  | 'DELIVERED'
  | 'CANCELLED'

export type OrderPriority = 'NORMAL' | 'URGENT' | 'EXPRESS'
export type RequestType = 'REFERENCE' | 'PRINTABLE_FILE' | 'WEB_MODEL'
export type DeliveryMethod = 'PICKUP' | 'SHIPPING'
export type PaymentOption = 'DEPOSIT' | 'FULL_PAYMENT'

export interface OrderSummary {
  id: string
  title: string
  status: OrderStatus
  priority: OrderPriority
  payment_status?: string
  created_at: string
}

export interface AdminOrderSummary extends OrderSummary {
  customer_phone: string
  request_type: string
  delivery_method: string
}

export interface Order extends OrderSummary {
  description: string
  request_type: RequestType
  delivery_method: DeliveryMethod
  color: string
  quantity: number
  payment_status: string
  delivered_at?: string | null
  cancelled_at?: string | null
  shipping_address?: ShippingAddress
  shipment?: Shipment | null
  active_quote?: Quote | null
}

export interface Quote {
  id: string
  order_id: string
  weight_grams: string
  print_time_hours: string
  material_cost: string
  energy_cost: string
  labor_cost: string
  post_processing_cost: string
  packaging_cost: string
  risk_cost: string
  shipping_cost: string
  subtotal: string
  profit_amount: string
  discount_amount: string
  total_price: string
  quote_status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED'
  expires_at?: string | null
  accepted_at?: string | null
  rejected_at?: string | null
  created_at: string
}

export interface QuoteCalculation {
  material_cost: string
  energy_cost: string
  labor_cost: string
  post_processing_cost: string
  packaging_cost: string
  risk_cost: string
  shipping_cost: string
  subtotal: string
  profit_amount: string
  discount_amount: string
  total_price: string
}

export type PaymentStatus = 'PENDING' | 'CONFIRMED' | 'REJECTED'
export type PaymentType = 'DEPOSIT' | 'BALANCE' | 'FULL_PAYMENT' | 'REFUND'
export type PaymentMethod = 'BANK_TRANSFER' | 'CASH'

export interface Payment {
  id: string
  order: string
  amount: string
  payment_type: PaymentType
  payment_method: PaymentMethod
  payment_status: PaymentStatus
  proof_file_url: string | null
  manual_confirmation: boolean
  confirmed_by: string | null
  confirmed_at: string | null
  notes: string
  created_at: string
}

export interface ShippingAddress {
  id: string
  address_name: string
  street: string
  external_number: string
  internal_number: string
  neighborhood: string
  postal_code: string
  city: string
  state: string
  country: string
  references: string
}

export interface Shipment {
  id: string
  carrier_name: string
  tracking_number: string
  shipped_at: string | null
  delivered_at: string | null
}

export interface ProductionHistoryEntry {
  id: string
  previous_status: OrderStatus
  new_status: OrderStatus
  notes: string
  changed_at: string
}

export interface OrderEvent {
  id: string
  event_type: string
  event_description: string
  created_at: string
}

export interface Printer {
  id: string
  name: string
  brand: string
  power_watts: number
  max_power_watts: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BusinessConfig {
  material_cost_per_kg: string
  electricity_rate_kwh: string
  labor_cost_per_hour: string
  post_processing_cost_per_gram: string
  packaging_cost: string
  failure_percentage: string
  profit_margin_percentage: string
  urgent_multiplier: string
  express_multiplier: string
  full_payment_discount_percentage: string
  deposit_deadline_hours: number | string
  balance_deadline_days: number | string
}

export interface PaymentInstructions {
  bank_name: string
  account_holder: string
  account_number: string
  clabe: string
  card_number: string
  additional_notes: string
}

export interface DashboardMetrics {
  pending_orders: number
  quoted_orders: number
  printing_orders: number
  ready_orders: number
  pending_payments: number
  monthly_revenue: string
  revenue_by_month: { month: string; revenue: string }[]
  orders_this_month: number
  orders_prev_month: number
  avg_delivery_days: number | null
  cancellation_rate: number
  request_type_counts: { request_type: string; count: number }[]
  priority_counts: { priority: string; count: number }[]
}

export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  count: number
  num_pages?: number
  results: T[]
}

export interface AdminUser {
  id: string
  phone: string
  email: string | null
  first_name: string
  last_name: string
  role: 'CUSTOMER' | 'ADMIN'
  is_active: boolean
  created_at: string
}
