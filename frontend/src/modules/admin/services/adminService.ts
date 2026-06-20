// Servicios administrativos
import api from '@/services/api'
import type {
  Order, AdminOrderSummary, AdminUser, Payment, BusinessConfig,
  PaymentInstructions, DashboardMetrics, PaginatedResponse, Printer, Material,
} from '@/types'

// --- Dashboard ---

export async function getDashboard(): Promise<DashboardMetrics> {
  const { data } = await api.get('/admin/dashboard/')
  return data.data
}

// --- Pedidos ---

export async function listAdminOrders(params?: Record<string, string>): Promise<PaginatedResponse<AdminOrderSummary>> {
  const { data } = await api.get('/admin/orders/', { params })
  return data.data
}

export async function getAdminOrder(orderId: string): Promise<Order> {
  const { data } = await api.get(`/admin/orders/${orderId}/`)
  return data.data
}

export async function updateOrderStatus(orderId: string, status: string, notes?: string): Promise<void> {
  await api.put(`/admin/orders/${orderId}/status/`, { status, notes: notes ?? '' })
}

export async function cancelOrderAdmin(orderId: string, reason: string): Promise<void> {
  await api.put(`/admin/orders/${orderId}/cancel/`, { reason })
}

export async function revertOrderStatus(orderId: string, reason: string): Promise<void> {
  await api.put(`/admin/orders/${orderId}/revert/`, { reason })
}

export async function createAdminOrder(payload: {
  customer_id: string
  request_type: string
  title: string
  description: string
  color: string
  quantity: number
  priority: string
  delivery_method: string
}): Promise<{ id: string; status: string }> {
  const { data } = await api.post('/admin/orders/create/', payload)
  return data.data
}

// --- Notas internas ---

export interface InternalNote {
  id: string
  content: string
  created_by: string | null
  created_by_name: string
  created_at: string
}

export async function listInternalNotes(orderId: string): Promise<PaginatedResponse<InternalNote>> {
  const { data } = await api.get(`/admin/orders/${orderId}/notes/`)
  return data.data
}

export async function createInternalNote(orderId: string, content: string): Promise<InternalNote> {
  const { data } = await api.post(`/admin/orders/${orderId}/notes/`, { content })
  return data.data
}

// --- Cotizaciones ---

export async function createQuote(orderId: string, payload: {
  weight_grams: string
  print_time_hours: string
  shipping_cost: string
  printer_id?: string | null
  include_post_processing?: boolean
}): Promise<{ quote_id: string; total_price: string }> {
  const { data } = await api.post(`/admin/orders/${orderId}/quote/`, payload)
  return data.data
}

export async function expireQuote(quoteId: string): Promise<void> {
  await api.put(`/admin/quotes/${quoteId}/expire/`)
}

export async function calculateQuote(payload: {
  weight_grams: string
  print_time_hours: string
  shipping_cost: string
  priority: string
  full_payment_selected: boolean
  printer_id?: string | null
  include_post_processing?: boolean
}): Promise<any> {
  const { data } = await api.post('/admin/calculator/calculate/', payload)
  return data.data
}

// --- Pagos ---

export async function listAdminPayments(params?: Record<string, string>): Promise<PaginatedResponse<Payment>> {
  const { data } = await api.get('/admin/payments/', { params })
  return data.data
}

export async function confirmPayment(paymentId: string, notes?: string): Promise<void> {
  await api.put(`/admin/payments/${paymentId}/confirm/`, { notes: notes ?? '' })
}

export async function rejectPayment(paymentId: string, reason: string): Promise<void> {
  await api.put(`/admin/payments/${paymentId}/reject/`, { reason })
}

export async function manualPayment(orderId: string, payload: {
  payment_type: string
  payment_method: string
  amount: string
  notes?: string
}): Promise<void> {
  await api.post(`/admin/orders/${orderId}/payments/manual-confirmation/`, payload)
}

