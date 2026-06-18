<template>
  <div class="p-6 max-w-6xl">
    <div class="mb-6">
      <h1 class="text-xl font-semibold text-white">Dashboard</h1>
      <p class="text-gray-400 text-sm mt-0.5">Resumen operativo del negocio</p>
    </div>

    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="h-28 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <template v-else-if="data">
      <!-- Cards de resumen -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <template v-for="metric in metrics" :key="metric.label">
          <RouterLink
            v-if="metric.to"
            :to="metric.to"
            class="block bg-gray-800 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition-colors"
          >
            <div class="flex items-center justify-between mb-3">
              <span class="text-2xl">{{ metric.icon }}</span>
              <div :class="['w-2 h-2 rounded-full', metric.color]" />
            </div>
            <p class="text-2xl font-semibold text-white">{{ metric.value }}</p>
            <p class="text-gray-400 text-sm mt-0.5">{{ metric.label }}</p>
          </RouterLink>
          <div v-else class="bg-gray-800 border border-gray-700 rounded-xl p-5">
            <div class="flex items-center justify-between mb-3">
              <span class="text-2xl">{{ metric.icon }}</span>
              <div :class="['w-2 h-2 rounded-full', metric.color]" />
            </div>
            <p class="text-2xl font-semibold text-white">{{ metric.value }}</p>
            <p class="text-gray-400 text-sm mt-0.5">{{ metric.label }}</p>
            <p v-if="metric.sub" class="text-xs mt-1" :class="metric.subColor ?? 'text-gray-500'">{{ metric.sub }}</p>
          </div>
        </template>
      </div>

      <!-- Ingresos por mes (barras horizontales) -->
      <div v-if="data.revenue_by_month.length" class="mt-8 bg-gray-800 border border-gray-700 rounded-xl p-5">
        <h2 class="text-sm font-medium text-gray-300 mb-4">Ingresos por mes</h2>
        <div class="space-y-3">
          <div v-for="item in data.revenue_by_month" :key="item.month" class="flex items-center gap-3">
            <span class="text-xs text-gray-400 w-16 shrink-0">{{ formatMonth(item.month) }}</span>
            <div class="flex-1 bg-gray-700 rounded-full h-5 overflow-hidden">
              <div
                class="bg-blue-500 h-full rounded-full transition-all duration-500"
                :style="{ width: barWidth(item.revenue) }"
              />
            </div>
            <span class="text-xs text-gray-300 w-24 text-right shrink-0">{{ formatMXN(item.revenue) }}</span>
          </div>
        </div>
      </div>

      <!-- Estadisticas y desglose -->
      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Tiempo promedio de entrega -->
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-2">Tiempo promedio de entrega</p>
          <p class="text-3xl font-semibold text-white">
            {{ data.avg_delivery_days !== null ? `${data.avg_delivery_days} d` : '—' }}
          </p>
          <p class="text-xs text-gray-500 mt-1">Pedidos entregados este mes</p>
        </div>

        <!-- Tipos de solicitud -->
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-3">Tipos de solicitud</p>
          <div v-if="data.request_type_counts.length" class="space-y-2">
            <div v-for="rt in data.request_type_counts" :key="rt.request_type" class="flex justify-between">
              <span class="text-sm text-gray-300">{{ REQUEST_TYPE_LABELS[rt.request_type] ?? rt.request_type }}</span>
              <span class="text-sm font-medium text-white">{{ rt.count }}</span>
            </div>
          </div>
          <p v-else class="text-sm text-gray-500">Sin pedidos este mes</p>
        </div>

        <!-- Pedidos por prioridad -->
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-3">Por prioridad</p>
          <div v-if="data.priority_counts.length" class="flex gap-3">
            <div
              v-for="pc in data.priority_counts"
              :key="pc.priority"
              :class="priorityBadgeClass(pc.priority)"
              class="flex-1 text-center rounded-lg py-2 px-1"
            >
              <p class="text-xl font-semibold">{{ pc.count }}</p>
              <p class="text-xs mt-0.5">{{ PRIORITY_LABELS[pc.priority] ?? pc.priority }}</p>
            </div>
          </div>
          <p v-else class="text-sm text-gray-500">Sin pedidos este mes</p>
        </div>
      </div>
    </template>

    <AppAlert :message="errorMessage" class="mt-4" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppAlert from '@/components/ui/AppAlert.vue'
import { getDashboard } from '../services/adminService'
import { formatMXN, REQUEST_TYPE_LABELS, PRIORITY_LABELS } from '@/utils/formatters'
import type { DashboardMetrics } from '@/types'

const data = ref<DashboardMetrics | null>(null)
const loading = ref(true)
const errorMessage = ref('')

const metrics = computed(() => {
  if (!data.value) return []
  const d = data.value

  const ordersDelta = d.orders_prev_month > 0
    ? Math.round((d.orders_this_month - d.orders_prev_month) / d.orders_prev_month * 100)
    : null

  return [
    { label: 'Pedidos pendientes', value: d.pending_orders, icon: '📋', color: 'bg-yellow-400', to: '/admin/orders?status=RECEIVED' },
    { label: 'Cotizados', value: d.quoted_orders, icon: '💬', color: 'bg-blue-400', to: '/admin/orders?status=QUOTED' },
    { label: 'En impresión', value: d.printing_orders, icon: '🖨️', color: 'bg-purple-400', to: '/admin/orders?status=PRINTING' },
    { label: 'Listos para entrega', value: d.ready_orders, icon: '✅', color: 'bg-teal-400', to: '/admin/orders?status=READY' },
    { label: 'Pagos pendientes', value: d.pending_payments, icon: '💳', color: 'bg-orange-400', to: '/admin/payments' },
    { label: 'Ingresos del mes', value: formatMXN(d.monthly_revenue), icon: '💰', color: 'bg-green-400', to: null },
    {
      label: 'Pedidos del mes',
      value: d.orders_this_month,
      icon: '📦',
      color: 'bg-blue-400',
      to: null,
      sub: ordersDelta !== null ? `${ordersDelta > 0 ? '+' : ''}${ordersDelta}% vs mes anterior` : null,
      subColor: ordersDelta !== null ? (ordersDelta >= 0 ? 'text-green-400' : 'text-red-400') : undefined,
    },
    {
      label: 'Tasa de cancelación',
      value: `${d.cancellation_rate}%`,
      icon: '🚫',
      color: d.cancellation_rate > 20 ? 'bg-red-400' : 'bg-gray-400',
      to: null,
    },
  ]
})

const maxRevenue = computed(() => {
  if (!data.value?.revenue_by_month.length) return 1
  return Math.max(...data.value.revenue_by_month.map(r => parseFloat(r.revenue)), 1)
})

function barWidth(revenue: string): string {
  const pct = (parseFloat(revenue) / maxRevenue.value) * 100
  return `${Math.max(pct, 2)}%`
}

function formatMonth(yyyymm: string): string {
  const [y, m] = yyyymm.split('-')
  const names = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  return `${names[parseInt(m) - 1]} ${y.slice(2)}`
}

function priorityBadgeClass(priority: string): string {
  const map: Record<string, string> = {
    NORMAL: 'bg-gray-700 text-gray-200',
    URGENT: 'bg-yellow-900/50 text-yellow-300',
    EXPRESS: 'bg-red-900/50 text-red-300',
  }
  return map[priority] ?? 'bg-gray-700 text-gray-200'
}

onMounted(async () => {
  try {
    data.value = await getDashboard()
  } catch {
    errorMessage.value = 'Error al cargar el dashboard'
  } finally {
    loading.value = false
  }
})
</script>
