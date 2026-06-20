<template>
  <div class="p-6 max-w-2xl">
    <div class="mb-6">
      <RouterLink to="/admin/orders" class="text-sm text-gray-400 hover:text-gray-200 flex items-center gap-1 mb-3 w-fit">
        ← Pedidos
      </RouterLink>
      <h1 class="text-xl font-semibold text-white">Crear pedido (admin)</h1>
      <p class="text-gray-400 text-sm mt-0.5">Crea un pedido a nombre de un cliente</p>
    </div>

    <form @submit.prevent="handleCreate" class="space-y-5">
      <!-- Selección de cliente -->
      <AppCard>
        <h3 class="text-sm font-medium text-gray-300 mb-4">Cliente</h3>
        <div class="space-y-3">
          <AppInput
            v-model="customerSearch"
            label="Buscar por teléfono"
            placeholder="Ej: 9611234567"
            :disabled="loading"
            @keyup="searchCustomers"
          />
          <div v-if="searching" class="text-xs text-gray-500">Buscando...</div>
          <div v-if="customerResults.length && !selectedCustomer" class="space-y-1">
            <button
              v-for="c in customerResults"
              :key="c.id"
              type="button"
              class="w-full text-left rounded-lg border border-gray-700 hover:border-blue-500 px-3 py-2 text-sm transition-colors"
              @click="selectCustomer(c)"
            >
              <span class="text-gray-200">{{ c.first_name }} {{ c.last_name }}</span>
              <span class="text-gray-500 ml-2">{{ c.phone }}</span>
            </button>
          </div>
          <div v-if="selectedCustomer" class="flex items-center gap-3 rounded-lg border border-blue-500/50 bg-blue-600/10 px-3 py-2">
            <div class="flex-1 text-sm">
              <span class="text-blue-300 font-medium">{{ selectedCustomer.first_name }} {{ selectedCustomer.last_name }}</span>
              <span class="text-gray-400 ml-2">{{ selectedCustomer.phone }}</span>
            </div>
            <button type="button" class="text-gray-400 hover:text-red-400 text-xs" @click="clearCustomer">Cambiar</button>
          </div>
          <p v-if="errors.customer_id" class="text-red-400 text-xs">{{ errors.customer_id }}</p>
        </div>
      </AppCard>

      <!-- Información del pedido -->
      <AppCard>
        <h3 class="text-sm font-medium text-gray-300 mb-4">Información del pedido</h3>
        <div class="space-y-4">
          <AppInput v-model="form.title" label="Título" placeholder="Ej: Figura personalizada de anime" :error="errors.title" :disabled="loading" />
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Comentarios <span class="text-gray-500 font-normal">(opcional)</span></label>
            <textarea
              v-model="form.description"
              rows="2"
              placeholder="Notas adicionales del cliente..."
              :disabled="loading"
              class="w-full rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 resize-none"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <AppInput v-model="form.color" label="Color deseado" placeholder="Ej: Negro" :disabled="loading" />
            <AppInput v-model="form.quantity" label="Cantidad" type="number" placeholder="1" min="1" :error="errors.quantity" :disabled="loading" />
          </div>
        </div>
      </AppCard>

      <!-- Tipo de solicitud -->
      <AppCard>
        <h3 class="text-sm font-medium text-gray-300 mb-4">Tipo de solicitud</h3>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <button
            v-for="opt in requestTypes"
            :key="opt.value"
            type="button"
            :disabled="loading"
            :class="[
              'rounded-lg border p-3 text-left transition-colors',
              form.request_type === opt.value
                ? 'border-blue-500 bg-blue-600/10 text-blue-300'
                : 'border-gray-700 hover:border-gray-600 text-gray-300',
            ]"
            @click="form.request_type = opt.value"
          >
            <p class="font-medium text-sm">{{ opt.label }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ opt.desc }}</p>
          </button>
        </div>

        <!-- Archivos de referencia (imágenes) -->
        <div v-if="form.request_type === 'REFERENCE'" class="mt-4 space-y-2">
          <label class="block text-xs text-gray-400">Imágenes de referencia (JPG, PNG, WEBP)</label>
          <input type="file" accept="image/*" multiple ref="fileInputRef" class="hidden" @change="handleFilesSelected" />
          <AppButton type="button" size="sm" variant="secondary" :disabled="loading" @click="(fileInputRef as HTMLInputElement)?.click()">
            + Agregar imágenes
          </AppButton>
          <ul v-if="selectedFiles.length" class="space-y-1 mt-2">
            <li v-for="(f, i) in selectedFiles" :key="i" class="flex items-center gap-2 text-sm text-gray-400">
              <span class="truncate flex-1">{{ f.name }}</span>
              <button type="button" class="text-red-400 shrink-0 hover:text-red-300" @click="removeFile(i)">✕</button>
            </li>
          </ul>
        </div>

        <!-- Archivos 3D -->
        <div v-if="form.request_type === 'PRINTABLE_FILE'" class="mt-4 space-y-2">
          <label class="block text-xs text-gray-400">Archivo 3D (STL, OBJ o 3MF)</label>
          <input type="file" accept=".stl,.obj,.3mf" multiple ref="fileInputRef" class="hidden" @change="handleFilesSelected" />
          <AppButton type="button" size="sm" variant="secondary" :disabled="loading" @click="(fileInputRef as HTMLInputElement)?.click()">
            + Agregar archivo 3D
          </AppButton>
          <ul v-if="selectedFiles.length" class="space-y-1 mt-2">
            <li v-for="(f, i) in selectedFiles" :key="i" class="flex items-center gap-2 text-sm text-gray-400">
              <span class="truncate flex-1">{{ f.name }}</span>
              <button type="button" class="text-red-400 shrink-0 hover:text-red-300" @click="removeFile(i)">✕</button>
            </li>
          </ul>
        </div>

        <!-- Enlace web -->
        <div v-if="form.request_type === 'WEB_MODEL'" class="mt-4 space-y-3">
          <AppInput
            v-model="webModelUrl"
            label="URL del modelo"
            placeholder="https://makerworld.com/models/12345"
            type="url"
            :error="errors.webModelUrl"
            :disabled="loading"
          />
          <AppInput
            v-model="webModelName"
            label="Nombre del modelo"
            placeholder="Ej: Yoda Mini"
            :error="errors.webModelName"
            :disabled="loading"
          />
          <div class="rounded-lg border border-yellow-700/50 bg-yellow-900/20 px-3 py-2 text-xs text-yellow-300">
            Si el modelo es de pago, el costo de la licencia corre por cuenta del cliente.
          </div>
        </div>
      </AppCard>

      <!-- Prioridad y entrega -->
      <AppCard>
        <h3 class="text-sm font-medium text-gray-300 mb-4">Prioridad y entrega</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Prioridad</label>
            <div class="flex gap-2">
              <button
                v-for="opt in priorities"
                :key="opt.value"
                type="button"
                :disabled="loading"
                :class="[
                  'flex-1 rounded-lg border py-2 text-xs font-medium transition-colors',
                  form.priority === opt.value
                    ? 'border-blue-500 bg-blue-600/10 text-blue-300'
                    : 'border-gray-700 hover:border-gray-600 text-gray-300',
                ]"
                @click="form.priority = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Método de entrega</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                v-for="opt in deliveryMethods"
                :key="opt.value"
                type="button"
                :disabled="loading"
                :class="[
                  'rounded-lg border p-3 text-left transition-colors',
                  form.delivery_method === opt.value
                    ? 'border-blue-500 bg-blue-600/10 text-blue-300'
                    : 'border-gray-700 hover:border-gray-600 text-gray-300',
                ]"
                @click="form.delivery_method = opt.value"
              >
                <p class="font-medium text-sm">{{ opt.label }}</p>
                <p class="text-xs text-gray-500 mt-0.5">{{ opt.desc }}</p>
              </button>
            </div>
          </div>
        </div>
      </AppCard>

      <AppAlert :message="errorMessage" />
      <div class="relative group/submit">
        <AppButton type="submit" size="lg" class="w-full" :loading="loading" :disabled="!selectedCustomer">
          Crear pedido
        </AppButton>
        <div v-if="!selectedCustomer" class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-56 text-xs text-center bg-gray-900 border border-gray-700 text-gray-400 rounded-lg px-2 py-1.5 hidden group-hover/submit:block z-10">
          Busca y selecciona un cliente primero.
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { createAdminOrder, listAdminUsers } from '../services/adminService'
import { uploadOrderFile, addWebModelLink } from '@/modules/orders/services/orderService'
import type { AdminUser } from '@/types'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const errors = ref<Record<string, string>>({})

