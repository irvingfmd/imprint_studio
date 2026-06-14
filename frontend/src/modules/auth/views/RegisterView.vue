<template>
  <div class="bg-gray-800 rounded-2xl border border-gray-700 p-8">
    <h2 class="text-xl font-semibold text-white mb-1">Crear cuenta</h2>
    <p class="text-gray-400 text-sm mb-6">Regístrate para hacer tus pedidos</p>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <AppInput
          v-model="form.first_name"
          label="Nombre *"
          placeholder="Irving"
          :error="errors.first_name"
          :disabled="loading"
        />
        <AppInput
          v-model="form.last_name"
          label="Apellido"
          placeholder="Martínez"
          :error="errors.last_name"
          :disabled="loading"
        />
      </div>
      <div>
        <AppInput
          v-model="form.phone"
          label="Teléfono WhatsApp *"
          type="tel"
          placeholder="+5219611234567"
          :error="errors.phone"
          :disabled="loading"
        />
        <p class="text-xs text-gray-500 mt-1">Formato: +52 seguido de 10 dígitos</p>
      </div>
      <AppInput
        v-model="form.email"
        label="Correo electrónico"
        type="email"
        placeholder="tu@email.com"
        :error="errors.email"
        :disabled="loading"
      />
      <AppAlert :message="errorMessage" />
      <AppButton type="submit" size="lg" class="w-full" :loading="loading">
        Registrarme
      </AppButton>
    </form>

    <p class="text-center text-sm text-gray-400 mt-6">
      ¿Ya tienes cuenta?
      <RouterLink to="/login" class="text-blue-400 hover:text-blue-300 font-medium">Inicia sesión</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { register, sendOtp } from '../services/authService'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const errors = ref<Record<string, string>>({})

const form = reactive({ first_name: '', last_name: '', phone: '', email: '' })

// Regex E.164: + seguido de 8 a 15 dígitos
const PHONE_REGEX = /^\+[1-9]\d{7,14}$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validateForm(): boolean {
  errors.value = {}

  if (!form.first_name.trim()) {
    errors.value.first_name = 'El nombre es obligatorio'
  }

  if (!form.phone.trim()) {
    errors.value.phone = 'El teléfono es obligatorio'
  } else if (!PHONE_REGEX.test(form.phone.trim())) {
    errors.value.phone = 'Formato inválido. Usa +52 seguido de 10 dígitos, ej: +5219611234567'
  }

  if (form.email && !EMAIL_REGEX.test(form.email.trim())) {
    errors.value.email = 'Ingresa un correo electrónico válido'
  }

  return Object.keys(errors.value).length === 0
}

async function handleRegister() {
  errorMessage.value = ''

  if (!validateForm()) return

  loading.value = true
  try {
    await register(form)
  } catch (err: any) {
    const data = err.response?.data
    if (data?.errors) {
      errors.value = Object.fromEntries(
        Object.entries(data.errors).map(([k, v]) => [k, Array.isArray(v) ? v[0] : String(v)])
      )
    } else {
      errorMessage.value = data?.message ?? 'Error al registrar. Verifica tus datos.'
    }
    loading.value = false
    return
  }

  // Registro exitoso — enviar OTP automáticamente
  try {
    const res = await sendOtp(form.phone)
    if (res.dev_code) sessionStorage.setItem('otp_dev_code', res.dev_code)
    router.push({ name: 'otp', query: { phone: form.phone } })
  } catch {
    // Si el OTP falla, redirigir a login con mensaje de éxito
    router.push({ name: 'login', query: { registered: '1' } })
  }
}
</script>
