<template>
  <div class="p-6 max-w-3xl">
    <RouterLink to="/orders" class="text-sm text-gray-400 hover:text-gray-200 flex items-center gap-1 mb-4 w-fit">
      ← Mis pedidos
    </RouterLink>

    <div v-if="loading" class="space-y-4">
      <div class="h-32 bg-gray-800 rounded-xl animate-pulse" />
      <div class="h-48 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="!order && !loading" class="text-center py-16">
      <div class="text-4xl mb-3">🔍</div>
      <p class="text-gray-300 font-medium">Pedido no encontrado</p>
      <p class="text-gray-500 text-sm mt-1">Es posible que haya sido eliminado o no tengas acceso.</p>
      <RouterLink to="/orders" class="inline-block mt-4">
        <AppButton variant="secondary" size="sm">← Volver a mis pedidos</AppButton>
      </RouterLink>
    </div>

    <template v-else-if="order">
      <!-- Encabezado -->
      <div class="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 class="text-xl font-semibold text-white">{{ order.title }}</h1>
          <p class="text-gray-400 text-sm mt-0.5">{{ formatDateTime(order.created_at) }}</p>
        </div>
        <StatusBadge :status="order.status" />
      </div>

      <!-- Detalle del pedido -->
      <AppCard class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Detalles</h3>
        <dl class="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
          <div>
            <dt class="text-gray-500">Tipo</dt>
            <dd class="text-gray-200 mt-0.5">{{ REQUEST_TYPE_LABELS[order.request_type] }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Prioridad</dt>
            <dd class="text-gray-200 mt-0.5">{{ PRIORITY_LABELS[order.priority] }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Color</dt>
            <dd class="text-gray-200 mt-0.5">{{ order.color || '—' }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Cantidad</dt>
            <dd class="text-gray-200 mt-0.5">{{ order.quantity }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Entrega</dt>
            <dd class="text-gray-200 mt-0.5">{{ DELIVERY_METHOD_LABELS[order.delivery_method] }}</dd>
          </div>
          <div class="col-span-2" v-if="order.description">
            <dt class="text-gray-500">Descripción</dt>
            <dd class="text-gray-200 mt-0.5">{{ order.description }}</dd>
          </div>
        </dl>
      </AppCard>

      <!-- Archivos adjuntos -->
      <AppCard v-if="files.length > 0 || canUploadFiles" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Archivos adjuntos</h3>
        <ul v-if="files.length > 0" class="space-y-2 mb-3">
          <li v-for="file in files" :key="file.id" class="flex items-center gap-2 text-sm">
            <template v-if="file.file_type === 'WEB_MODEL'">
              <span class="text-gray-500">🔗</span>
              <a :href="file.file_url" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:underline truncate">
                {{ file.original_filename || file.file_url }}
              </a>
              <span class="text-xs text-gray-600 shrink-0">Enlace web</span>
            </template>
            <template v-else>
              <span class="text-gray-500">📎</span>
              <a :href="file.file_url" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:underline truncate">
                {{ file.original_filename }}
              </a>
              <span class="text-xs text-gray-600 shrink-0 uppercase">{{ file.file_type }}</span>
            </template>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 mb-3">Sin archivos adjuntos aún.</p>
        <div v-if="canUploadFiles" :class="{ 'pt-3 border-t border-gray-700': files.length > 0 }">
          <input
            type="file"
            :accept="order!.request_type === 'REFERENCE' ? 'image/*' : '.stl,.obj,.3mf'"
            multiple
            class="hidden"
            ref="addFileInput"
            @change="handleAddFile"
          />
          <AppButton size="sm" variant="secondary" :loading="uploadingFile" @click="(addFileInput as HTMLInputElement)?.click()">
            + Agregar {{ order!.request_type === 'REFERENCE' ? 'imágenes' : 'archivo 3D' }}
          </AppButton>
        </div>
      </AppCard>

      <!-- Cotización activa -->
      <AppCard v-if="activeQuote" class="mb-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-medium text-gray-400">Cotización</h3>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">{{ formatDate(activeQuote.created_at) }}</span>
            <StatusBadge :status="activeQuote.quote_status" type="quote" />
            <AppButton
              size="sm"
              variant="ghost"
              :loading="downloadingPDF"
              @click="handleDownloadPDF"
              title="Descargar PDF"
            >
              📄 PDF
            </AppButton>
          </div>
        </div>

        <div class="space-y-2 text-sm">
          <div class="flex justify-between text-gray-400">
            <span>Material</span><span class="text-gray-300">{{ formatMXN(activeQuote.material_cost) }}</span>
          </div>
          <div class="flex justify-between text-gray-400">
            <span>Energía</span><span class="text-gray-300">{{ formatMXN(activeQuote.energy_cost) }}</span>
          </div>
          <div class="flex justify-between text-gray-400">
            <span>Mano de obra</span><span class="text-gray-300">{{ formatMXN(activeQuote.labor_cost) }}</span>
          </div>
          <div v-if="Number(activeQuote.post_processing_cost) > 0" class="flex justify-between text-gray-400">
            <span>Post-procesado</span><span class="text-gray-300">{{ formatMXN(activeQuote.post_processing_cost) }}</span>
          </div>
          <div v-if="Number(activeQuote.shipping_cost) > 0" class="flex justify-between text-gray-400">
            <span>Envío</span><span class="text-gray-300">{{ formatMXN(activeQuote.shipping_cost) }}</span>
          </div>
          <div v-if="Number(activeQuote.discount_amount) > 0" class="flex justify-between text-green-400">
            <span>Descuento por pago completo</span><span>-{{ formatMXN(activeQuote.discount_amount) }}</span>
          </div>
          <div class="flex justify-between font-semibold text-white pt-2 border-t border-gray-700">
            <span>Total</span><span>{{ formatMXN(activeQuote.total_price) }}</span>
          </div>
        </div>

        <!-- Acciones si está pendiente -->
        <div v-if="activeQuote.quote_status === 'PENDING'" class="mt-4 space-y-2">
          <p class="text-xs text-gray-500">Selecciona la modalidad de pago:</p>
          <div class="flex gap-2">
            <AppButton class="flex-1" :loading="accepting" @click="handleAccept('DEPOSIT')">
              ✓ Anticipo 50%
            </AppButton>
            <AppButton class="flex-1" :loading="accepting" @click="handleAccept('FULL_PAYMENT')">
              ✓ Pago completo (5% dto)
            </AppButton>
          </div>
          <AppButton variant="ghost" class="w-full" :loading="rejecting" @click="showRejectModal = true">
            ✕ Rechazar cotización
          </AppButton>
        </div>

        <p v-if="activeQuote.quote_status === 'EXPIRED'" class="mt-3 text-xs text-yellow-400">
          Esta cotización ha vencido. Espera a que el administrador genere una nueva.
        </p>
      </AppCard>

      <!-- Sin cotización aún -->
      <AppCard v-else-if="['RECEIVED', 'PENDING_ANALYSIS'].includes(order.status)" class="mb-4">
        <p class="text-sm text-gray-400">Tu pedido está siendo revisado. Recibirás una cotización pronto.</p>
      </AppCard>

      <!-- Estimado de entrega -->
      <AppCard v-if="deliveryEstimate" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-1">Tiempo de entrega estimado</h3>
        <template v-if="deliveryEstimate.type === 'range'">
          <p class="text-white font-medium">{{ deliveryEstimate.from }} – {{ deliveryEstimate.to }}</p>
          <p class="text-xs text-gray-500 mt-0.5">No incluye sábados, domingos ni días festivos.</p>
        </template>
        <template v-else>
          <p class="text-gray-300 text-sm">{{ deliveryEstimate.label }}</p>
          <p class="text-xs text-gray-500 mt-0.5">El plazo inicia una vez que se confirme tu anticipo. No incluye sábados, domingos ni festivos.</p>
        </template>
      </AppCard>

      <!-- Pagos -->
      <AppCard v-if="payments.length > 0" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Pagos</h3>
        <div class="space-y-2">
          <div
            v-for="payment in payments"
            :key="payment.id"
            class="flex items-center justify-between text-sm py-2 border-b border-gray-700 last:border-0"
          >
            <div>
              <p class="text-gray-200">{{ PAYMENT_TYPE_LABELS[payment.payment_type] }}</p>
              <p class="text-gray-500 text-xs">{{ formatDate(payment.created_at) }}</p>
            </div>
            <div class="text-right">
              <p class="text-gray-200 font-medium">{{ formatMXN(payment.amount) }}</p>
              <StatusBadge :status="payment.payment_status" type="payment" />
            </div>
          </div>
        </div>

        <!-- Subir comprobante -->
        <div v-if="pendingPayment" class="mt-3 pt-3 border-t border-gray-700">
          <p class="text-xs text-gray-400 mb-2">Sube tu comprobante de pago para que el administrador lo confirme:</p>
          <div class="flex gap-2">
            <input type="file" accept="image/*,.pdf" class="hidden" ref="proofInput" @change="handleProofUpload" />
            <AppButton size="sm" variant="secondary" @click="(proofInput as HTMLInputElement)?.click()" :loading="uploadingProof">
              📎 Subir comprobante
            </AppButton>
          </div>
        </div>
      </AppCard>

      <!-- Timeline de seguimiento -->
      <AppCard v-if="history.length > 0" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-4">Seguimiento del pedido</h3>
        <ol class="relative ml-3">
          <li
            v-for="(entry, idx) in history"
            :key="entry.id"
            class="relative pl-7 pb-6 last:pb-0"
          >
            <!-- Línea vertical -->
            <div
              v-if="idx < history.length - 1"
              class="absolute left-0 top-3 w-0.5 h-full"
              :class="entry.new_status === 'CANCELLED' ? 'bg-red-800' : 'bg-gray-700'"
            />

            <!-- Dot -->
            <div
              class="absolute left-0 top-0.5 -translate-x-1/2 rounded-full border-2 flex items-center justify-center"
              :class="timelineDotClass(entry.new_status, idx)"
            >
              <svg v-if="idx < history.length - 1 && entry.new_status !== 'CANCELLED'" class="w-2.5 h-2.5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>

            <!-- Contenido -->
            <div class="min-w-0">
              <p
                class="text-sm font-medium"
                :class="idx === history.length - 1 ? 'text-blue-400' : entry.new_status === 'CANCELLED' ? 'text-red-400' : 'text-gray-200'"
              >
                {{ ORDER_STATUS_LABELS[entry.new_status] || entry.new_status }}
              </p>
              <p class="text-xs text-gray-500 mt-0.5">{{ formatDateTime(entry.changed_at) }}</p>
              <p v-if="entry.notes" class="text-xs text-gray-500 mt-1 leading-relaxed">{{ entry.notes }}</p>
            </div>
          </li>
        </ol>
      </AppCard>

      <!-- Pedido entregado -->
      <AppCard v-if="order.status === 'DELIVERED'" class="mb-4 border-emerald-800">
        <div class="flex items-center gap-3">
          <span class="text-2xl">✓</span>
          <div>
            <p class="text-emerald-300 font-semibold text-sm">¡Pedido entregado!</p>
            <p v-if="order.delivered_at" class="text-gray-400 text-xs mt-0.5">
              Entregado el {{ formatDate(order.delivered_at) }}
            </p>
          </div>
        </div>
      </AppCard>

      <!-- Cancelar pedido -->
      <div v-if="canCancel" class="mt-4">
        <AppButton variant="danger" size="sm" @click="showCancelModal = true">
          Cancelar pedido
        </AppButton>
      </div>
    </template>

    <AppAlert :message="errorMessage" class="mt-4" />

    <!-- Modal: rechazar cotización -->
    <div
      v-if="showRejectModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="reject-modal-title"
      @keydown.esc="showRejectModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 id="reject-modal-title" class="text-lg font-semibold text-white mb-3">Rechazar cotización</h3>
        <AppInput v-model="rejectReason" label="Motivo (opcional)" placeholder="¿Por qué rechazas la cotización?" />
        <div class="flex gap-2 mt-4">
          <AppButton variant="ghost" class="flex-1" @click="showRejectModal = false">Cancelar</AppButton>
          <AppButton variant="danger" class="flex-1" :loading="rejecting" @click="handleReject">Rechazar</AppButton>
        </div>
      </div>
    </div>

    <!-- Modal: cancelar pedido -->
    <div
      v-if="showCancelModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="cancel-modal-title"
      @keydown.esc="showCancelModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 id="cancel-modal-title" class="text-lg font-semibold text-white mb-2">Cancelar pedido</h3>
        <p class="text-xs text-gray-500 mb-3">Esta acción no se puede deshacer.</p>
        <AppInput v-model="cancelReason" label="Motivo" placeholder="¿Por qué cancelas el pedido?" />
        <div class="flex gap-2 mt-4">
          <AppButton variant="ghost" class="flex-1" @click="showCancelModal = false">Volver</AppButton>
          <AppButton variant="danger" class="flex-1" :loading="cancelling" @click="handleCancel">Cancelar pedido</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getOrder, listProductionHistory, cancelOrder, listOrderFiles, uploadOrderFile } from '../services/orderService'
import { listOrderQuotes, acceptQuote, rejectQuote, downloadQuotePDF } from '@/modules/quotes/services/quoteService'
import { listOrderPayments, uploadPaymentProof } from '@/modules/payments/services/paymentService'
import { formatMXN, formatDate, formatDateTime, ORDER_STATUS_LABELS, PRIORITY_LABELS, PAYMENT_TYPE_LABELS, REQUEST_TYPE_LABELS, DELIVERY_METHOD_LABELS } from '@/utils/formatters'
import { useToast } from '@/composables/useToast'
import type { Order, Quote, Payment, ProductionHistoryEntry } from '@/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const orderId = String(route.params.id)

const order = ref<Order | null>(null)
const activeQuote = ref<Quote | null>(null)
const payments = ref<Payment[]>([])
const history = ref<ProductionHistoryEntry[]>([])
const files = ref<any[]>([])
const loading = ref(true)
const errorMessage = ref('')
const accepting = ref(false)
const rejecting = ref(false)
const cancelling = ref(false)
const uploadingProof = ref(false)
const showRejectModal = ref(false)
const showCancelModal = ref(false)
const downloadingPDF = ref(false)
const rejectReason = ref('')
const cancelReason = ref('')
const proofInput = ref<HTMLInputElement | null>(null)
const addFileInput = ref<HTMLInputElement | null>(null)
const uploadingFile = ref(false)

const CANCELLABLE_STATUSES = ['RECEIVED', 'PENDING_ANALYSIS', 'QUOTED', 'APPROVED', 'PENDING_DEPOSIT']

function timelineDotClass(status: string, idx: number): string {
  if (status === 'CANCELLED') return 'w-5 h-5 bg-red-900 border-red-500'
  if (idx === history.value.length - 1) return 'w-5 h-5 bg-blue-900 border-blue-400'
  return 'w-5 h-5 bg-emerald-900/50 border-emerald-600'
}

const canCancel = computed(() => order.value && CANCELLABLE_STATUSES.includes(order.value.status))
const pendingPayment = computed(() => payments.value.find(p => p.payment_status === 'PENDING'))
const canUploadFiles = computed(() =>
  order.value &&
  ['REFERENCE', 'PRINTABLE_FILE'].includes(order.value.request_type) &&
  ['RECEIVED', 'PENDING_ANALYSIS'].includes(order.value.status)
)

const DELIVERY_RANGES: Record<string, { min: number; max: number; label: string }> = {
  NORMAL:  { min: 5, max: 7, label: '5 a 7 días hábiles' },
  URGENT:  { min: 2, max: 3, label: '2 a 3 días hábiles' },
  EXPRESS: { min: 1, max: 2, label: '24 a 48 horas hábiles' },
}

function addWorkingDays(start: Date, days: number): Date {
  const d = new Date(start)
  let added = 0
  while (added < days) {
    d.setDate(d.getDate() + 1)
    const day = d.getDay()
    if (day !== 0 && day !== 6) added++
  }
  return d
}

const deliveryEstimate = computed(() => {
  if (!order.value) return null
  if (['CANCELLED', 'DELIVERED'].includes(order.value.status)) return null
  if (!activeQuote.value || activeQuote.value.quote_status !== 'ACCEPTED') return null

  const range = DELIVERY_RANGES[order.value.priority]
  if (!range) return null

  const depositEntry = history.value.find(h => ['DEPOSIT_PAID', 'FULLY_PAID'].includes(h.new_status))
  if (depositEntry) {
    const start = new Date(depositEntry.changed_at)
    return {
      type: 'range' as const,
      from: formatDate(addWorkingDays(start, range.min).toISOString()),
      to: formatDate(addWorkingDays(start, range.max).toISOString()),
    }
  }

  return { type: 'pending' as const, label: range.label }
})

async function reload() {
  const [orderData, quotesData, paymentsData, historyData, filesData] = await Promise.all([
    getOrder(orderId),
    listOrderQuotes(orderId),
    listOrderPayments(orderId),
    listProductionHistory(orderId),
    listOrderFiles(orderId),
  ])
  order.value = orderData
  activeQuote.value = quotesData.results[0] ?? null
  payments.value = paymentsData.results
  history.value = historyData.results
  files.value = filesData.results
}

onMounted(async () => {
  try {
    await reload()
  } catch {
    errorMessage.value = 'Error al cargar el pedido'
  } finally {
    loading.value = false
  }
})

async function handleAccept(option: 'DEPOSIT' | 'FULL_PAYMENT') {
  if (!activeQuote.value) return
  accepting.value = true
  try {
    await acceptQuote(activeQuote.value.id, option)
    toast.show('Cotización aceptada. Ya puedes realizar tu pago.')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al aceptar la cotización'
  } finally {
    accepting.value = false
  }
}

async function handleReject() {
  if (!activeQuote.value) return
  rejecting.value = true
  try {
    await rejectQuote(activeQuote.value.id, rejectReason.value)
    showRejectModal.value = false
    toast.show('Cotización rechazada.', 'info')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al rechazar la cotización'
  } finally {
    rejecting.value = false
  }
}

async function handleCancel() {
  cancelling.value = true
  try {
    await cancelOrder(orderId, cancelReason.value)
    showCancelModal.value = false
    toast.show('Pedido cancelado.', 'info')
    router.push('/orders')
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al cancelar el pedido'
    showCancelModal.value = false
  } finally {
    cancelling.value = false
  }
}

async function handleDownloadPDF() {
  if (!activeQuote.value) return
  downloadingPDF.value = true
  try {
    const shortId = activeQuote.value.id.split('-')[0]
    await downloadQuotePDF(activeQuote.value.id, `cotizacion-${shortId}.pdf`)
  } catch {
    errorMessage.value = 'Error al descargar el PDF. Intenta de nuevo.'
  } finally {
    downloadingPDF.value = false
  }
}

async function handleAddFile(event: Event) {
  const input = event.target as HTMLInputElement
  const fileList = input.files
  if (!fileList || !order.value) return
  const fileType = order.value.request_type === 'REFERENCE' ? 'REFERENCE' : 'PRINTABLE_FILE'
  uploadingFile.value = true
  try {
    await Promise.all(Array.from(fileList).map(f => uploadOrderFile(orderId, f, fileType)))
    toast.show('Archivo(s) agregado(s) correctamente.')
    files.value = (await listOrderFiles(orderId)).results
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al subir el archivo'
  } finally {
    uploadingFile.value = false
    if (addFileInput.value) addFileInput.value.value = ''
  }
}

async function handleProofUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file || !pendingPayment.value) return

  const MAX_SIZE = 10 * 1024 * 1024 // 10 MB
  if (file.size > MAX_SIZE) {
    errorMessage.value = 'El archivo no puede superar los 10 MB.'
    return
  }

  uploadingProof.value = true
  try {
    await uploadPaymentProof(pendingPayment.value.id, file)
    toast.show('Comprobante enviado. El administrador lo revisará pronto.')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al subir el comprobante'
  } finally {
    uploadingProof.value = false
  }
}
</script>
