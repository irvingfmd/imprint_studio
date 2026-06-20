<template>
  <div class="min-h-screen bg-gray-950 flex items-center justify-center p-6">
    <div class="w-full max-w-lg">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-white">Cotización exprés</h1>
        <p class="text-gray-400 text-sm mt-1">Sube tu archivo STL y obtén un estimado al instante</p>
      </div>

      <!-- Drag & drop / upload -->
      <div
        v-if="!result"
        :class="[
          'border-2 border-dashed rounded-2xl p-10 text-center transition-colors cursor-pointer',
          dragging ? 'border-blue-500 bg-blue-600/10' : 'border-gray-700 hover:border-gray-600',
        ]"
        @click="fileInput?.click()"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="handleDrop"
      >
        <input type="file" accept=".stl" class="hidden" ref="fileInput" @change="handleFileSelected" />
        <div v-if="loading" class="space-y-3">
          <div class="inline-block w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p class="text-gray-400 text-sm">Analizando archivo...</p>
        </div>
        <div v-else>
          <div class="text-4xl mb-3">📐</div>
          <p class="text-gray-300 font-medium">Arrastra tu archivo STL aquí</p>
          <p class="text-gray-500 text-sm mt-1">o haz clic para seleccionarlo</p>
          <p class="text-gray-600 text-xs mt-3">Máximo 20 MB · Solo formato STL binario</p>
        </div>
      </div>

      <!-- Error -->
      <div v-if="errorMessage" class="mt-4 p-3 rounded-lg bg-red-900/30 border border-red-800 text-red-300 text-sm">
        {{ errorMessage }}
      </div>

      <!-- Resultado -->
      <div v-if="result" class="space-y-4">
        <div class="bg-gray-800 border border-gray-700 rounded-2xl p-6">
          <h2 class="text-sm font-medium text-gray-400 mb-4">Estimado de impresión</h2>

          <div class="grid grid-cols-3 gap-4 mb-5">
            <div class="text-center">
              <p class="text-xs text-gray-500">Peso</p>
              <p class="text-white font-semibold text-lg">{{ result.weight_grams }}g</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500">Tiempo</p>
              <p class="text-white font-semibold text-lg">{{ result.print_time_hours }}h</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500">Volumen</p>
              <p class="text-white font-semibold text-lg">{{ Number(result.volume_cm3).toFixed(1) }}cm³</p>
            </div>
          </div>

          <div class="space-y-2 text-sm">
            <div class="flex justify-between text-gray-400">
              <span>Material</span><span class="text-gray-300">{{ formatMXN(result.material_cost) }}</span>
            </div>
            <div class="flex justify-between text-gray-400">
              <span>Energía</span><span class="text-gray-300">{{ formatMXN(result.energy_cost) }}</span>
            </div>
            <div class="flex justify-between text-gray-400">
              <span>Mano de obra</span><span class="text-gray-300">{{ formatMXN(result.labor_cost) }}</span>
            </div>
            <div v-if="Number(result.post_processing_cost) > 0" class="flex justify-between text-gray-400">
              <span>Post-procesado</span><span class="text-gray-300">{{ formatMXN(result.post_processing_cost) }}</span>
            </div>
            <div v-if="Number(result.tax_amount) > 0" class="flex justify-between text-gray-400">
              <span>IVA</span><span class="text-gray-300">{{ formatMXN(result.tax_amount) }}</span>
            </div>
            <div class="flex justify-between font-semibold text-white pt-2 border-t border-gray-600 text-base">
              <span>Total estimado</span><span>{{ formatMXN(result.total_price) }}</span>
            </div>
          </div>
        </div>

        <div class="rounded-lg border border-yellow-700/50 bg-yellow-900/20 px-4 py-3 text-xs text-yellow-300">
          Este es un estimado basado en PLA con relleno estándar. El precio final puede variar según color, material y acabado.
        </div>

        <div class="flex gap-3">
          <button
            @click="reset"
            class="flex-1 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-gray-300 text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            Cotizar otro archivo
          </button>
          <RouterLink
            to="/register"
            class="flex-1 px-4 py-3 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-colors text-center"
          >
            Crear cuenta para pedir
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/services/api'
import { formatMXN } from '@/utils/formatters'

const fileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const dragging = ref(false)
const errorMessage = ref('')
const result = ref<Record<string, any> | null>(null)

function reset() {
  result.value = null
  errorMessage.value = ''
}

function handleDrop(e: DragEvent) {
  dragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) upload(file)
}

function handleFileSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) upload(file)
  if (fileInput.value) fileInput.value.value = ''
}

async function upload(file: File) {
  errorMessage.value = ''
  result.value = null

  if (!file.name.toLowerCase().endsWith('.stl')) {
    errorMessage.value = 'Solo se aceptan archivos STL.'
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    errorMessage.value = 'El archivo no puede superar los 20 MB.'
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/quotes/estimate/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    result.value = data.data
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al analizar el archivo.'
  } finally {
    loading.value = false
  }
}
</script>
