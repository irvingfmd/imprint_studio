<template>
  <div class="flex items-center gap-1 text-xs">
    <button
      v-for="opt in options"
      :key="opt.value"
      :class="[
        'px-1.5 py-0.5 rounded transition-colors',
        locale === opt.value
          ? 'bg-gray-700 text-white'
          : 'text-gray-500 hover:text-gray-300',
      ]"
      @click="setLocale(opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const options = [
  { value: 'es', label: 'ES' },
  { value: 'en', label: 'EN' },
]

function setLocale(value: string) {
  locale.value = value
  localStorage.setItem('locale', value)
}
</script>
