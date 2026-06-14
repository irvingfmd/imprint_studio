<template>
  <div class="bg-gray-800 rounded-2xl border border-gray-700 p-8">
    <h2 class="text-xl font-semibold text-white mb-1">Iniciar sesión</h2>
    <p class="text-gray-400 text-sm mb-6">Ingresa tu número de WhatsApp con código de país</p>

    <!-- Aviso post-registro -->
    <AppAlert v-if="registeredMessage" :message="registeredMessage" variant="success" class="mb-4" />

    <form @submit.prevent="handleSendOtp" class="space-y-4">
      <AppInput
        v-model="phone"
        label="Número de teléfono"
        type="tel"
        placeholder="+5219611234567"
        :error="errors.phone"
        :disabled="loading"
      />
      <p class="text-xs text-gray-500 -mt-2">
        Formato internacional: <span class="text-gray-400">+52 seguido de 10 dígitos</span>
      </p>
      <AppAlert :message="errorMessage" />
      <AppButton type="submit" size="lg" class="w-full" :loading="loading">
        Enviar código OTP
      </AppButton>
    </form>

    <p class="text-center text-sm text-gray-400 mt-6">
      ¿No tienes cuenta?
      <RouterLink to="/register" class="text-blue-400 hover:text-blue-300 font-medium">Regístrate aquí</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { sendOtp } from '../services/authService'

const router = useRouter()
const route = useRoute()

const phone = ref('')
const loading = ref(false)
const errorMessage = ref('')
const registeredMessage = ref('')
const errors = ref<Record<string, string>>({})

// Regex E.164: + seguido de 8 a 15 dígitos
const PHONE_REGEX = /^\+[1-9]\d{7,14}$/

onMounted(() => {
  if (route.query.registered) {
    registeredMessage.value = 'Cuenta creada exitosamente. Ingresa tu número para recibir el código OTP.'
  }
})

function validatePhone(value: string): string {
  if (!value.trim()) return 'El teléfono es obligatorio'
  if (!PHONE_REGEX.test(value.trim())) return 'Formato inválido. Usa +52 seguido de 10 dígitos, ej: +5219611234567'
  return ''
}

async function handleSendOtp() {
  errorMessage.value = ''
  registeredMessage.value = ''
  errors.value = {}

  const phoneError = validatePhone(phone.value)
  if (phoneError) {
    errors.value.phone = phoneError
    return
  }

  loading.value = true
  try {
    const res = await sendOtp(phone.value.trim())
    if (res.dev_code) sessionStorage.setItem('otp_dev_code', res.dev_code)
    router.push({ name: 'otp', query: { phone: phone.value.trim() } })
  } catch (err: any) {
    const detail = err.response?.data?.message ?? 'Error al enviar el código'
    errorMessage.value = detail
  } finally {
    loading.value = false
  }
}
</script>
