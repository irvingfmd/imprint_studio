<template>
  <div class="p-6 max-w-4xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-white">Mis pedidos</h1>
        <p class="text-gray-400 text-sm mt-0.5">Historial de tus solicitudes de impresión</p>
      </div>
      <RouterLink to="/orders/new">
        <AppButton>+ Nuevo pedido</AppButton>
      </RouterLink>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-20 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="orders.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">📦</div>
      <p class="text-gray-300 font-medium">No tienes pedidos aún</p>
      <p class="text-gray-500 text-sm mt-1">Crea tu primer pedido de impresión 3D</p>
      <RouterLink to="/orders/new" class="inline-block mt-4">
        <AppButton>Crear pedido</AppButton>
      </RouterLink>
    </div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="order in orders"
        :key="order.id"
        :to="`/orders/${order.id}`"
        class="block bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-gray-600 transition-colors group"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <p class="text-gray-100 font-medium group-hover:text-white transition-colors truncate">{{ order.title }}</p>
            <p class="text-gray-500 text-xs mt-1">{{ formatDateTime(order.created_at) }}</p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <span :class="['text-xs px-2 py-0.5 rounded-md font-medium', priorityClass(order.priority)]">
              {{ PRIORITY_LABELS[order.priority] }}
            </span>
            <StatusBadge :status="order.status" />
          </div>
        </div>
      </RouterLink>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { listOrders } from '../services/orderService'
import { formatDateTime, PRIORITY_LABELS } from '@/utils/formatters'
import type { OrderSummary } from '@/types'

const orders = ref<OrderSummary[]>([])
const loading = ref(true)
const errorMessage = ref('')

function priorityClass(priority: string) {
  return {
    NORMAL: 'bg-gray-700 text-gray-300',
    URGENT: 'bg-orange-900/50 text-orange-300',
    EXPRESS: 'bg-red-900/50 text-red-300',
  }[priority] ?? 'bg-gray-700 text-gray-300'
}

onMounted(async () => {
  try {
    const result = await listOrders()
    orders.value = result.results
  } catch {
    errorMessage.value = 'Error al cargar los pedidos'
  } finally {
    loading.value = false
  }
})
</script>
