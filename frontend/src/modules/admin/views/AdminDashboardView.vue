<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-xl font-semibold text-white">Dashboard</h1>
      <p class="text-gray-400 text-sm mt-0.5">Resumen operativo del negocio</p>
    </div>

    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="h-28 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-4">
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
        </div>
      </template>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppAlert from '@/components/ui/AppAlert.vue'
import { getDashboard } from '../services/adminService'
import { formatMXN } from '@/utils/formatters'
import type { DashboardMetrics } from '@/types'

const data = ref<DashboardMetrics | null>(null)
const loading = ref(true)
const errorMessage = ref('')

const metrics = computed(() => {
  if (!data.value) return []
  return [
    { label: 'Pedidos pendientes', value: data.value.pending_orders, icon: '📋', color: 'bg-yellow-400', to: '/admin/orders?status=RECEIVED' },
    { label: 'Cotizados', value: data.value.quoted_orders, icon: '💬', color: 'bg-blue-400', to: '/admin/orders?status=QUOTED' },
    { label: 'En impresión', value: data.value.printing_orders, icon: '🖨️', color: 'bg-purple-400', to: '/admin/orders?status=PRINTING' },
    { label: 'Listos para entrega', value: data.value.ready_orders, icon: '✅', color: 'bg-teal-400', to: '/admin/orders?status=READY' },
    { label: 'Pagos pendientes', value: data.value.pending_payments, icon: '💳', color: 'bg-orange-400', to: '/admin/payments' },
    { label: 'Ingresos del mes', value: formatMXN(data.value.monthly_revenue), icon: '💰', color: 'bg-green-400', to: null },
  ]
})

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
