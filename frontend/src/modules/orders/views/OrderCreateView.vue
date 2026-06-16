<template>
  <div class="p-6 max-w-2xl">
    <div class="mb-6">
      <RouterLink to="/orders" class="text-sm text-gray-400 hover:text-gray-200 flex items-center gap-1 mb-3 w-fit">
        ← Mis pedidos
      </RouterLink>
      <h1 class="text-xl font-semibold text-white">Nuevo pedido</h1>
    </div>

    <form @submit.prevent="handleCreate" class="space-y-5">
      <AppCard>
        <h3 class="text-sm font-medium text-gray-300 mb-4">Información del pedido</h3>
        <div class="space-y-4">
          <AppInput v-model="form.title" label="Título" placeholder="Ej: Figura personalizada de anime" :error="errors.title" :disabled="loading" />
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Descripción</label>
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="Describe lo que necesitas imprimir..."
              :disabled="loading"
              class="w-full rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 resize-none"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <AppInput v-model="form.color" label="Color deseado" placeholder="Ej: Negro" :error="errors.color" :disabled="loading" />
            <AppInput v-model="form.quantity" label="Cantidad" type="number" placeholder="1" min="1" :error="errors.quantity" :disabled="loading" />
          </div>
        </div>
      </AppCard>

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

        <!-- Campos adicionales por tipo de solicitud -->
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
            Si el modelo es de pago, el costo de la licencia corre por tu cuenta. Imprint Studio solo cobra el servicio de impresión.
          </div>
        </div>
      </AppCard>

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
            <p class="text-xs text-gray-500 mt-1">{{ priorityNote }}</p>
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
      <AppButton type="submit" size="lg" class="w-full" :loading="loading">
        Crear pedido
      </AppButton>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { createOrder, addWebModelLink, uploadOrderFile } from '../services/orderService'

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

const webModelUrl = ref('')
const webModelName = ref('')
const selectedFiles = ref<File[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

watch(() => form.request_type, () => { selectedFiles.value = [] })

function handleFilesSelected(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (!files) return
  selectedFiles.value = [...selectedFiles.value, ...Array.from(files)]
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
}

const requestTypes = [
  { value: 'REFERENCE', label: 'Por referencia', desc: 'Subes fotos o imágenes de lo que quieres' },
  { value: 'PRINTABLE_FILE', label: 'Archivo 3D', desc: 'Tienes un archivo STL, OBJ o 3MF' },
  { value: 'WEB_MODEL', label: 'Enlace web', desc: 'Encontraste el modelo en MakerWorld, Thingiverse u otro sitio' },
]

const priorities = [
  { value: 'NORMAL', label: 'Normal (5-7 días)' },
  { value: 'URGENT', label: 'Urgente +30% (2-3 días)' },
  { value: 'EXPRESS', label: 'Express +50% (24-48h)' },
]

const deliveryMethods = [
  { value: 'PICKUP', label: 'Recoger en taller', desc: 'Pasa a recoger tu pedido' },
  { value: 'SHIPPING', label: 'Envío a domicilio', desc: 'Te lo enviamos a tu dirección' },
]

const priorityNote = computed(() => ({
  NORMAL: 'Tiempo estimado: 5 a 7 días hábiles',
  URGENT: 'Tiempo estimado: 2 a 3 días hábiles. Costo +30%.',
  EXPRESS: 'Tiempo estimado: 24 a 48 horas hábiles. Costo +50%.',
}[form.priority]))

async function handleCreate() {
  errorMessage.value = ''
  errors.value = {}

  if (!form.title.trim()) {
    errors.value.title = 'El título es obligatorio'
  }
  if (!form.description.trim()) {
    errorMessage.value = 'La descripción es obligatoria'
  }
  if (Number(form.quantity) < 1) {
    errors.value.quantity = 'La cantidad mínima es 1'
  }
  if (form.request_type === 'WEB_MODEL') {
    if (!webModelUrl.value.trim()) {
      errors.value.webModelUrl = 'La URL del modelo es obligatoria'
    }
    if (!webModelName.value.trim()) {
      errors.value.webModelName = 'El nombre del modelo es obligatorio'
    }
  }
  if (Object.keys(errors.value).length > 0 || errorMessage.value) return

  loading.value = true
  try {
    const result = await createOrder({
      ...form,
      quantity: Number(form.quantity),
    })
    if (form.request_type === 'WEB_MODEL') {
      await addWebModelLink(result.id, webModelUrl.value.trim(), webModelName.value.trim())
    } else if (selectedFiles.value.length) {
      const fileType = form.request_type === 'REFERENCE' ? 'REFERENCE' : 'PRINTABLE_FILE'
      await Promise.all(selectedFiles.value.map(f => uploadOrderFile(result.id, f, fileType)))
    }
    router.push(`/orders/${result.id}`)
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
