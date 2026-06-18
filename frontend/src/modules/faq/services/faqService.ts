// Servicios de FAQ
import api from '@/services/api'

export interface FAQ {
  id: string
  question: string
  answer: string
  display_order: number
}

export async function getFAQs(): Promise<FAQ[]> {
  const { data } = await api.get('/faq/')
  return data.data?.results ?? []
}
