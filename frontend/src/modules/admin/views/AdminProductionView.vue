<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-white">Producción</h1>
        <p class="text-gray-400 text-sm mt-0.5">Vista de pedidos en producción</p>
      </div>
      <span class="text-xs text-gray-600">Auto-refresh cada 60s</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="col in columns" :key="col.status" class="flex flex-col min-h-[300px]">
        <!-- Header -->
        <div class="flex items-center justify-between px-3 py-2 rounded-t-xl" :class="col.headerClass">
          <span class="text-sm font-medium">{{ col.label }}</span>
          <span class="text-xs px-1.5 py-0.5 rounded-full bg-black/20">
            {{ col.loading ? '…' : col.orders.length }}
          </span>
        </div>

        <!-- Contenido -->
        <div class="flex-1 bg-gray-800/50 border border-gray-700 border-t-0 rounded-b-xl p-2 space-y-2 overflow-y-auto max-h-[70vh]">
          <!-- Skeleton -->
          <template v-if="col.loading">
            <div v-for="i in 3" :key="i" class="h-20 bg-gray-800 rounded-lg animate-pulse" />
          </template>

          <!-- Vacío -->
          <p v-else-if="col.orders.length === 0" class="text-center text-gray-600 text-xs py-8">
            Sin pedidos
          </p>

          <!-- Tarjetas -->
          <RouterLink
            v-else
            v-for="order in col.orders"
            :key="order.id"
            :to="`/admin/orders/${order.id}`"
            class="block bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 hover:border-gray-500 transition-colors cursor-pointer"
          >
            <p class="text-sm text-gray-200 font-medium truncate">{{ order.title }}</p>
            <div class="flex items-center gap-2 mt-1.5">
              <span :class="['text-[10px] px-1.5 py-0.5 rounded font-medium', priorityClass(order.priority)]">
                {{ PRIORITY_LABELS[order.priority] }}
              </span>
              <span class="text-[10px] text-gray-500 font-mono">{{ order.customer_phone }}</span>
            </div>
            <p class="text-[10px] text-gray-600 mt-1">{{ formatDateTime(order.created_at) }}</p>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { listAdminOrders } from '../services/adminService'
import { formatDateTime, PRIORITY_LABELS } from '@/utils/formatters'
import type { AdminOrderSummary } from '@/types'

interface KanbanColumn {
  status: string
  label: string
  headerClass: string
  orders: AdminOrderSummary[]
  loading: boolean
}

const columns = reactive<KanbanColumn[]>([
  { status: 'DEPOSIT_PAID', label: 'Depósito pagado', headerClass: 'bg-blue-900/60 text-blue-300', orders: [], loading: true },
  { status: 'PRINTING', label: 'En impresión', headerClass: 'bg-yellow-900/60 text-yellow-300', orders: [], loading: true },
  { status: 'POST_PROCESSING', label: 'Post-procesado', headerClass: 'bg-purple-900/60 text-purple-300', orders: [], loading: true },
  { status: 'READY', label: 'Listo', headerClass: 'bg-green-900/60 text-green-300', orders: [], loading: true },
])

function priorityClass(priority: string): string {
  return ({
    NORMAL: 'bg-gray-700 text-gray-300',
    URGENT: 'bg-orange-900/50 text-orange-300',
    EXPRESS: 'bg-red-900/50 text-red-300',
  } as Record<string, string>)[priority] ?? 'bg-gray-700 text-gray-300'
}

async function loadAll() {
  await Promise.all(columns.map(async (col) => {
    try {
      const res = await listAdminOrders({ status: col.status, page_size: '50' })
      col.orders = res.results
    } catch {
      col.orders = []
    } finally {
      col.loading = false
    }
  }))
}

let intervalId: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadAll()
  intervalId = setInterval(loadAll, 60_000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>
