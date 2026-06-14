<template>
  <div class="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['pointer-events-auto flex items-center gap-2 px-4 py-3 rounded-xl text-sm shadow-xl border max-w-xs', variantClass(toast.variant)]"
      >
        <span class="shrink-0 font-bold">{{ icon(toast.variant) }}</span>
        <span>{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts } = useToast()

function variantClass(v: string) {
  return {
    success: 'bg-green-900/95 border-green-700 text-green-200',
    error: 'bg-red-900/95 border-red-700 text-red-200',
    info: 'bg-blue-900/95 border-blue-700 text-blue-200',
  }[v] ?? 'bg-gray-800 border-gray-700 text-gray-200'
}

function icon(v: string) {
  return { success: '✓', error: '✕', info: 'ℹ' }[v] ?? '•'
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(110%);
}
</style>
