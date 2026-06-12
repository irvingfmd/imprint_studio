<template>
  <div>
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-300 mb-1.5">
      {{ label }}
    </label>
    <input
      :id="inputId"
      v-bind="$attrs"
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="[
        'w-full rounded-lg bg-gray-800 border text-gray-100 placeholder-gray-500',
        'px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
        'disabled:opacity-50 disabled:cursor-not-allowed transition-colors',
        error ? 'border-red-500' : 'border-gray-700 focus:border-blue-500',
      ]"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="mt-1 text-xs text-red-400">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { useId } from 'vue'

withDefaults(defineProps<{
  modelValue?: string | number
  label?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}>(), {
  type: 'text',
})

defineEmits<{ 'update:modelValue': [value: string] }>()

const inputId = useId()
</script>
