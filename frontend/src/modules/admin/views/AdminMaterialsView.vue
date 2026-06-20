<template>
  <div class="p-6 max-w-5xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-semibold text-white">Materiales</h1>
        <p class="text-gray-400 text-sm mt-0.5">Catálogo de filamentos y resinas con inventario</p>
      </div>
      <div class="flex gap-2">
        <button
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
            showLowStock ? 'bg-red-600 text-white' : 'bg-gray-800 text-gray-400 border border-gray-700 hover:text-gray-200',
          ]"
          @click="showLowStock = !showLowStock"
        >
          Stock bajo
        </button>
        <button
          class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-colors"
          @click="openCreateModal"
        >
          + Nuevo material
        </button>
      </div>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-20 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="materials.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">🧪</div>
      <p class="text-gray-400">No hay materiales registrados</p>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="m in materials"
        :key="m.id"
        :class="[
          'bg-gray-800 border rounded-xl px-4 py-3',
          isLowStock(m) ? 'border-red-700/50' : 'border-gray-700',
        ]"
      >
        <div class="flex items-center gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <p class="text-gray-100 text-sm font-medium">{{ m.brand ? `${m.brand} ${m.name}` : m.name }}</p>
              <span class="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-300">{{ m.material_type }}</span>
              <span v-if="!m.is_active" class="text-xs px-1.5 py-0.5 rounded bg-gray-600 text-gray-400">Inactivo</span>
            </div>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span
                v-for="color in m.available_colors"
                :key="color"
                class="text-xs px-2 py-0.5 rounded-full bg-gray-700 text-gray-300"
              >{{ color }}</span>
              <span v-if="m.available_colors.length === 0" class="text-xs text-gray-600">Sin colores</span>
            </div>
          </div>

          <div class="text-right shrink-0 space-y-0.5">
            <p class="text-sm text-gray-300">${{ m.price_per_kg }}/kg</p>
            <p :class="['text-xs font-medium', isLowStock(m) ? 'text-red-400' : 'text-gray-500']">
              {{ Number(m.stock_grams).toLocaleString() }}g
              <span v-if="isLowStock(m)" class="ml-1">⚠️</span>
            </p>
          </div>

          <div class="flex gap-1 shrink-0">
            <button class="px-2 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600" @click="openStockModal(m)">Stock</button>
            <button class="px-2 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600" @click="openEditModal(m)">Editar</button>
          </div>
        </div>
      </div>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />

    <!-- Modal: crear/editar material -->
    <div
      v-if="showFormModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      @keydown.esc="showFormModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold text-white mb-4">{{ editingMaterial ? 'Editar material' : 'Nuevo material' }}</h3>
        <div class="space-y-3">
          <AppInput v-model="form.name" label="Nombre" placeholder="Ej: PLA+" />
          <div>
            <label class="block text-xs text-gray-400 mb-1">Tipo</label>
            <select v-model="form.material_type" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option v-for="t in materialTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
          <AppInput v-model="form.brand" label="Marca (opcional)" placeholder="Ej: eSUN" />
          <AppInput v-model="form.price_per_kg" label="Precio por kg (MXN)" type="number" placeholder="350" />
          <div class="grid grid-cols-2 gap-3">
            <AppInput v-model="form.stock_grams" label="Stock actual (g)" type="number" placeholder="1000" />
            <AppInput v-model="form.min_stock_grams" label="Stock mínimo (g)" type="number" placeholder="500" />
          </div>
          <div>
            <label class="block text-xs text-gray-400 mb-1">Colores disponibles (separados por coma)</label>
            <input
              v-model="colorsInput"
              placeholder="Negro, Blanco, Rojo, Azul"
              class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="form.is_active" class="rounded border-gray-600 bg-gray-800 text-blue-500" />
            <span class="text-sm text-gray-300">Activo</span>
          </label>
        </div>
        <AppAlert :message="formError" class="mt-3" />
        <div class="flex gap-2 mt-4">
          <AppButton variant="ghost" class="flex-1" @click="showFormModal = false">Cancelar</AppButton>
          <AppButton class="flex-1" :loading="saving" @click="handleSave">{{ editingMaterial ? 'Guardar' : 'Crear' }}</AppButton>
        </div>
      </div>
    </div>

    <!-- Modal: ajustar stock -->
    <div
      v-if="showStockModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4"
      @keydown.esc="showStockModal = false"
    >
      <div class="bg-gray-800 rounded-2xl border border-gray-700 p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold text-white mb-2">Ajustar stock</h3>
        <p class="text-sm text-gray-400 mb-4">{{ stockMaterial?.brand }} {{ stockMaterial?.name }} — {{ Number(stockMaterial?.stock_grams).toLocaleString() }}g actuales</p>
        <div class="space-y-3">
          <div class="flex gap-2">
            <button
              v-for="op in [{ value: 'add', label: '+ Agregar' }, { value: 'deduct', label: '- Descontar' }]"
              :key="op.value"
              :class="[
                'flex-1 py-2 rounded-lg text-sm font-medium border transition-colors',
                stockOperation === op.value
                  ? 'border-blue-500 bg-blue-600/10 text-blue-300'
                  : 'border-gray-700 text-gray-400 hover:border-gray-600',
              ]"
              @click="stockOperation = op.value as 'add' | 'deduct'"
            >{{ op.label }}</button>
          </div>
          <AppInput v-model="stockGrams" label="Gramos" type="number" placeholder="500" />
        </div>
        <AppAlert :message="stockError" class="mt-3" />
        <div class="flex gap-2 mt-4">
          <AppButton variant="ghost" class="flex-1" @click="showStockModal = false">Cancelar</AppButton>
          <AppButton class="flex-1" :loading="adjustingStock" @click="handleAdjustStock">Aplicar</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { listMaterials, createMaterial, updateMaterial, adjustStock } from '../services/adminService'
