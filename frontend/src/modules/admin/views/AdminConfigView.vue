<template>
  <div class="p-6 max-w-3xl">
    <div class="mb-6">
      <h1 class="text-xl font-semibold text-white">Configuración</h1>
      <p class="text-gray-400 text-sm mt-0.5">Costos, márgenes, horarios e instrucciones de pago</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 bg-gray-800 p-1 rounded-xl w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="[
          'px-4 py-2 text-sm rounded-lg transition-colors font-medium',
          activeTab === tab.value ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-gray-200',
        ]"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab: Configuración del negocio -->
    <template v-if="activeTab === 'config'">
      <div v-if="loadingConfig" class="h-64 bg-gray-800 rounded-xl animate-pulse" />
      <form v-else-if="config" @submit.prevent="handleSaveConfig" class="space-y-4">
        <AppCard>
          <h3 class="text-sm font-medium text-gray-400 mb-4">Costos de producción</h3>
          <div class="grid grid-cols-2 gap-4">
            <AppInput v-model="config.material_cost_per_kg" label="Costo material (MXN/kg)" type="number" />
            <AppInput v-model="config.labor_cost_per_hour" label="Costo mano de obra (MXN/h)" type="number" />
            <AppInput v-model="config.post_processing_cost_per_gram" label="Costo postprocesado (MXN/g)" type="number" />
            <AppInput v-model="config.packaging_cost" label="Costo empaque (MXN)" type="number" />
            <AppInput v-model="config.failure_percentage" label="Porcentaje de riesgo (%)" type="number" />
          </div>

          <!-- Tarifa eléctrica con lookup CFE -->
          <div class="mt-4 pt-4 border-t border-gray-700">
            <h4 class="text-xs font-medium text-gray-400 mb-3">Tarifa eléctrica</h4>
            <div class="flex items-end gap-3">
              <div class="flex-1">
                <AppInput v-model="config.electricity_rate_kwh" label="Tarifa actual (MXN/kWh)" type="number" />
              </div>
              <div class="flex-1">
                <label class="block text-xs text-gray-400 mb-1">Consultar por código postal</label>
                <div class="flex gap-2">
                  <input
                    v-model="cfePostalCode"
                    maxlength="5"
                    placeholder="29000"
                    class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    @keyup.enter="handleCfeLookup"
                  />
                  <AppButton size="sm" variant="secondary" :loading="lookingUpCfe" @click="handleCfeLookup">
                    Consultar
                  </AppButton>
                </div>
              </div>
            </div>

            <!-- Resultado del lookup -->
            <div v-if="cfeResult" class="mt-3 p-3 bg-gray-900/60 rounded-lg border border-gray-700 text-sm">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-gray-200 font-medium">Tarifa CFE {{ cfeResult.tariff_zone }}</p>
                  <p class="text-gray-500 text-xs mt-0.5">{{ cfeResult.zone_description }}</p>
                  <p class="text-gray-400 text-xs mt-1">
                    Tarifa de referencia (bloque intermedio 2025):
                    <span class="text-white font-medium">${{ cfeResult.rate_kwh }} MXN/kWh</span>
                  </p>
                  <p class="text-yellow-500/70 text-xs mt-1">
                    Referencia aproximada. Verifica tu tarifa real en tu recibo CFE.
                  </p>
                </div>
                <AppButton size="sm" @click="applyCfeRate">Aplicar</AppButton>
              </div>
            </div>
            <p v-if="cfeError" class="mt-2 text-xs text-red-400">{{ cfeError }}</p>
          </div>
        </AppCard>
        <AppCard>
          <h3 class="text-sm font-medium text-gray-400 mb-4">Ganancia y descuentos</h3>
          <div class="grid grid-cols-2 gap-4">
            <AppInput v-model="config.profit_margin_percentage" label="Margen de ganancia (%)" type="number" />
            <AppInput v-model="config.full_payment_discount_percentage" label="Descuento pago completo (%)" type="number" />
            <AppInput v-model="config.urgent_multiplier" label="Multiplicador urgente" type="number" />
            <AppInput v-model="config.express_multiplier" label="Multiplicador express" type="number" />
          </div>
        </AppCard>
        <AppCard>
          <h3 class="text-sm font-medium text-gray-400 mb-4">Plazos de pago</h3>
          <div class="grid grid-cols-2 gap-4">
            <AppInput v-model="config.deposit_deadline_hours" label="Plazo anticipo (horas)" type="number" />
            <AppInput v-model="config.balance_deadline_days" label="Plazo saldo (días)" type="number" />
          </div>
        </AppCard>
        <AppAlert :message="configError" />
        <AppAlert :message="configSuccess" variant="success" />
        <AppButton type="submit" :loading="savingConfig">Guardar configuración</AppButton>
      </form>
    </template>

    <!-- Tab: Instrucciones de pago -->
    <template v-if="activeTab === 'payment-instructions'">
      <div v-if="loadingInstructions" class="h-48 bg-gray-800 rounded-xl animate-pulse" />
      <form v-else-if="instructions" @submit.prevent="handleSaveInstructions" class="space-y-4">
        <AppCard>
          <div class="space-y-4">
            <AppInput v-model="instructions.bank_name" label="Banco" placeholder="BBVA" />
            <AppInput v-model="instructions.account_holder" label="Titular de la cuenta" placeholder="Imprint Studio" />
            <AppInput v-model="instructions.account_number" label="Número de cuenta" placeholder="1234567890" />
            <AppInput v-model="instructions.clabe" label="CLABE interbancaria" placeholder="012345678901234567" />
            <AppInput v-model="instructions.card_number" label="Número de tarjeta" placeholder="1234 5678 9012 3456" />
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-1.5">Notas adicionales</label>
              <textarea
                v-model="instructions.additional_notes"
                rows="3"
                class="w-full rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Instrucciones para el cliente..."
              />
            </div>
          </div>
        </AppCard>
        <AppAlert :message="instructionsError" />
        <AppAlert :message="instructionsSuccess" variant="success" />
        <AppButton type="submit" :loading="savingInstructions">Guardar instrucciones</AppButton>
      </form>
    </template>

    <!-- Tab: Días festivos -->
    <template v-if="activeTab === 'holidays'">
      <div class="space-y-4">
        <AppCard>
          <h3 class="text-sm font-medium text-gray-400 mb-3">Agregar día festivo</h3>
          <div class="grid grid-cols-2 gap-3">
            <AppInput v-model="newHoliday.holiday_date" label="Fecha" type="date" />
            <AppInput v-model="newHoliday.holiday_name" label="Nombre" placeholder="Navidad" />
          </div>
          <div class="flex gap-4 mt-3 text-sm">
            <label class="flex items-center gap-2 text-gray-400">
              <input type="checkbox" v-model="newHoliday.affects_shipping" class="rounded" />
              Afecta envíos
            </label>
            <label class="flex items-center gap-2 text-gray-400">
              <input type="checkbox" v-model="newHoliday.affects_pickup" class="rounded" />
              Afecta recolección
            </label>
          </div>
          <AppButton size="sm" class="mt-3" :loading="creatingHoliday" @click="handleCreateHoliday">
            + Agregar
          </AppButton>
        </AppCard>

        <div v-if="loadingHolidays" class="h-32 bg-gray-800 rounded-xl animate-pulse" />
        <AppCard v-else>
          <h3 class="text-sm font-medium text-gray-400 mb-3">Días festivos registrados</h3>
          <div v-if="holidays.length === 0" class="text-gray-500 text-sm">No hay días festivos registrados.</div>
          <div v-else class="space-y-2">
            <div
              v-for="holiday in holidays"
              :key="holiday.id"
              class="flex items-center justify-between text-sm py-2 border-b border-gray-700 last:border-0"
            >
              <div>
                <p class="text-gray-200">{{ holiday.holiday_name }}</p>
                <p class="text-gray-500 text-xs">{{ formatDate(holiday.holiday_date) }}</p>
              </div>
              <AppButton size="sm" variant="danger" @click="handleDeleteHoliday(holiday.id)">Eliminar</AppButton>
            </div>
          </div>
        </AppCard>
        <AppAlert :message="holidaysError" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import {
  getBusinessConfig, updateBusinessConfig,
  getPaymentInstructions, updatePaymentInstructions,
  listHolidays, createHoliday, deleteHoliday,
  lookupElectricityRate,
} from '../services/adminService'
import type { CfeRateLookup } from '../services/adminService'
import { formatDate } from '@/utils/formatters'
import type { BusinessConfig, PaymentInstructions } from '@/types'

