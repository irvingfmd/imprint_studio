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

      <!-- Enlace de modelo web (WEB_MODEL) -->
      <AppCard v-if="order.request_type === 'WEB_MODEL'" class="mb-4 border-blue-800/50">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Modelos del cliente</h3>
        <div v-if="webModelFiles.length > 0" class="space-y-2">
          <div v-for="file in webModelFiles" :key="file.id" class="flex items-center gap-2">
            <span class="text-blue-400 shrink-0">🔗</span>
            <a
              :href="file.file_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-400 hover:underline text-sm truncate"
            >
              {{ file.original_filename || file.file_url }}
            </a>
            <span class="text-xs text-gray-600 ml-auto shrink-0">{{ file.file_url }}</span>
          </div>
        </div>
        <p v-else class="text-xs text-gray-500">El cliente aún no ha adjuntado un enlace.</p>
        <p class="mt-2 text-xs text-yellow-400/70">El costo de la licencia, si el modelo es de pago, corre por cuenta del cliente.</p>
      </AppCard>

      <!-- Archivos adjuntos (non-WEB_MODEL) -->
      <AppCard v-else-if="files.length > 0" class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Archivos adjuntos</h3>
        <ul class="space-y-1.5">
          <li v-for="file in files" :key="file.id" class="flex items-center gap-2 text-sm">
            <span class="text-gray-500">📎</span>
            <a :href="file.file_url" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:underline truncate">
              {{ file.original_filename }}
            </a>
            <span class="text-xs text-gray-600 shrink-0 uppercase">{{ file.file_type }}</span>
          </li>
        </ul>
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
          <div class="relative group/status inline-block">
            <AppButton size="sm" :loading="updatingStatus" :disabled="!selectedStatus" @click="handleStatusChange">
              Actualizar estado
            </AppButton>
            <div v-if="!selectedStatus" class="absolute bottom-full left-0 mb-1 w-52 text-xs bg-gray-900 border border-gray-700 text-gray-400 rounded-lg px-2 py-1.5 hidden group-hover/status:block z-10">
              Selecciona un estado arriba para continuar.
            </div>
          </div>
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
          <div>
            <label class="block text-xs text-gray-400 mb-1">Impresora (opcional)</label>
            <select
              v-model="quoteForm.printer_id"
              class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Sin impresora (energía = $0)</option>
              <option v-for="p in printers" :key="p.id" :value="p.id">
                {{ p.brand ? `${p.brand} ${p.name}` : p.name }} ({{ p.power_watts }}W)
              </option>
            </select>
          </div>
        </div>

        <label class="flex items-center gap-2 mt-3 cursor-pointer">
          <input type="checkbox" v-model="quoteForm.include_post_processing" class="rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-0" />
          <span class="text-sm text-gray-300">Incluir post-procesado</span>
          <span class="text-xs text-gray-500">(lijado, soportes, acabado)</span>
        </label>

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
          <div v-if="Number(quotePreview.tax_amount) > 0" class="flex justify-between text-gray-400">
            <span>IVA</span><span class="text-gray-300">{{ formatMXN(quotePreview.tax_amount) }}</span>
          </div>
          <div class="flex justify-between font-semibold text-white pt-1 border-t border-gray-600">
            <span>Total estimado</span><span>{{ formatMXN(quotePreview.total_price) }}</span>
          </div>
        </div>

        <div class="flex gap-2 mt-3">
          <AppButton size="sm" variant="secondary" :loading="calculating" @click="handleCalculate">
            Calcular
          </AppButton>
          <div class="relative group/quote inline-block">
            <AppButton size="sm" :loading="creatingQuote" :disabled="!quotePreview" @click="handleCreateQuote">
              Crear cotización
            </AppButton>
            <div v-if="!quotePreview" class="absolute bottom-full left-0 mb-1 w-56 text-xs bg-gray-900 border border-gray-700 text-gray-400 rounded-lg px-2 py-1.5 hidden group-hover/quote:block z-10">
              Primero haz clic en «Calcular» para ver el desglose.
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Cotización activa -->
      <AppCard v-if="activeQuote" class="mb-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-medium text-gray-400">Cotización activa</h3>
          <div class="flex items-center gap-2">
            <span :class="['px-2 py-0.5 rounded-full text-xs font-medium border', quoteStatusClass(activeQuote.quote_status)]">
              {{ QUOTE_STATUS_LABELS[activeQuote.quote_status] }}
            </span>
            <AppButton size="sm" variant="ghost" :loading="downloadingPDF" title="Descargar PDF" @click="handleDownloadPDF">
              📄 PDF
            </AppButton>
          </div>
        </div>

        <p class="text-2xl font-semibold text-white mb-3">{{ formatMXN(activeQuote.total_price) }}</p>

        <div class="space-y-1 text-sm">
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
          <div v-if="Number(activeQuote.tax_amount) > 0" class="flex justify-between text-gray-400 pt-1 border-t border-gray-700">
            <span>IVA</span><span class="text-gray-300">{{ formatMXN(activeQuote.tax_amount) }}</span>
          </div>
        </div>

        <p v-if="activeQuote.expires_at" class="mt-2 text-xs text-gray-500">
          {{ activeQuote.quote_status === 'PENDING' ? 'Expira' : 'Expiró' }}: {{ formatDate(activeQuote.expires_at) }}
        </p>

        <div v-if="activeQuote.quote_status === 'PENDING'" class="mt-3">
          <AppButton size="sm" variant="ghost" :loading="expiringQuote" @click="handleExpireQuote">
            Expirar cotización
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

      <!-- Notas internas (solo admin) -->
      <AppCard class="mb-4">
        <h3 class="text-sm font-medium text-gray-400 mb-3">Notas internas</h3>
        <div v-if="internalNotes.length > 0" class="space-y-3 mb-4">
          <div v-for="note in internalNotes" :key="note.id" class="text-sm border-l-2 border-gray-700 pl-3">
            <p class="text-gray-200 whitespace-pre-wrap">{{ note.content }}</p>
            <p class="text-gray-600 text-xs mt-1">{{ note.created_by_name || 'Sistema' }} · {{ formatDateTime(note.created_at) }}</p>
          </div>
        </div>
        <p v-else class="text-gray-500 text-xs mb-3">Sin notas internas.</p>
        <div class="flex gap-2">
          <textarea
            v-model="newNoteContent"
            rows="2"
            placeholder="Agregar nota interna..."
            class="flex-1 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
          <div class="relative group/note self-end">
            <AppButton size="sm" :loading="addingNote" :disabled="!newNoteContent.trim()" @click="handleAddNote">
              Agregar
            </AppButton>
            <div v-if="!newNoteContent.trim()" class="absolute bottom-full right-0 mb-1 w-44 text-xs bg-gray-900 border border-gray-700 text-gray-400 rounded-lg px-2 py-1.5 hidden group-hover/note:block z-10">
              Escribe una nota primero.
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Revertir / Cancelar pedido (admin) -->
      <div class="flex gap-2 mt-4">
        <AppButton v-if="canRevert" variant="secondary" size="sm" @click="showRevertModal = true">
          ← Revertir estado
        </AppButton>
        <AppButton v-if="canCancelAdmin" variant="danger" size="sm" @click="showCancelModal = true">
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

    <!-- Modal: revertir estado -->
    <div
      v-if="showRevertModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="admin-revert-modal-title"
      @keydown.esc="showRevertModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 id="admin-revert-modal-title" class="text-lg font-semibold text-white mb-2">Revertir estado</h3>
        <p class="text-xs text-gray-500 mb-3">El pedido regresará al estado anterior. Esto queda registrado en el historial.</p>
        <AppInput v-model="revertReason" label="Motivo" placeholder="¿Por qué reviertes el estado?" />
        <div class="flex gap-2 mt-4">
          <AppButton variant="ghost" class="flex-1" @click="showRevertModal = false">Cancelar</AppButton>
          <div class="relative group/revert flex-1">
            <AppButton variant="secondary" class="w-full" :loading="reverting" :disabled="!revertReason.trim()" @click="handleRevert">Revertir</AppButton>
            <div v-if="!revertReason.trim()" class="absolute bottom-full left-0 mb-1 w-48 text-xs bg-gray-900 border border-gray-700 text-gray-400 rounded-lg px-2 py-1.5 hidden group-hover/revert:block z-10">
              Escribe el motivo para continuar.
            </div>
          </div>
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
  getAdminOrder, updateOrderStatus, cancelOrderAdmin, revertOrderStatus,
  createQuote, calculateQuote, createShipment, markDelivered, expireQuote, listPrinters,
  listInternalNotes, createInternalNote,
} from '../services/adminService'
import type { InternalNote } from '../services/adminService'
import { listProductionHistory, listOrderFiles } from '@/modules/orders/services/orderService'
import { downloadQuotePDF } from '@/modules/quotes/services/quoteService'
import { formatMXN, formatDate, formatDateTime, ORDER_STATUS_LABELS, PRIORITY_LABELS, REQUEST_TYPE_LABELS, DELIVERY_METHOD_LABELS } from '@/utils/formatters'
import { useToast } from '@/composables/useToast'
import type { Order, ProductionHistoryEntry, QuoteCalculation, Quote, Printer } from '@/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const orderId = String(route.params.id)

