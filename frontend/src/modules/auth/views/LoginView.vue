<template>
  <div class="bg-gray-800 rounded-2xl border border-gray-700 p-8">
    <h2 class="text-xl font-semibold text-white mb-1">Iniciar sesión</h2>
    <p class="text-gray-400 text-sm mb-6">Ingresa tu número de WhatsApp</p>

    <form @submit.prevent="handleSendOtp" class="space-y-4">
      <AppInput
        v-model="phone"
        label="Número de teléfono"
        type="tel"
        placeholder="+5219611234567"
        :error="errors.phone"
        :disabled="loading"
      />
      <AppAlert :message="errorMessage" />
      <AppButton type="submit" size="lg" class="w-full" :loading="loading">
        Enviar código OTP
      </AppButton>
    </form>

    <p class="text-center text-sm text-gray-400 mt-6">
      ¿No tienes cuenta?
      <RouterLink to="/register" class="text-blue-400 hover:text-blue-300 font-medium">Regístrate</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { sendOtp } from '../services/authService'

const router = useRouter()
const phone = ref('')
const loading = ref(false)
const errorMessage = ref('')
const errors = ref<Record<string, string>>({})

async function handleSendOtp() {
  errorMessage.value = ''
  errors.value = {}

  if (!phone.value.trim()) {
    errors.value.phone = 'El teléfono es obligatorio'
    return
  }

  loading.value = true
  try {
    await sendOtp(phone.value.trim())
    router.push({ name: 'otp', query: { phone: phone.value.trim() } })
  } catch (err: any) {
    const detail = err.response?.data?.message ?? 'Error al enviar el código'
    errorMessage.value = detail
  } finally {
    loading.value = false
  }
}
</script>
