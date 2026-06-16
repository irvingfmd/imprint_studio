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
  // Estados de transacción de pago (Payment.payment_status)
  PENDING: 'Pendiente',
  CONFIRMED: 'Confirmado',
  REJECTED: 'Rechazado',
  // Estados de pago del pedido (Order.payment_status)
  NO_PAYMENT: 'Sin pago',
  DEPOSIT_PENDING: 'Anticipo pendiente',
  DEPOSIT_PAID: 'Anticipo pagado',
  BALANCE_PENDING: 'Saldo pendiente',
  FULLY_PAID: 'Pagado completo',
  REFUNDED: 'Reembolsado',
}

export const PAYMENT_TYPE_LABELS: Record<string, string> = {
  DEPOSIT: 'Anticipo',
  BALANCE: 'Saldo',
  FULL_PAYMENT: 'Pago completo',
  REFUND: 'Reembolso',
}

export const QUOTE_STATUS_LABELS: Record<string, string> = {
  PENDING: 'Pendiente',
  ACCEPTED: 'Aceptada',
  REJECTED: 'Rechazada',
  EXPIRED: 'Vencida',
}

export const REQUEST_TYPE_LABELS: Record<string, string> = {
  REFERENCE: 'Por referencia',
  PRINTABLE_FILE: 'Archivo 3D',
  WEB_MODEL: 'Enlace web',
}

export const DELIVERY_METHOD_LABELS: Record<string, string> = {
  PICKUP: 'Recoger en tienda',
  SHIPPING: 'Envío a domicilio',
}
