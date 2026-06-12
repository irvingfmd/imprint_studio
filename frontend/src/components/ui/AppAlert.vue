<template>
  <div v-if="message" :class="['rounded-lg px-4 py-3 text-sm flex items-start gap-2', variantClass]">
    <span class="shrink-0 mt-0.5">{{ icon }}</span>
    <span>{{ message }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  message?: string
  variant?: 'error' | 'success' | 'warning' | 'info'
}>(), { variant: 'error' })

const variantClass = computed(() => ({
  error: 'bg-red-900/40 border border-red-700 text-red-300',
  success: 'bg-green-900/40 border border-green-700 text-green-300',
  warning: 'bg-yellow-900/40 border border-yellow-700 text-yellow-300',
  info: 'bg-blue-900/40 border border-blue-700 text-blue-300',
}[props.variant]))

const icon = computed(() => ({ error: '✕', success: '✓', warning: '⚠', info: 'ℹ' }[props.variant]))
</script>
