<template>
  <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', colorClass]">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ORDER_STATUS_LABELS, PAYMENT_STATUS_LABELS } from '@/utils/formatters'
import type { OrderStatus, PaymentStatus } from '@/types'

const props = defineProps<{
  status: OrderStatus | PaymentStatus | string
  type?: 'order' | 'payment'
}>()

const label = computed(() => {
  if (props.type === 'payment') return PAYMENT_STATUS_LABELS[props.status] ?? props.status
  return ORDER_STATUS_LABELS[props.status] ?? props.status
})

const PAYMENT_COLORS: Record<string, string> = {
  PENDING: 'bg-yellow-900/50 text-yellow-300',
  CONFIRMED: 'bg-green-900/50 text-green-300',
  REJECTED: 'bg-red-900/50 text-red-300',
}

const ORDER_COLORS: Record<string, string> = {
  RECEIVED: 'bg-gray-700 text-gray-300',
  PENDING_ANALYSIS: 'bg-blue-900/50 text-blue-300',
  QUOTED: 'bg-yellow-900/50 text-yellow-300',
  APPROVED: 'bg-cyan-900/50 text-cyan-300',
  PENDING_DEPOSIT: 'bg-orange-900/50 text-orange-300',
  DEPOSIT_PAID: 'bg-lime-900/50 text-lime-300',
  PRINTING: 'bg-purple-900/50 text-purple-300',
  POST_PROCESSING: 'bg-indigo-900/50 text-indigo-300',
  READY: 'bg-teal-900/50 text-teal-300',
  PENDING_BALANCE: 'bg-orange-900/50 text-orange-300',
  FULLY_PAID: 'bg-green-900/50 text-green-300',
  DELIVERED: 'bg-emerald-900/50 text-emerald-300',
  CANCELLED: 'bg-red-900/50 text-red-300',
}

const colorClass = computed(() => {
  const map = props.type === 'payment' ? PAYMENT_COLORS : ORDER_COLORS
  return map[props.status] ?? 'bg-gray-700 text-gray-300'
})
</script>