import type { Material } from '@/types'

const materials = ref<Material[]>([])
const loading = ref(true)
const errorMessage = ref('')
const showLowStock = ref(false)

const showFormModal = ref(false)
const editingMaterial = ref<Material | null>(null)
const saving = ref(false)
const formError = ref('')
const colorsInput = ref('')
const form = ref({
  name: '',
  material_type: 'PLA',
  brand: '',
  price_per_kg: '',
  stock_grams: '0',
  min_stock_grams: '500',
  is_active: true,
})

const showStockModal = ref(false)
const stockMaterial = ref<Material | null>(null)
const stockOperation = ref<'add' | 'deduct'>('add')
const stockGrams = ref('')
const adjustingStock = ref(false)
const stockError = ref('')

const materialTypes = [
  { value: 'PLA', label: 'PLA' },
  { value: 'PETG', label: 'PETG' },
  { value: 'ABS', label: 'ABS' },
  { value: 'TPU', label: 'TPU' },
  { value: 'RESIN', label: 'Resina' },
  { value: 'OTHER', label: 'Otro' },
]

function isLowStock(m: Material): boolean {
  return Number(m.stock_grams) < Number(m.min_stock_grams)
}

function openCreateModal() {
  editingMaterial.value = null
  form.value = { name: '', material_type: 'PLA', brand: '', price_per_kg: '', stock_grams: '0', min_stock_grams: '500', is_active: true }
  colorsInput.value = ''
  formError.value = ''
  showFormModal.value = true
}

function openEditModal(m: Material) {
  editingMaterial.value = m
  form.value = {
    name: m.name,
    material_type: m.material_type,
    brand: m.brand,
    price_per_kg: m.price_per_kg,
    stock_grams: m.stock_grams,
    min_stock_grams: m.min_stock_grams,
    is_active: m.is_active,
  }
  colorsInput.value = m.available_colors.join(', ')
  formError.value = ''
  showFormModal.value = true
}

function openStockModal(m: Material) {
  stockMaterial.value = m
  stockOperation.value = 'add'
  stockGrams.value = ''
  stockError.value = ''
  showStockModal.value = true
}

async function loadMaterials() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await listMaterials({ low_stock: showLowStock.value })
    materials.value = res.results
  } catch {
    errorMessage.value = 'Error al cargar materiales'
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  formError.value = ''
  if (!form.value.name.trim()) { formError.value = 'El nombre es obligatorio'; return }
  if (!form.value.price_per_kg || Number(form.value.price_per_kg) <= 0) { formError.value = 'El precio debe ser mayor a 0'; return }

  const colors = colorsInput.value.split(',').map(c => c.trim()).filter(Boolean)
  const payload = { ...form.value, available_colors: colors }

  saving.value = true
  try {
    if (editingMaterial.value) {
      await updateMaterial(editingMaterial.value.id, payload)
    } else {
      await createMaterial(payload)
    }
    showFormModal.value = false
    await loadMaterials()
  } catch (err: any) {
    formError.value = err.response?.data?.message ?? 'Error al guardar'
  } finally {
    saving.value = false
  }
}

async function handleAdjustStock() {
  stockError.value = ''
  if (!stockGrams.value || Number(stockGrams.value) <= 0) { stockError.value = 'Los gramos deben ser mayor a 0'; return }
  if (!stockMaterial.value) return

  adjustingStock.value = true
  try {
    await adjustStock(stockMaterial.value.id, stockGrams.value, stockOperation.value)
    showStockModal.value = false
    await loadMaterials()
  } catch (err: any) {
    stockError.value = err.response?.data?.message ?? 'Error al ajustar stock'
  } finally {
    adjustingStock.value = false
  }
}

watch(showLowStock, () => loadMaterials())
onMounted(() => loadMaterials())
</script>