export async function processRefund(orderId: string, payload: {
  amount: string
  reason: string
}): Promise<void> {
  await api.post(`/admin/orders/${orderId}/refund/`, payload)
}

// --- Envíos ---

export async function createShipment(orderId: string, payload: {
  carrier_name: string
  tracking_number: string
  shipping_cost: string
  shipping_notes?: string
}): Promise<void> {
  await api.post(`/admin/orders/${orderId}/shipment/`, payload)
}

export async function markDelivered(shipmentId: string): Promise<void> {
  await api.put(`/admin/shipments/${shipmentId}/delivered/`)
}

// --- Configuración ---

export async function getBusinessConfig(): Promise<BusinessConfig> {
  const { data } = await api.get('/admin/business-config/')
  return data.data
}

export async function updateBusinessConfig(payload: Partial<BusinessConfig>): Promise<BusinessConfig> {
  const { data } = await api.put('/admin/business-config/', payload)
  return data.data
}

export async function getPaymentInstructions(): Promise<PaymentInstructions> {
  const { data } = await api.get('/admin/payment-instructions/')
  return data.data
}

export async function updatePaymentInstructions(payload: Partial<PaymentInstructions>): Promise<PaymentInstructions> {
  const { data } = await api.put('/admin/payment-instructions/', payload)
  return data.data
}

export async function listBusinessHours(): Promise<any[]> {
  const { data } = await api.get('/admin/business-hours/')
  return data.data.results
}

export async function updateBusinessHours(payload: {
  weekday: number
  is_open: boolean
  opening_time?: string
  closing_time?: string
  notes?: string
}): Promise<void> {
  await api.put('/admin/business-hours/', payload)
}

export async function listHolidays(): Promise<any[]> {
  const { data } = await api.get('/admin/holidays/')
  return data.data.results
}

export async function createHoliday(payload: {
  holiday_date: string
  holiday_name: string
  affects_shipping: boolean
  affects_pickup: boolean
}): Promise<void> {
  await api.post('/admin/holidays/', payload)
}

export async function deleteHoliday(holidayId: string): Promise<void> {
  await api.delete(`/admin/holidays/${holidayId}/`)
}

// --- Usuarios ---

export async function listAdminUsers(params?: { page?: number; page_size?: number; search?: string }): Promise<PaginatedResponse<AdminUser>> {
  const { data } = await api.get('/admin/users/', { params })
  return data.data
}

export async function getAdminUser(userId: string): Promise<AdminUser> {
  const { data } = await api.get(`/admin/users/${userId}/`)
  return data.data
}

export async function updateUserRole(userId: string, role: 'CUSTOMER' | 'ADMIN'): Promise<AdminUser> {
  const { data } = await api.put(`/admin/users/${userId}/role/`, { role })
  return data.data
}

// --- Exportaciones CSV ---