const form = reactive({
  title: '',
  description: '',
  color: '',
  quantity: '1',
  request_type: 'REFERENCE',
  priority: 'NORMAL',
  delivery_method: 'PICKUP',
})

const customerSearch = ref('')
const customerResults = ref<AdminUser[]>([])
const selectedCustomer = ref<AdminUser | null>(null)
const searching = ref(false)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const selectedFiles = ref<File[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const webModelUrl = ref('')
const webModelName = ref('')

watch(() => form.request_type, () => {
  selectedFiles.value = []
  webModelUrl.value = ''
  webModelName.value = ''
})

function handleFilesSelected(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (!files) return
  selectedFiles.value = [...selectedFiles.value, ...Array.from(files)]
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
}

function searchCustomers() {
  if (selectedCustomer.value) return
  if (searchTimeout) clearTimeout(searchTimeout)
  const q = customerSearch.value.trim()
  if (q.length < 3) {
    customerResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    searching.value = true
    try {
      const res = await listAdminUsers({ page: 1, page_size: 10, search: q })
      customerResults.value = res.results
    } catch {
      customerResults.value = []
    } finally {
      searching.value = false
    }
  }, 300)
}

function selectCustomer(c: AdminUser) {
  selectedCustomer.value = c
  customerSearch.value = c.phone
  customerResults.value = []
}

