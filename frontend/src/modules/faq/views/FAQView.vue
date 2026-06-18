<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFAQs, type FAQ } from '../services/faqService'

const faqs = ref<FAQ[]>([])
const loading = ref(true)
const expandedId = ref<string | null>(null)

function toggle(id: string) {
  expandedId.value = expandedId.value === id ? null : id
}

onMounted(async () => {
  try {
    faqs.value = await getFAQs()
  } catch {
    // silencioso — se muestra estado vacío
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <div class="max-w-3xl mx-auto px-4 py-12">
      <!-- Header -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 mb-4">
          <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 class="text-2xl font-semibold">Preguntas Frecuentes</h1>
        <p class="text-gray-400 text-sm mt-1">Todo lo que necesitas saber sobre nuestro servicio de impresión 3D</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center text-gray-400 py-12">
        Cargando...
      </div>

      <!-- Estado vacío -->
      <div v-else-if="faqs.length === 0" class="text-center text-gray-500 py-12">
        <p>No hay preguntas frecuentes disponibles en este momento.</p>
      </div>

      <!-- Lista de FAQs -->
      <div v-else class="space-y-3">
        <div
          v-for="faq in faqs"
          :key="faq.id"
          class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden"
        >
          <button
            class="w-full text-left px-5 py-4 flex items-center justify-between gap-3 hover:bg-gray-750 transition-colors cursor-pointer"
            @click="toggle(faq.id)"
          >
            <span class="font-medium text-sm">{{ faq.question }}</span>
            <svg
              class="w-5 h-5 text-gray-400 shrink-0 transition-transform duration-200"
              :class="{ 'rotate-180': expandedId === faq.id }"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <div
            v-if="expandedId === faq.id"
            class="px-5 pb-4 text-gray-300 text-sm whitespace-pre-line border-t border-gray-700 pt-3"
          >
            {{ faq.answer }}
          </div>
        </div>
      </div>

      <!-- Link de regreso -->
      <div class="text-center mt-10">
        <router-link to="/login" class="text-blue-400 hover:text-blue-300 text-sm">
          ← Volver al inicio
        </router-link>
      </div>
    </div>
  </div>
</template>