const order = ref<Order | null>(null)
const history = ref<ProductionHistoryEntry[]>([])
const files = ref<any[]>([])
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
const quoteForm = ref({ weight_grams: '', print_time_hours: '', shipping_cost: '0', printer_id: '' as string | null, include_post_processing: true })
const printers = ref<Printer[]>([])
const creatingShipment = ref(false)
const markingDelivered = ref(false)
const shipmentForm = ref({ carrier_name: '', tracking_number: '', shipping_cost: '0', shipping_notes: '' })
const downloadingPDF = ref(false)
const expiringQuote = ref(false)
const showRevertModal = ref(false)
const revertReason = ref('')
const reverting = ref(false)
const internalNotes = ref<InternalNote[]>([])
const newNoteContent = ref('')
const addingNote = ref(false)

const activeQuote = computed((): Quote | null => order.value?.active_quote ?? null)
const webModelFiles = computed(() => files.value.filter((f: any) => f.file_type === 'WEB_MODEL'))

const QUOTE_STATUS_LABELS: Record<string, string> = {
  PENDING: 'Pendiente',
  ACCEPTED: 'Aceptada',
  REJECTED: 'Rechazada',
  EXPIRED: 'Expirada',
}

function quoteStatusClass(s: string): string {
  return ({
    PENDING: 'bg-yellow-600/20 text-yellow-300 border-yellow-700',
    ACCEPTED: 'bg-green-600/20 text-green-300 border-green-700',
    REJECTED: 'bg-red-600/20 text-red-300 border-red-700',
    EXPIRED: 'bg-gray-600/20 text-gray-400 border-gray-600',
  } as Record<string, string>)[s] ?? 'bg-gray-600/20 text-gray-400 border-gray-600'
}

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

