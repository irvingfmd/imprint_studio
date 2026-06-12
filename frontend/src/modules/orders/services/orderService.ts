// Servicios de pedidos para clientes
import api from '@/services/api'
import type { Order, OrderSummary, OrderEvent, ProductionHistoryEntry, PaginatedResponse } from '@/types'

export async function listOrders(): Promise<PaginatedResponse<OrderSummary>> {
  const { data } = await api.get('/orders/')
  return data.data
}

export async function getOrder(orderId: string): Promise<Order> {
  const { data } = await api.get(`/orders/${orderId}/`)
  return data.data
}

export async function createOrder(payload: {
  request_type: string
  title: string
  description: string
  color: string
  quantity: number
  priority: string
  delivery_method: string
}): Promise<{ id: string }> {
  const { data } = await api.post('/orders/', payload)
  return data.data
}

export async function cancelOrder(orderId: string, reason: string): Promise<void> {
  await api.put(`/orders/${orderId}/cancel/`, { reason })
}

export async function assignShippingAddress(orderId: string, shippingAddressId: string): Promise<void> {
  await api.put(`/orders/${orderId}/shipping-address/`, { shipping_address_id: shippingAddressId })
}

export async function listOrderFiles(orderId: string): Promise<PaginatedResponse<any>> {
  const { data } = await api.get(`/orders/${orderId}/files/`)
  return data.data
}

export async function uploadOrderFile(orderId: string, file: File, fileType: string): Promise<void> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('file_type', fileType)
  await api.post(`/orders/${orderId}/files/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export async function listProductionHistory(orderId: string): Promise<PaginatedResponse<ProductionHistoryEntry>> {
  const { data } = await api.get(`/orders/${orderId}/production-history/`)
  return data.data
}

export async function listOrderEvents(orderId: string): Promise<PaginatedResponse<OrderEvent>> {
  const { data } = await api.get(`/orders/${orderId}/events/`)
  return data.data
}