const activeTab = ref('config')
const tabs = [
  { value: 'config', label: 'Costos y márgenes' },
  { value: 'payment-instructions', label: 'Instrucciones de pago' },
  { value: 'holidays', label: 'Días festivos' },
]

// --- Config ---
const config = ref<BusinessConfig | null>(null)
const loadingConfig = ref(true)
const savingConfig = ref(false)
const configError = ref('')
const configSuccess = ref('')

// --- Instrucciones de pago ---
const instructions = ref<PaymentInstructions | null>(null)
const loadingInstructions = ref(true)
const savingInstructions = ref(false)
const instructionsError = ref('')
const instructionsSuccess = ref('')

// --- Lookup tarifa CFE ---
const cfePostalCode = ref('')
const cfeResult = ref<CfeRateLookup | null>(null)
const cfeError = ref('')
const lookingUpCfe = ref(false)

async function handleCfeLookup() {
  if (!cfePostalCode.value || cfePostalCode.value.length !== 5) {
    cfeError.value = 'Ingresa un CP de 5 dígitos.'
    return
  }
  lookingUpCfe.value = true
  cfeError.value = ''
  cfeResult.value = null
  try {
    cfeResult.value = await lookupElectricityRate(cfePostalCode.value)
  } catch (err: any) {
    cfeError.value = err.response?.data?.message ?? 'No se encontró información para ese CP.'
  } finally {
    lookingUpCfe.value = false
  }
}

