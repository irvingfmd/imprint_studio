// Servicios de autenticación
import api from '@/services/api'
import type { User, AuthTokens } from '@/types'

export async function register(payload: {
  phone: string
  email: string
  first_name: string
  last_name: string
}): Promise<void> {
  await api.post('/auth/register/', payload)
}

export async function sendOtp(phone: string): Promise<void> {
  await api.post('/auth/otp/send/', { phone })
}

export async function verifyOtp(phone: string, otp_code: string): Promise<AuthTokens> {
  const { data } = await api.post('/auth/otp/verify/', { phone, otp_code })
  return data
}

export async function getMe(): Promise<User> {
  const { data } = await api.get('/auth/me/')
  return data.data
}