async function downloadCSV(url: string, filename: string, params?: Record<string, string>): Promise<void> {
  const response = await api.get(url, { params, responseType: 'blob' })
  const blob = new Blob([response.data], { type: 'text/csv' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

export async function exportOrdersCSV(params?: Record<string, string>): Promise<void> {
  await downloadCSV('/admin/export/orders/', 'pedidos.csv', params)
}

export async function exportPaymentsCSV(params?: Record<string, string>): Promise<void> {
  await downloadCSV('/admin/export/payments/', 'pagos.csv', params)
}

// --- Historial de pagos de cliente ---

export async function getCustomerPaymentHistory(userId: string): Promise<{
  total_paid: string
  total_orders: number
  average_ticket: string
  payments: Payment[]
}> {
  const { data } = await api.get(`/admin/users/${userId}/payments/`)
  return data.data
}

// --- Impresoras ---

export async function listPrinters(activeOnly = false): Promise<Printer[]> {
  const { data } = await api.get('/admin/printers/', { params: activeOnly ? { active_only: 'true' } : {} })
  return data.data.results
}

export async function createPrinter(payload: { name: string; brand: string; power_watts: number; max_power_watts?: number | null; is_active: boolean }): Promise<Printer> {
  const { data } = await api.post('/admin/printers/', payload)
  return data.data
}

export async function updatePrinter(printerId: string, payload: { name?: string; brand?: string; power_watts?: number; max_power_watts?: number | null; is_active?: boolean }): Promise<Printer> {
  const { data } = await api.put(`/admin/printers/${printerId}/`, payload)
  return data.data
}

export async function deletePrinter(printerId: string): Promise<void> {
  await api.delete(`/admin/printers/${printerId}/`)
}

// --- Tarifas CFE ---

export interface CfeRateLookup {
  postal_code: string
  tariff_zone: string
  rate_kwh: string
  zone_description: string
}

export async function lookupElectricityRate(postalCode: string): Promise<CfeRateLookup> {
  const { data } = await api.get('/admin/electricity-rate-lookup/', { params: { postal_code: postalCode } })
  return data.data
}

// --- Materiales ---

export async function listMaterials(params?: { active_only?: boolean; low_stock?: boolean }): Promise<PaginatedResponse<Material>> {
  const queryParams: Record<string, string> = {}
  if (params?.active_only) queryParams.active_only = 'true'
  if (params?.low_stock) queryParams.low_stock = 'true'
  const { data } = await api.get('/admin/materials/', { params: queryParams })
  return data.data
}

export async function createMaterial(payload: {
  name: string
  material_type: string
  brand?: string
  available_colors?: string[]
  price_per_kg: string
  stock_grams?: string
  min_stock_grams?: string
  is_active?: boolean
}): Promise<Material> {
  const { data } = await api.post('/admin/materials/', payload)
  return data.data
}

export async function updateMaterial(materialId: string, payload: {
  name: string
  material_type: string
  brand?: string
  available_colors?: string[]
  price_per_kg: string
  stock_grams?: string
  min_stock_grams?: string
  is_active?: boolean
}): Promise<Material> {
  const { data } = await api.put(`/admin/materials/${materialId}/`, payload)
  return data.data
}

export async function deleteMaterial(materialId: string): Promise<void> {
  await api.delete(`/admin/materials/${materialId}/`)
}

export async function adjustStock(materialId: string, grams: string, operation: 'add' | 'deduct'): Promise<{ stock_grams: string }> {
  const { data } = await api.post(`/admin/materials/${materialId}/stock/`, { grams, operation })
  return data.data
}

// --- Descuentos ---

export interface DiscountCode {
  id: string
  code: string
  discount_type: 'PERCENTAGE' | 'FIXED_AMOUNT'
  discount_value: string
  min_order_amount: string
  max_uses: number | null
  current_uses: number
  valid_from: string
  valid_until: string | null
  is_active: boolean
  created_at: string
}

export async function listDiscountCodes(activeOnly = false): Promise<PaginatedResponse<DiscountCode>> {
  const params = activeOnly ? { active_only: 'true' } : {}
  const { data } = await api.get('/admin/discounts/', { params })
  return data.data
}

export async function createDiscountCode(payload: {
  code: string
  discount_type: string
  discount_value: string
  min_order_amount?: string
  max_uses?: number | null
  valid_from: string
  valid_until?: string | null
  is_active?: boolean
}): Promise<DiscountCode> {
  const { data } = await api.post('/admin/discounts/', payload)
  return data.data
}

export async function updateDiscountCode(discountId: string, payload: {
  code: string
  discount_type: string
  discount_value: string
  min_order_amount?: string
  max_uses?: number | null
  valid_from: string
  valid_until?: string | null
  is_active?: boolean
}): Promise<DiscountCode> {
  const { data } = await api.put(`/admin/discounts/${discountId}/`, payload)
  return data.data
}

export async function deleteDiscountCode(discountId: string): Promise<void> {
  await api.delete(`/admin/discounts/${discountId}/`)
}
