// Servicios de cotizaciones para clientes
import api from '@/services/api'
import type { Quote, PaginatedResponse } from '@/types'

export async function listOrderQuotes(orderId: string): Promise<PaginatedResponse<Quote>> {
  const { data } = await api.get(`/orders/${orderId}/quotes/`)
  return data.data
}

export async function getQuote(quoteId: string): Promise<Quote> {
  const { data } = await api.get(`/quotes/${quoteId}/`)
  return data.data
}

export async function acceptQuote(quoteId: string, paymentOption: 'DEPOSIT' | 'FULL_PAYMENT'): Promise<void> {
  await api.put(`/quotes/${quoteId}/accept/`, { payment_option: paymentOption })
}

export async function rejectQuote(quoteId: string, reason: string): Promise<void> {
  await api.put(`/quotes/${quoteId}/reject/`, { reason })
}
