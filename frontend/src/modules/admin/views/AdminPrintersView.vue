<template>
  <div class="p-6 max-w-3xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-white">Impresoras</h1>
        <p class="text-gray-400 text-sm mt-0.5">Catálogo de impresoras 3D disponibles</p>
      </div>
      <AppButton size="sm" @click="openCreate">+ Nueva impresora</AppButton>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-16 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <template v-else>
      <AppCard v-if="printers.length === 0" class="text-center text-gray-500 py-8">
        No hay impresoras registradas.
      </AppCard>

      <div v-else class="space-y-2">
        <div
          v-for="p in printers"
          :key="p.id"
          class="flex items-center gap-4 bg-gray-800 rounded-xl px-4 py-3 border border-gray-700"
        >
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ p.brand ? `${p.brand} ${p.name}` : p.name }}</p>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ p.power_watts }}W promedio
              <span v-if="p.max_power_watts"> · {{ p.max_power_watts }}W máx. técnico</span>
            </p>
          </div>
          <span
            :class="p.is_active ? 'text-green-400 bg-green-400/10 border-green-800' : 'text-gray-500 bg-gray-700/30 border-gray-700'"
            class="text-xs px-2 py-0.5 rounded-full border shrink-0"
          >
            {{ p.is_active ? 'Activa' : 'Inactiva' }}
          </span>
          <div class="flex gap-1.5 shrink-0">
            <button class="text-xs text-blue-400 hover:text-blue-300 px-2 py-1" @click="openEdit(p)">Editar</button>
            <button class="text-xs text-red-400 hover:text-red-300 px-2 py-1" @click="confirmDelete(p)">Eliminar</button>
          </div>
        </div>
      </div>
    </template>

    <AppAlert :message="errorMessage" class="mt-4" />

    <!-- Modal: crear / editar -->
    <div
      v-if="showForm"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      role="dialog"
      aria-modal="true"
      @keydown.esc="showForm = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold text-white mb-4">{{ editingId ? 'Editar' : 'Nueva' }} impresora</h3>
        <div class="space-y-3">
          <AppInput v-model="form.name" label="Nombre del modelo" placeholder="Ej: X1 Carbon" :error="formErrors.name" />
          <AppInput v-model="form.brand" label="Marca" placeholder="Ej: Bambu Lab" />
          <AppInput v-model="form.power_watts" label="Potencia promedio (W)" type="number" placeholder="350" :error="formErrors.power_watts" />
          <AppInput v-model="form.max_power_watts" label="Potencia máxima técnica (W)" type="number" placeholder="1000 (opcional)" />
          <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="rounded" />
            Activa
          </label>
        </div>
        <div class="flex gap-2 mt-5">
          <AppButton variant="ghost" class="flex-1" @click="showForm = false">Cancelar</AppButton>
          <AppButton class="flex-1" :loading="saving" @click="handleSave">
            {{ editingId ? 'Guardar' : 'Crear' }}
          </AppButton>
        </div>
      </div>
    </div>

    <!-- Modal: confirmar eliminar -->
    <div
      v-if="deletingPrinter"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      role="dialog"
      aria-modal="true"
      @keydown.esc="deletingPrinter = null"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold text-white mb-2">Eliminar impresora</h3>
        <p class="text-sm text-gray-400 mb-4">
          ¿Eliminar <strong class="text-white">{{ deletingPrinter.brand ? `${deletingPrinter.brand} ${deletingPrinter.name}` : deletingPrinter.name }}</strong>?
          Esta acción no se puede deshacer.
        </p>
        <div class="flex gap-2">
          <AppButton variant="ghost" class="flex-1" @click="deletingPrinter = null">Cancelar</AppButton>
          <AppButton variant="danger" class="flex-1" :loading="deleting" @click="handleDelete">Eliminar</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { listPrinters, createPrinter, updatePrinter, deletePrinter } from '../services/adminService'
import { useToast } from '@/composables/useToast'
import type { Printer } from '@/types'

const toast = useToast()

const printers = ref<Printer[]>([])
const loading = ref(true)
const errorMessage = ref('')
const showForm = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editingId = ref<string | null>(null)
const deletingPrinter = ref<Printer | null>(null)

const form = ref({ name: '', brand: '', power_watts: '', max_power_watts: '', is_active: true })
const formErrors = ref<Record<string, string>>({})

async function load() {
  printers.value = await listPrinters()
}

onMounted(async () => {
  try {
    await load()
  } catch {
    errorMessage.value = 'Error al cargar las impresoras'
  } finally {
    loading.value = false
  }
})

function openCreate() {
  editingId.value = null
  form.value = { name: '', brand: '', power_watts: '', max_power_watts: '', is_active: true }
  formErrors.value = {}
  showForm.value = true
}

function openEdit(p: Printer) {
  editingId.value = p.id
  form.value = {
    name: p.name,
    brand: p.brand,
    power_watts: String(p.power_watts),
    max_power_watts: p.max_power_watts != null ? String(p.max_power_watts) : '',
    is_active: p.is_active,
  }
  formErrors.value = {}
  showForm.value = true
}

function confirmDelete(p: Printer) {
  deletingPrinter.value = p
}

function validate(): boolean {
  formErrors.value = {}
  if (!form.value.name.trim()) formErrors.value.name = 'Requerido'
  const watts = Number(form.value.power_watts)
  if (!form.value.power_watts || watts <= 0) formErrors.value.power_watts = 'Debe ser mayor a 0'
  return Object.keys(formErrors.value).length === 0
}

async function handleSave() {
  if (!validate()) return
  saving.value = true
  errorMessage.value = ''
  try {
    const payload = {
      name: form.value.name.trim(),
      brand: form.value.brand.trim(),
      power_watts: Number(form.value.power_watts),
      max_power_watts: form.value.max_power_watts ? Number(form.value.max_power_watts) : null,
      is_active: form.value.is_active,
    }
    if (editingId.value) {
      await updatePrinter(editingId.value, payload)
      toast.show('Impresora actualizada.')
    } else {
      await createPrinter(payload)
      toast.show('Impresora creada.')
    }
    showForm.value = false
    await load()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al guardar'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!deletingPrinter.value) return
  deleting.value = true
  errorMessage.value = ''
  try {
    await deletePrinter(deletingPrinter.value.id)
    toast.show('Impresora eliminada.', 'info')
    deletingPrinter.value = null
    await load()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al eliminar'
    deletingPrinter.value = null
  } finally {
    deleting.value = false
  }
}
</script>