const NON_REVERTIBLE = ['DELIVERED', 'CANCELLED']
const canRevert = computed(() =>
  order.value && !NON_REVERTIBLE.includes(order.value.status) && history.value.length > 0
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
  const [orderData, historyData, filesData, notesData] = await Promise.all([
    getAdminOrder(orderId),
    listProductionHistory(orderId),
    listOrderFiles(orderId),
    listInternalNotes(orderId),
  ])
  order.value = orderData
  history.value = historyData.results
  files.value = filesData.results
  internalNotes.value = notesData.results
  selectedStatus.value = ''
  statusNotes.value = ''
}

onMounted(async () => {
  try {
    const [, printersData] = await Promise.all([reload(), listPrinters(true)])
    printers.value = printersData
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

async function handleRevert() {
  if (!revertReason.value.trim()) return
  reverting.value = true
  errorMessage.value = ''
  try {
    await revertOrderStatus(orderId, revertReason.value)
    showRevertModal.value = false
    revertReason.value = ''
    toast.show('Estado revertido correctamente.')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al revertir el estado'
    showRevertModal.value = false
  } finally {
    reverting.value = false
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
      full_payment_selected: false,
      printer_id: quoteForm.value.printer_id || null,
      include_post_processing: quoteForm.value.include_post_processing,
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
    await createQuote(orderId, {
      weight_grams: quoteForm.value.weight_grams,
      print_time_hours: quoteForm.value.print_time_hours,
      shipping_cost: quoteForm.value.shipping_cost,
      printer_id: quoteForm.value.printer_id || null,
      include_post_processing: quoteForm.value.include_post_processing,
    })
    toast.show('Cotización creada y enviada al cliente.')
    quotePreview.value = null
    quoteForm.value = { weight_grams: '', print_time_hours: '', shipping_cost: '0', printer_id: '', include_post_processing: true }
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

async function handleAddNote() {
  if (!newNoteContent.value.trim()) return
  addingNote.value = true
  errorMessage.value = ''
  try {
    await createInternalNote(orderId, newNoteContent.value.trim())
    newNoteContent.value = ''
    toast.show('Nota agregada.')
    const notesData = await listInternalNotes(orderId)
    internalNotes.value = notesData.results
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al agregar la nota'
  } finally {
    addingNote.value = false
  }
}

async function handleExpireQuote() {
  if (!activeQuote.value) return
  expiringQuote.value = true
  errorMessage.value = ''
  try {
    await expireQuote(activeQuote.value.id)
    toast.show('Cotización expirada.')
    await reload()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al expirar la cotización'
  } finally {
    expiringQuote.value = false
  }
}
</script>