function clearCustomer() {
  selectedCustomer.value = null
  customerSearch.value = ''
  customerResults.value = []
}

const requestTypes = [
  { value: 'REFERENCE', label: 'Por referencia', desc: 'El cliente trae fotos o imágenes' },
  { value: 'PRINTABLE_FILE', label: 'Archivo 3D', desc: 'El cliente tiene un STL, OBJ o 3MF' },
  { value: 'WEB_MODEL', label: 'Enlace web', desc: 'Modelo de MakerWorld, Thingiverse, etc.' },
]

const priorities = [
  { value: 'NORMAL', label: 'Normal' },
  { value: 'URGENT', label: 'Urgente +30%' },
  { value: 'EXPRESS', label: 'Express +50%' },
]

const deliveryMethods = [
  { value: 'PICKUP', label: 'Recoger en taller', desc: 'El cliente pasa a recoger' },
  { value: 'SHIPPING', label: 'Envío a domicilio', desc: 'Se envía a su dirección' },
]

async function handleCreate() {
  errorMessage.value = ''
  errors.value = {}

  if (!selectedCustomer.value) {
    errors.value.customer_id = 'Selecciona un cliente'
    return
  }
  if (!form.title.trim()) {
    errors.value.title = 'El título es obligatorio'
    return
  }
  if (Number(form.quantity) < 1) {
    errors.value.quantity = 'La cantidad mínima es 1'
    return
  }
  if (form.request_type === 'WEB_MODEL') {
    if (!webModelUrl.value.trim()) {
      errors.value.webModelUrl = 'La URL del modelo es obligatoria'
    }
    if (!webModelName.value.trim()) {
      errors.value.webModelName = 'El nombre del modelo es obligatorio'
    }
    if (Object.keys(errors.value).length) return
  }

  loading.value = true
  try {
    const result = await createAdminOrder({
      customer_id: selectedCustomer.value.id,
      request_type: form.request_type,
      title: form.title,
      description: form.description,
      color: form.color,
      quantity: Number(form.quantity),
      priority: form.priority,
      delivery_method: form.delivery_method,
    })

    if (form.request_type === 'WEB_MODEL') {
      await addWebModelLink(result.id, webModelUrl.value.trim(), webModelName.value.trim())
    } else if (selectedFiles.value.length) {
      const fileType = form.request_type === 'REFERENCE' ? 'IMAGE' : 'STL'
      await Promise.all(selectedFiles.value.map(f => uploadOrderFile(result.id, f, fileType)))
    }

    router.push(`/admin/orders/${result.id}`)
  } catch (err: any) {
    const data = err.response?.data
    if (data?.errors) {
      errors.value = Object.fromEntries(
        Object.entries(data.errors).map(([k, v]) => [k, Array.isArray(v) ? v[0] : String(v)])
      )
    } else {
      errorMessage.value = data?.message ?? 'Error al crear el pedido'
    }
  } finally {
    loading.value = false
  }
}
</script>