function applyCfeRate() {
  if (config.value && cfeResult.value) {
    config.value.electricity_rate_kwh = cfeResult.value.rate_kwh
  }
}

// --- Días festivos ---
const holidays = ref<any[]>([])
const loadingHolidays = ref(true)
const creatingHoliday = ref(false)
const holidaysError = ref('')
const newHoliday = ref({ holiday_date: '', holiday_name: '', affects_shipping: true, affects_pickup: true })

onMounted(async () => {
  const [c, i, h] = await Promise.allSettled([
    getBusinessConfig(),
    getPaymentInstructions(),
    listHolidays(),
  ])
  if (c.status === 'fulfilled') config.value = c.value
  loadingConfig.value = false
  if (i.status === 'fulfilled') instructions.value = i.value
  loadingInstructions.value = false
  if (h.status === 'fulfilled') holidays.value = h.value
  loadingHolidays.value = false
})

async function handleSaveConfig() {
  if (!config.value) return
  savingConfig.value = true
  configError.value = ''
  configSuccess.value = ''
  try {
    config.value = await updateBusinessConfig(config.value)
    configSuccess.value = 'Configuración guardada correctamente.'
  } catch (err: any) {
    configError.value = err.response?.data?.message ?? 'Error al guardar'
  } finally {
    savingConfig.value = false
  }
}

async function handleSaveInstructions() {
  if (!instructions.value) return
  savingInstructions.value = true
  instructionsError.value = ''
  instructionsSuccess.value = ''
  try {
    instructions.value = await updatePaymentInstructions(instructions.value)
    instructionsSuccess.value = 'Instrucciones guardadas correctamente.'
  } catch (err: any) {
    instructionsError.value = err.response?.data?.message ?? 'Error al guardar'
  } finally {
    savingInstructions.value = false
  }
}

async function handleCreateHoliday() {
  creatingHoliday.value = true
  holidaysError.value = ''
  try {
    await createHoliday(newHoliday.value)
    holidays.value = await listHolidays()
    newHoliday.value = { holiday_date: '', holiday_name: '', affects_shipping: true, affects_pickup: true }
  } catch (err: any) {
    holidaysError.value = err.response?.data?.message ?? 'Error al agregar'
  } finally {
    creatingHoliday.value = false
  }
}

async function handleDeleteHoliday(id: string) {
  try {
    await deleteHoliday(id)
    holidays.value = holidays.value.filter(h => h.id !== id)
  } catch (err: any) {
    holidaysError.value = err.response?.data?.message ?? 'Error al eliminar'
  }
}
</script>
