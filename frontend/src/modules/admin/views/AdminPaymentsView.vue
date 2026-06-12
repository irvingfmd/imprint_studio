<template>
  <div class="p-6 max-w-4xl">
    <div class="mb-6">
      <h1 class="text-xl font-semibold text-white">Pagos</h1>
      <p class="text-gray-400 text-sm mt-0.5">Confirmación y gestión de pagos</p>
    </div>

    <!-- Filtro por estado -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="opt in statusFilters"
        :key="opt.value"
        :class="[
          'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
          activeFilter === opt.value
            ? 'bg-blue-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700',
        ]"
        @click="setFilter(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-20 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="payments.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">💳</div>
      <p class="text-gray-400">No hay pagos con este filtro</p>
    </div>

    <div v-else class="space-y-3">
      <AppCard v-for="payment in payments" :key="payment.id">
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-gray-100 font-medium text-sm">{{ PAYMENT_TYPE_LABELS[payment.payment_type] }}</span>
              <StatusBadge :status="payment.payment_status" type="payment" />
            </div>
            <p class="text-2xl font-semibold text-white">{{ formatMXN(payment.amount) }}</p>
            <p class="text-gray-500 text-xs mt-1">{{ formatDateTime(payment.created_at) }}</p>
            <p v-if="payment.notes" class="text-gray-400 text-xs mt-1">{{ payment.notes }}</p>
          </div>
          <div v-if="payment.payment_status === 'PENDING'" class="flex flex-col gap-2">
            <AppButton size="sm" :loading="confirming === payment.id" @click="handleConfirm(payment.id)">
              ✓ Confirmar
            </AppButton>
            <AppButton size="sm" variant="danger" :loading="rejecting === payment.id" @click="openRejectModal(payment.id)">
              ✕ Rechazar
            </AppButton>
          </div>
        </div>
        <p v-if="payment.proof_file_url" class="mt-2 text-xs text-blue-400">
          <a :href="payment.proof_file_url" target="_blank">Ver comprobante →</a>
        </p>
      </AppCard>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />

    <!-- Modal: rechazar pago -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold text-white mb-3">Rechazar pago</h3>
        <AppInput v-model="rejectReason" label="Motivo" placeholder="¿Por qué se rechaza?" />
        <div class="flex gap-2 mt-4">
          <AppButton variant="ghost" class="flex-1" @click="showRejectModal = false">Cancelar</AppButton>
          <AppButton variant="danger" class="flex-1" :loading="rejecting !== null" @click="handleReject">Rechazar</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { listAdminPayments, confirmPayment, rejectPayment } from '../services/adminService'
import { formatMXN, formatDateTime, PAYMENT_TYPE_LABELS } from '@/utils/formatters'
import type { Payment } from '@/types'

const payments = ref<Payment[]>([])
const loading = ref(true)
const errorMessage = ref('')
const activeFilter = ref('PENDING')
const confirming = ref<string | null>(null)
const rejecting = ref<string | null>(null)
const showRejectModal = ref(false)
const rejectReason = ref('')
const rejectTargetId = ref<string | null>(null)

const statusFilters = [
  { value: 'PENDING', label: 'Pendientes' },
  { value: 'CONFIRMED', label: 'Confirmados' },
  { value: 'REJECTED', label: 'Rechazados' },
  { value: '', label: 'Todos' },
]

function setFilter(value: string) {
  activeFilter.value = value
}

async function loadPayments() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params: Record<string, string> = {}
    if (activeFilter.value) params.payment_status = activeFilter.value
    const result = await listAdminPayments(params)
    payments.value = result.results
  } catch {
    errorMessage.value = 'Error al cargar los pagos'
  } finally {
    loading.value = false
  }
}

async function handleConfirm(paymentId: string) {
  confirming.value = paymentId
  try {
    await confirmPayment(paymentId)
    await loadPayments()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al confirmar'
  } finally {
    confirming.value = null
  }
}

function openRejectModal(paymentId: string) {
  rejectTargetId.value = paymentId
  rejectReason.value = ''
  showRejectModal.value = true
}

async function handleReject() {
  if (!rejectTargetId.value) return
  rejecting.value = rejectTargetId.value
  try {
    await rejectPayment(rejectTargetId.value, rejectReason.value)
    showRejectModal.value = false
    await loadPayments()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al rechazar'
  } finally {
    rejecting.value = null
  }
}

watch(activeFilter, loadPayments)
onMounted(loadPayments)
</script>
