// Utilidades de formato para la UI

export function formatMXN(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(num)
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('es-MX', {
    day: '2-digit', month: 'short', year: 'numeric',
    timeZone: 'America/Mexico_City',
  }).format(new Date(iso))
}

export function formatDateTime(iso: string): string {
  return new Intl.DateTimeFormat('es-MX', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
    timeZone: 'America/Mexico_City',
  }).format(new Date(iso))
}

// Etiquetas en español para los estados del pedido
export const ORDER_STATUS_LABELS: Record<string, string> = {
  RECEIVED: 'Recibido',
  PENDING_ANALYSIS: 'Pendiente de análisis',
  QUOTED: 'Cotizado',
  APPROVED: 'Aprobado',
  PENDING_DEPOSIT: 'Pendiente de anticipo',
  DEPOSIT_PAID: 'Anticipo pagado',
  PRINTING: 'En impresión',
  POST_PROCESSING: 'En postprocesado',
  READY: 'Listo',
  PENDING_BALANCE: 'Pendiente de saldo',
  FULLY_PAID: 'Pagado completo',
  DELIVERED: 'Entregado',
  CANCELLED: 'Cancelado',
}

export const PRIORITY_LABELS: Record<string, string> = {
  NORMAL: 'Normal',
  URGENT: 'Urgente',
  EXPRESS: 'Express',
}

export const PAYMENT_STATUS_LABELS: Record<string, string> = {
  PENDING: 'Pendiente',
  CONFIRMED: 'Confirmado',
  REJECTED: 'Rechazado',
}

export const PAYMENT_TYPE_LABELS: Record<string, string> = {
  DEPOSIT: 'Anticipo',
  BALANCE: 'Saldo',
  FULL_PAYMENT: 'Pago completo',
  REFUND: 'Reembolso',
}
