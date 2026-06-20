<template>
  <div class="p-6 max-w-5xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-white">Pedidos</h1>
        <p class="text-gray-400 text-sm mt-0.5">Gestión de todos los pedidos</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="handleExportCSV"
          class="px-4 py-2 rounded-lg bg-gray-700 text-gray-200 text-sm font-medium hover:bg-gray-600 transition-colors"
        >
          Exportar CSV
        </button>
        <RouterLink to="/admin/orders/new" class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-colors">
          + Nuevo pedido
        </RouterLink>
      </div>
    </div>

    <!-- Filtros -->
    <div class="flex gap-2 mb-4 flex-wrap">
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
      <div v-for="i in 5" :key="i" class="h-16 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="orders.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">📭</div>
      <p class="text-gray-400">No hay pedidos con este filtro</p>
    </div>

    <div v-else class="space-y-2">
      <RouterLink
        v-for="order in orders"
        :key="order.id"
        :to="`/admin/orders/${order.id}`"
        class="flex items-center gap-4 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 hover:border-gray-600 transition-colors group"
      >
        <div class="flex-1 min-w-0">
          <p class="text-gray-100 text-sm font-medium group-hover:text-white truncate">{{ order.title }}</p>
          <div class="flex items-center gap-2 mt-0.5">
            <p class="text-gray-500 text-xs">{{ formatDateTime(order.created_at) }}</p>
            <span v-if="order.customer_phone" class="text-gray-600 text-xs">·</span>
            <p v-if="order.customer_phone" class="text-gray-500 text-xs font-mono">{{ order.customer_phone }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <span :class="['text-xs px-2 py-0.5 rounded font-medium', priorityClass(order.priority)]">
            {{ PRIORITY_LABELS[order.priority] }}
          </span>
          <StatusBadge :status="order.status" />
          <svg class="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </RouterLink>
    </div>

    <!-- Paginación -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4 text-sm text-gray-400">
      <AppButton size="sm" variant="ghost" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
        ← Anterior
      </AppButton>
      <span>Página {{ currentPage }} de {{ totalPages }}</span>
      <AppButton size="sm" variant="ghost" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Siguiente →
      </AppButton>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppAlert from '@/components/ui/AppAlert.vue'
import AppButton from '@/components/ui/AppButton.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { listAdminOrders, exportOrdersCSV } from '../services/adminService'
import { formatDateTime, PRIORITY_LABELS } from '@/utils/formatters'
import type { AdminOrderSummary } from '@/types'

const route = useRoute()
const router = useRouter()
const orders = ref<AdminOrderSummary[]>([])
const loading = ref(true)
const errorMessage = ref('')
const activeFilter = ref(String(route.query.status ?? ''))
const currentPage = ref(1)
const totalPages = ref(1)
const PAGE_SIZE = 20

const statusFilters = [
  { value: '', label: 'Todos' },
  { value: 'RECEIVED', label: 'Recibidos' },
  { value: 'PENDING_ANALYSIS', label: 'Por analizar' },
  { value: 'QUOTED', label: 'Cotizados' },
  { value: 'PENDING_DEPOSIT', label: 'Anticipo pendiente' },
  { value: 'PRINTING', label: 'En impresión' },
  { value: 'READY', label: 'Listos' },
  { value: 'DELIVERED', label: 'Entregados' },
  { value: 'CANCELLED', label: 'Cancelados' },
]

function priorityClass(priority: string) {
  return {
    NORMAL: 'bg-gray-700 text-gray-300',
    URGENT: 'bg-orange-900/50 text-orange-300',
    EXPRESS: 'bg-red-900/50 text-red-300',
  }[priority] ?? 'bg-gray-700 text-gray-300'
}

function setFilter(value: string) {
  activeFilter.value = value
  router.replace({ query: value ? { status: value } : {} })
}

async function loadOrders(page = 1) {
  loading.value = true
  errorMessage.value = ''
  try {
    const params: Record<string, string> = {
      page: String(page),
      page_size: String(PAGE_SIZE),
    }
    if (activeFilter.value) params.status = activeFilter.value
    const result = await listAdminOrders(params)
    orders.value = result.results
    totalPages.value = result.num_pages ?? 1
    currentPage.value = page
  } catch {
    errorMessage.value = 'Error al cargar los pedidos'
  } finally {
    loading.value = false
  }
}

async function goToPage(page: number) {
  await loadOrders(page)
}

async function handleExportCSV() {
  const params: Record<string, string> = {}
  if (activeFilter.value) params.status = activeFilter.value
  try {
    await exportOrdersCSV(params)
  } catch {
    errorMessage.value = 'Error al exportar CSV'
  }
}

watch(activeFilter, () => loadOrders(1))
onMounted(() => loadOrders(1))
</script>
