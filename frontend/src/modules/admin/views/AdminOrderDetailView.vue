<template>
  <div class="p-6 max-w-3xl">
    <RouterLink to="/admin/orders" class="text-sm text-gray-400 hover:text-gray-200 flex items-center gap-1 mb-4 w-fit">
      ← Pedidos
    </RouterLink>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 4" :key="i" class="h-28 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <template v-else-if="order">
      <div class="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 class="text-xl font-semibold text-white">{{ order.title }}</h1>
          <p class="text-gray-400 text-sm mt-0.5">{{ formatDateTime(order.created_at) }}</p>
        </div>
        <div class="flex flex-col items-end gap-1.5">
          <StatusBadge :status="order.status" />
          <StatusBadge :status="order.payment_status" type="payment" />
        </div>
      </div>

      <!-- Detalles básicos -->
      <AppCard class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Detalles del pedido</h3>
        <dl class="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
          <div>
            <dt class="text-gray-500">Tipo</dt>
            <dd class="text-gray-200 mt-0.5">{{ REQUEST_TYPE_LABELS[order.request_type] }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Prioridad</dt>
            <dd class="text-gray-200 mt-0.5">{{ PRIORITY_LABELS[order.priority] ?? order.priority }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Entrega</dt>
            <dd class="text-gray-200 mt-0.5">{{ DELIVERY_METHOD_LABELS[order.delivery_method] }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Cantidad</dt>
            <dd class="text-gray-200 mt-0.5">{{ order.quantity }}</dd>
          </div>
          <div v-if="order.color">
            <dt class="text-gray-500">Color</dt>
            <dd class="text-gray-200 mt-0.5">{{ order.color }}</dd>
          </div>
        </dl>
      </AppCard>

      <!-- Cambiar estado -->
      <AppCard class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Cambiar estado</h3>
        <div v-if="availableTransitions.length > 0 || blockedDelivered" class="space-y-3">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="s in availableTransitions"
              :key="s.value"
              :class="[
                'px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                selectedStatus === s.value
                  ? 'border-blue-500 bg-blue-600/10 text-blue-300'
                  : 'border-gray-700 text-gray-400 hover:border-gray-600 hover:text-gray-200',
              ]"
              @click="selectedStatus = s.value"
            >
              {{ s.label }}
            </button>
            <!-- DELIVERED bloqueado: se muestra pero deshabilitado con explicación -->
            <div v-if="blockedDelivered" class="relative group">
              <button
                disabled
                class="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-800 text-gray-600 cursor-not-allowed"
              >
                Entregado
              </button>
              <div class="absolute bottom-full left-0 mb-1 w-52 text-xs bg-gray-900 border border-gray-700 text-gray-400 rounded-lg px-2 py-1.5 hidden group-hover:block z-10">
                Requiere pago completo. Mueve a "Pagado completo" primero.
              </div>
            </div>
          </div>
          <AppInput v-model="statusNotes" placeholder="Notas para el cliente (opcional)" />
          <AppButton size="sm" :loading="updatingStatus" :disabled="!selectedStatus" @click="handleStatusChange">
            Actualizar estado
          </AppButton>
        </div>
        <p v-else class="text-gray-500 text-sm">No hay transiciones disponibles desde el estado actual.</p>
      </AppCard>

      <!-- Crear cotización -->
      <AppCard v-if="canCreateQuote" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Crear cotización</h3>
        <p class="text-xs text-gray-500 mb-3">Ingresa los datos del archivo en Bambu Studio:</p>
        <div class="grid grid-cols-2 gap-3">
          <AppInput
            v-model="quoteForm.weight_grams"
            label="Peso (gramos)"
            type="number"
            placeholder="250"
            :error="quoteErrors.weight_grams"
          />
          <AppInput
            v-model="quoteForm.print_time_hours"
            label="Tiempo de impresión (horas)"
            type="number"
            placeholder="12.5"
            :error="quoteErrors.print_time_hours"
          />
          <AppInput
            v-model="quoteForm.shipping_cost"
            label="Costo de envío (MXN)"
            type="number"
            placeholder="0"
          />
        </div>

        <!-- Desglose detallado del cálculo -->
        <div v-if="quotePreview" class="mt-4 p-3 bg-gray-900/60 rounded-lg text-sm space-y-1.5 border border-gray-700">
          <p class="text-xs font-medium text-gray-400 mb-2">Desglose de costos:</p>
          <div class="flex justify-between text-gray-400">
            <span>Material</span><span class="text-gray-300">{{ formatMXN(quotePreview.material_cost) }}</span>
          </div>
          <div class="flex justify-between text-gray-400">
            <span>Energía</span><span class="text-gray-300">{{ formatMXN(quotePreview.energy_cost) }}</span>
          </div>
          <div class="flex justify-between text-gray-400">
            <span>Mano de obra</span><span class="text-gray-300">{{ formatMXN(quotePreview.labor_cost) }}</span>
          </div>
          <div v-if="Number(quotePreview.post_processing_cost) > 0" class="flex justify-between text-gray-400">
            <span>Post-procesado</span><span class="text-gray-300">{{ formatMXN(quotePreview.post_processing_cost) }}</span>
          </div>
          <div v-if="Number(quotePreview.packaging_cost) > 0" class="flex justify-between text-gray-400">
            <span>Empaque</span><span class="text-gray-300">{{ formatMXN(quotePreview.packaging_cost) }}</span>
          </div>
          <div v-if="Number(quotePreview.risk_cost) > 0" class="flex justify-between text-gray-400">
            <span>Riesgo</span><span class="text-gray-300">{{ formatMXN(quotePreview.risk_cost) }}</span>
          </div>
          <div v-if="Number(quotePreview.shipping_cost) > 0" class="flex justify-between text-gray-400">
            <span>Envío</span><span class="text-gray-300">{{ formatMXN(quotePreview.shipping_cost) }}</span>
          </div>
          <div class="flex justify-between text-gray-400 pt-1 border-t border-gray-700">
            <span>Subtotal + margen</span><span class="text-gray-300">{{ formatMXN(quotePreview.subtotal) }}</span>
          </div>
          <div class="flex justify-between font-semibold text-white pt-1 border-t border-gray-600">
            <span>Total estimado</span><span>{{ formatMXN(quotePreview.total_price) }}</span>
          </div>
        </div>

        <div class="flex gap-2 mt-3">
          <AppButton size="sm" variant="secondary" :loading="calculating" @click="handleCalculate">
            Calcular
          </AppButton>
          <AppButton size="sm" :loading="creatingQuote" :disabled="!quotePreview" @click="handleCreateQuote">
            Crear cotización
          </AppButton>
        </div>
      </AppCard>

      <!-- Historial de producción -->
      <AppCard v-if="history.length > 0" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Historial de estados</h3>
        <div class="space-y-2">
          <div v-for="entry in history" :key="entry.id" class="flex items-start gap-3 text-sm">
            <div class="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />
            <div class="flex-1">
              <span class="text-gray-300">{{ ORDER_STATUS_LABELS[entry.new_status] }}</span>
              <span v-if="entry.notes" class="text-gray-500 ml-1">— {{ entry.notes }}</span>
            </div>
            <span class="text-gray-600 text-xs shrink-0">{{ formatDate(entry.changed_at) }}</span>
          </div>
        </div>
      </AppCard>

      <!-- Envío (solo si delivery_method = SHIPPING) -->
      <template v-if="order.delivery_method === 'SHIPPING'">
        <AppCard v-if="!order.shipment" class="mb-4">
          <h3 class="text-sm font-medium text-gray-400 mb-3">Registrar envío</h3>
          <div class="grid grid-cols-2 gap-3">
            <AppInput v-model="shipmentForm.carrier_name" label="Paquetería" placeholder="Ej: FedEx, DHL" />
            <AppInput v-model="shipmentForm.tracking_number" label="Número de rastreo" placeholder="Ej: 123456789" />
            <AppInput v-model="shipmentForm.shipping_cost" label="Costo de envío (MXN)" type="number" placeholder="0" />
          </div>
          <AppInput v-model="shipmentForm.shipping_notes" label="Notas (opcional)" placeholder="Instrucciones especiales" class="mt-3" />
          <AppButton size="sm" class="mt-3" :loading="creatingShipment" @click="handleCreateShipment">
            Registrar envío
          </AppButton>
        </AppCard>

        <AppCard v-else-if="!order.shipment.delivered_at" class="mb-4">
          <h3 class="text-sm font-medium text-gray-400 mb-2">Envío en camino</h3>
          <div class="text-sm space-y-1">
            <p v-if="order.shipment.carrier_name" class="text-gray-300">
              Paquetería: <span class="text-white">{{ order.shipment.carrier_name }}</span>
            </p>
            <p v-if="order.shipment.tracking_number" class="text-gray-300">
              Rastreo: <span class="text-white font-mono">{{ order.shipment.tracking_number }}</span>
            </p>
            <p class="text-gray-300">
              Costo: <span class="text-white">{{ formatMXN(order.shipment.shipping_cost) }}</span>
            </p>
          </div>
          <AppButton size="sm" class="mt-3" :loading="markingDelivered" @click="handleMarkDelivered">
            Marcar como entregado
          </AppButton>
        </AppCard>

        <AppCard v-else class="mb-4">
          <h3 class="text-sm font-medium text-gray-400 mb-2">Envío entregado</h3>
          <div class="text-sm space-y-1">
            <p v-if="order.shipment.carrier_name" class="text-gray-300">
              Paquetería: <span class="text-white">{{ order.shipment.carrier_name }}</span>
            </p>
            <p v-if="order.shipment.tracking_number" class="text-gray-300">
              Rastreo: <span class="text-white font-mono">{{ order.shipment.tracking_number }}</span>
            </p>
            <p class="text-gray-300">
              Entregado: <span class="text-white">{{ formatDate(order.shipment.delivered_at!) }}</span>
            </p>
          </div>
        </AppCard>
      </template>

      <!-- Cancelar pedido (admin) -->
      <div v-if="canCancelAdmin" class="mt-4">
        <AppButton variant="danger" size="sm" @click="showCancelModal = true">
          Cancelar pedido
        </AppButton>
      </div>
    </template>

    <AppAlert :message="errorMessage" class="mt-4" />

    <!-- Modal: cancelar -->
    <div
      v-if="showCancelModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="admin-cancel-modal-title"
      @keydown.esc="showCancelModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 id="admin-cancel-modal-title" class="text-lg font-semibold text-white mb-2">Cancelar pedido</h3>
        <p class="text-xs text-gray-500 mb-3">El cliente será notificado del motivo.</p>
        <AppInput v-model="cancelReason" label="Motivo" placeholder="Motivo de cancelación" />
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
import {
  getAdminOrder, updateOrderStatus, cancelOrderAdmin,
  createQuote, calculateQuote, createShipment, markDelivered,
} from '../services/adminService'
import { listProductionHistory } from '@/modules/orders/services/orderService'
import { formatMXN, formatDate, formatDateTime, ORDER_STATUS_LABELS, PRIORITY_LABELS, REQUEST_TYPE_LABELS, DELIVERY_METHOD_LABELS } from '@/utils/formatters'
import { useToast } from '@/composables/useToast'
import type { Order, ProductionHistoryEntry, QuoteCalculation } from '@/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const orderId = String(route.params.id)

const order = ref<Order | null>(null)
const history = ref<ProductionHistoryEntry[]>([])
const loading = ref(true)
const errorMessage = ref('')
const selectedStatus = ref('')
const statusNotes = ref('')
const updatingStatus = ref(false)
const cancelling = ref(false)
const showCancelModal = ref(false)
const cancelReason = ref('')
const calculating = ref(false)
const creatingQuote = ref(false)
const quotePreview = ref<QuoteCalculation | null>(null)
const quoteErrors = ref<Record<string, string>>({})
const quoteForm = ref({ weight_grams: '', print_time_hours: '', shipping_cost: '0' })
const creatingShipment = ref(false)
const markingDelivered = ref(false)
const shipmentForm = ref({ carrier_name: '', tracking_number: '', shipping_cost: '0', shipping_notes: '' })

// Transiciones válidas según status-flow.md
const VALID_TRANSITIONS: Record<string, string[]> = {
  RECEIVED: ['QUOTED', 'CANCELLED'],
  PENDING_ANALYSIS: ['QUOTED', 'CANCELLED'],
  QUOTED: ['APPROVED', 'CANCELLED'],
  APPROVED: ['PENDING_DEPOSIT', 'FULLY_PAID', 'CANCELLED'],
  PENDING_DEPOSIT: ['DEPOSIT_PAID', 'CANCELLED'],
  DEPOSIT_PAID: ['PRINTING'],
  PRINTING: ['POST_PROCESSING'],
  POST_PROCESSING: ['READY'],
  READY: ['PENDING_BALANCE', 'FULLY_PAID', 'DELIVERED'],
  PENDING_BALANCE: ['FULLY_PAID'],
  FULLY_PAID: ['PRINTING', 'DELIVERED'],
}

const CANCELLABLE_FROM_ADMIN = ['RECEIVED', 'PENDING_ANALYSIS', 'QUOTED', 'APPROVED', 'PENDING_DEPOSIT']
const QUOTE_ELIGIBLE = ['RECEIVED', 'PENDING_ANALYSIS']

const availableTransitions = computed(() => {
  if (!order.value) return []
  return (VALID_TRANSITIONS[order.value.status] ?? [])
    .filter(s => s !== 'CANCELLED')
    // DELIVERED desde READY solo si ya está completamente pagado
    .filter(s => !(s === 'DELIVERED' && order.value!.payment_status !== 'FULLY_PAID'))
    .map(s => ({ value: s, label: ORDER_STATUS_LABELS[s] ?? s }))
})

const canCancelAdmin = computed(() =>
  order.value && CANCELLABLE_FROM_ADMIN.includes(order.value.status)
)

// DELIVERED aparece en READY o FULLY_PAID solo si el pago está completo.
// Cuando está bloqueado mostramos el botón deshabilitado con tooltip.
const blockedDelivered = computed(() => {
  if (!order.value) return false
  const hasDeliveredTransition = (VALID_TRANSITIONS[order.value.status] ?? []).includes('DELIVERED')
  return hasDeliveredTransition && order.value.payment_status !== 'FULLY_PAID'
})

const canCreateQuote = computed(() =>
  order.value && QUOTE_ELIGIBLE.includes(order.value.status)
)

async function reload() {
  const [orderData, historyData] = await Promise.all([
    getAdminOrder(orderId),
    listProductionHistory(orderId),
  ])
  order.value = orderData
  history.value = historyData.results
  selectedStatus.value = ''
  statusNotes.value = ''
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

async function handleStatusChange() {
  if (!selectedStatus.value) return
  updatingStatus.value = true
  errorMessage.value = ''
  try {
    await updateOrderStatus(orderId, selectedStatus.value, statusNotes.value)
    toast.show(`Estado actualizado a: ${ORDER_STATUS_LABELS[selectedStatus.value] ?? selectedStatus.value}`)
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al cambiar el estado'
  } finally {
    updatingStatus.value = false
  }
}

async function handleCancel() {
  cancelling.value = true
  try {
    await cancelOrderAdmin(orderId, cancelReason.value)
    showCancelModal.value = false
    toast.show('Pedido cancelado.', 'info')
    router.push('/admin/orders')
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al cancelar'
    showCancelModal.value = false
  } finally {
    cancelling.value = false
  }
}

function validateQuoteForm(): boolean {
  quoteErrors.value = {}
  const weight = Number(quoteForm.value.weight_grams)
  const hours = Number(quoteForm.value.print_time_hours)
  if (!quoteForm.value.weight_grams || weight <= 0) {
    quoteErrors.value.weight_grams = 'Debe ser mayor a 0'
  }
  if (!quoteForm.value.print_time_hours || hours <= 0) {
    quoteErrors.value.print_time_hours = 'Debe ser mayor a 0'
  }
  return Object.keys(quoteErrors.value).length === 0
}

async function handleCalculate() {
  if (!validateQuoteForm()) return
  calculating.value = true
  errorMessage.value = ''
  quotePreview.value = null
  try {
    const result = await calculateQuote({
      weight_grams: quoteForm.value.weight_grams,
      print_time_hours: quoteForm.value.print_time_hours,
      shipping_cost: quoteForm.value.shipping_cost,
      priority: order.value?.priority ?? 'NORMAL',
      payment_option: 'DEPOSIT',
    })
    quotePreview.value = result
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al calcular'
  } finally {
    calculating.value = false
  }
}

async function handleCreateQuote() {
  creatingQuote.value = true
  errorMessage.value = ''
  try {
    await createQuote(orderId, quoteForm.value)
    toast.show('Cotización creada y enviada al cliente.')
    quotePreview.value = null
    quoteForm.value = { weight_grams: '', print_time_hours: '', shipping_cost: '0' }
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al crear la cotización'
  } finally {
    creatingQuote.value = false
  }
}

async function handleCreateShipment() {
  creatingShipment.value = true
  errorMessage.value = ''
  try {
    await createShipment(orderId, shipmentForm.value)
    toast.show('Envío registrado correctamente.')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al registrar el envío'
  } finally {
    creatingShipment.value = false
  }
}

async function handleMarkDelivered() {
  if (!order.value?.shipment?.id) return
  markingDelivered.value = true
  errorMessage.value = ''
  try {
    await markDelivered(order.value.shipment.id)
    toast.show('Pedido marcado como entregado.')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al marcar como entregado'
  } finally {
    markingDelivered.value = false
  }
}
</script>
