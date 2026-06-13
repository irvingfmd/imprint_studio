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
        <StatusBadge :status="order.status" />
      </div>

      <!-- Cambiar estado -->
      <AppCard class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Cambiar estado</h3>
        <div v-if="availableTransitions.length > 0" class="space-y-3">
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
          </div>
          <AppInput v-model="statusNotes" placeholder="Notas (opcional)" />
          <AppButton size="sm" :loading="updatingStatus" :disabled="!selectedStatus" @click="handleStatusChange">
            Actualizar estado
          </AppButton>
        </div>
        <p v-else class="text-gray-500 text-sm">No hay transiciones disponibles para este estado.</p>
      </AppCard>

      <!-- Crear cotización -->
      <AppCard v-if="canCreateQuote" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Crear cotización</h3>
        <p class="text-xs text-gray-500 mb-3">Ingresa los datos reales de Bambu Studio:</p>
        <div class="grid grid-cols-2 gap-3">
          <AppInput v-model="quoteForm.weight_grams" label="Peso (gramos)" type="number" placeholder="250" />
          <AppInput v-model="quoteForm.print_time_hours" label="Tiempo de impresión (horas)" type="number" placeholder="12.5" />
          <AppInput v-model="quoteForm.shipping_cost" label="Costo de envío (MXN)" type="number" placeholder="0" />
        </div>
        <div v-if="quotePreview" class="mt-3 p-3 bg-gray-900/50 rounded-lg text-sm">
          <div class="flex justify-between text-gray-400 mb-1">
            <span>Precio total estimado:</span>
            <span class="text-white font-semibold">{{ formatMXN(quotePreview.total_price) }}</span>
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
          <div v-for="entry in history" :key="entry.id" class="flex items-center gap-3 text-sm">
            <div class="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0" />
            <div class="flex-1">
              <span class="text-gray-300">{{ ORDER_STATUS_LABELS[entry.new_status] }}</span>
              <span v-if="entry.notes" class="text-gray-500 ml-1">— {{ entry.notes }}</span>
            </div>
            <span class="text-gray-600 text-xs">{{ formatDate(entry.changed_at) }}</span>
          </div>
        </div>
      </AppCard>

      <!-- Envío (solo si delivery_method = SHIPPING) -->
      <template v-if="order.delivery_method === 'SHIPPING'">
        <!-- Sin envío creado aún -->
        <AppCard v-if="!order.shipment" class="mb-4">
          <h3 class="text-sm font-medium text-gray-400 mb-3">Crear envío</h3>
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

        <!-- Envío creado, pendiente de entrega -->
        <AppCard v-else-if="!order.shipment.delivered_at" class="mb-4">
          <h3 class="text-sm font-medium text-gray-400 mb-2">Envío registrado</h3>
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

        <!-- Envío entregado -->
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
    <div v-if="showCancelModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold text-white mb-3">Cancelar pedido</h3>
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
import { formatMXN, formatDate, formatDateTime, ORDER_STATUS_LABELS } from '@/utils/formatters'
import type { Order, ProductionHistoryEntry } from '@/types'

const route = useRoute()
const router = useRouter()
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
const quotePreview = ref<any>(null)
const quoteForm = ref({ weight_grams: '', print_time_hours: '', shipping_cost: '0' })
const creatingShipment = ref(false)
const markingDelivered = ref(false)
const shipmentForm = ref({ carrier_name: '', tracking_number: '', shipping_cost: '0', shipping_notes: '' })

// Transiciones válidas por estado según status-flow.md
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
  FULLY_PAID: ['DELIVERED'],
}

const CANCELLABLE_FROM_ADMIN = ['RECEIVED', 'PENDING_ANALYSIS', 'QUOTED', 'APPROVED', 'PENDING_DEPOSIT']
const QUOTE_ELIGIBLE = ['RECEIVED', 'PENDING_ANALYSIS']

const availableTransitions = computed(() => {
  if (!order.value) return []
  return (VALID_TRANSITIONS[order.value.status] ?? []).map(s => ({
    value: s,
    label: ORDER_STATUS_LABELS[s] ?? s,
  }))
})

const canCancelAdmin = computed(() =>
  order.value && CANCELLABLE_FROM_ADMIN.includes(order.value.status)
)

const canCreateQuote = computed(() =>
  order.value && QUOTE_ELIGIBLE.includes(order.value.status)
)

onMounted(async () => {
  try {
    const [orderData, historyData] = await Promise.all([
      getAdminOrder(orderId),
      listProductionHistory(orderId),
    ])
    order.value = orderData
    history.value = historyData.results
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
    router.go(0)
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
    router.push('/admin/orders')
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al cancelar'
  } finally {
    cancelling.value = false
  }
}

async function handleCalculate() {
  if (!quoteForm.value.weight_grams || !quoteForm.value.print_time_hours) return
  calculating.value = true
  errorMessage.value = ''
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
    router.go(0)
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
    router.go(0)
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
    router.go(0)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al marcar como entregado'
  } finally {
    markingDelivered.value = false
  }
}
</script>
