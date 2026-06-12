// Servicios de pagos para clientes
import api from '@/services/api'
import type { Payment, PaginatedResponse } from '@/types'

export async function listOrderPayments(orderId: string): Promise<PaginatedResponse<Payment>> {
  const { data } = await api.get(`/orders/${orderId}/payments/`)
  return data.data
}

export async function getPayment(paymentId: string): Promise<Payment> {
  const { data } = await api.get(`/payments/${paymentId}/`)
  return data.data
}

export async function uploadPaymentProof(paymentId: string, file: File): Promise<void> {
  const formData = new FormData()
  formData.append('file', file)
  await api.post(`/payments/${paymentId}/proof/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
