<template>
  <div class="p-6 max-w-5xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-white">Códigos de descuento</h1>
        <p class="text-gray-400 text-sm mt-0.5">Programa de lealtad y cupones</p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-colors"
      >
        + Nuevo código
      </button>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-16 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="codes.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">🎟️</div>
      <p class="text-gray-400">No hay códigos de descuento registrados</p>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="code in codes"
        :key="code.id"
        class="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 flex items-center gap-4"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-white font-mono font-semibold text-sm">{{ code.code }}</span>
            <span
              :class="[
                'px-2 py-0.5 rounded text-xs font-medium',
                code.is_active ? 'bg-green-900/50 text-green-300' : 'bg-gray-700 text-gray-500',
              ]"
            >
              {{ code.is_active ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
          <p class="text-gray-400 text-xs mt-0.5">
            {{ code.discount_type === 'PERCENTAGE' ? `${code.discount_value}%` : `$${code.discount_value} MXN` }}
            <span v-if="Number(code.min_order_amount) > 0" class="text-gray-500"> · Min ${{ code.min_order_amount }}</span>
            <span class="text-gray-500"> · Usos: {{ code.current_uses }}{{ code.max_uses ? `/${code.max_uses}` : '' }}</span>
            <span v-if="code.valid_until" class="text-gray-500"> · Hasta {{ formatDate(code.valid_until) }}</span>
          </p>
        </div>
        <div class="flex gap-1.5 shrink-0">
          <button
            class="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
            @click="openEditModal(code)"
          >
            Editar
          </button>
          <button
            class="px-2 py-1 rounded text-xs bg-red-900/50 text-red-300 hover:bg-red-900 transition-colors"
            @click="handleDeactivate(code.id)"
          >
            Desactivar
          </button>
        </div>
      </div>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />

    <!-- Modal: crear/editar -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      @keydown.esc="showModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold text-white mb-4">{{ editingId ? 'Editar' : 'Nuevo' }} código</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs text-gray-400 mb-1">Código</label>
            <div class="flex gap-2">
              <input
                v-model="modalForm.code"
                class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 uppercase focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="VERANO2026"
              />
              <button
                type="button"
                class="px-3 py-2 bg-gray-700 rounded-lg text-xs text-gray-300 hover:bg-gray-600 transition-colors"
                @click="generateCode"
              >
                Generar
              </button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-400 mb-1">Tipo</label>
              <select v-model="modalForm.discount_type" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
                <option value="PERCENTAGE">Porcentaje (%)</option>
                <option value="FIXED_AMOUNT">Monto fijo ($)</option>
              </select>
            </div>
            <AppInput v-model="modalForm.discount_value" :label="modalForm.discount_type === 'PERCENTAGE' ? 'Porcentaje (%)' : 'Monto ($)'" type="number" />
          </div>
          <AppInput v-model="modalForm.min_order_amount" label="Monto mínimo de pedido ($)" type="number" />
          <AppInput v-model="modalForm.max_uses" label="Máximo de usos (vacío = ilimitado)" type="number" />
          <div class="grid grid-cols-2 gap-3">
            <AppInput v-model="modalForm.valid_from" label="Válido desde" type="datetime-local" />
            <AppInput v-model="modalForm.valid_until" label="Válido hasta (opcional)" type="datetime-local" />
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="modalForm.is_active" class="rounded border-gray-600 bg-gray-800 text-blue-500" />
            <span class="text-sm text-gray-300">Activo</span>
          </label>
        </div>
        <div class="flex gap-2 mt-5">
          <AppButton variant="ghost" class="flex-1" @click="showModal = false">Cancelar</AppButton>
          <AppButton class="flex-1" :loading="saving" @click="handleSave">{{ editingId ? 'Guardar' : 'Crear' }}</AppButton>
        </div>
        <p v-if="modalError" class="text-red-400 text-xs mt-2">{{ modalError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import {
  listDiscountCodes, createDiscountCode, updateDiscountCode, deleteDiscountCode,
} from '../services/adminService'
import type { DiscountCode } from '../services/adminService'
import { formatDate } from '@/utils/formatters'

const codes = ref<DiscountCode[]>([])
const loading = ref(true)
const errorMessage = ref('')
const showModal = ref(false)
const saving = ref(false)
const modalError = ref('')
const editingId = ref<string | null>(null)

const modalForm = reactive({
  code: '',
  discount_type: 'PERCENTAGE' as string,
  discount_value: '',
  min_order_amount: '0',
  max_uses: '' as string,
  valid_from: '',
  valid_until: '',
  is_active: true,
})

function resetForm() {
  modalForm.code = ''
  modalForm.discount_type = 'PERCENTAGE'
  modalForm.discount_value = ''
  modalForm.min_order_amount = '0'
  modalForm.max_uses = ''
  modalForm.valid_from = new Date().toISOString().slice(0, 16)
  modalForm.valid_until = ''
  modalForm.is_active = true
  editingId.value = null
  modalError.value = ''
}

function generateCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < 8; i++) code += chars[Math.floor(Math.random() * chars.length)]
  modalForm.code = code
}

function openCreateModal() {
  resetForm()
  showModal.value = true
}

function openEditModal(code: DiscountCode) {
  editingId.value = code.id
  modalForm.code = code.code
  modalForm.discount_type = code.discount_type
  modalForm.discount_value = code.discount_value
  modalForm.min_order_amount = code.min_order_amount
  modalForm.max_uses = code.max_uses?.toString() ?? ''
  modalForm.valid_from = code.valid_from.slice(0, 16)
  modalForm.valid_until = code.valid_until?.slice(0, 16) ?? ''
  modalForm.is_active = code.is_active
  modalError.value = ''
  showModal.value = true
}

async function loadCodes() {
  loading.value = true
  try {
    const res = await listDiscountCodes()
    codes.value = res.results
  } catch {
    errorMessage.value = 'Error al cargar los códigos'
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!modalForm.code.trim() || !modalForm.discount_value) {
    modalError.value = 'Código y valor son obligatorios.'
    return
  }
  saving.value = true
  modalError.value = ''
  const payload = {
    code: modalForm.code,
    discount_type: modalForm.discount_type,
    discount_value: modalForm.discount_value,
    min_order_amount: modalForm.min_order_amount || '0',
    max_uses: modalForm.max_uses ? Number(modalForm.max_uses) : null,
    valid_from: new Date(modalForm.valid_from).toISOString(),
    valid_until: modalForm.valid_until ? new Date(modalForm.valid_until).toISOString() : null,
    is_active: modalForm.is_active,
  }
  try {
    if (editingId.value) {
      await updateDiscountCode(editingId.value, payload)
    } else {
      await createDiscountCode(payload)
    }
    showModal.value = false
    await loadCodes()
  } catch (err: any) {
    modalError.value = err.response?.data?.message ?? 'Error al guardar'
  } finally {
    saving.value = false
  }
}

async function handleDeactivate(id: string) {
  try {
    await deleteDiscountCode(id)
    await loadCodes()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al desactivar'
  }
}

onMounted(loadCodes)
</script>
