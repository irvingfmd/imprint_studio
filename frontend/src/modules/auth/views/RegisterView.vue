<template>
  <div class="bg-gray-800 rounded-2xl border border-gray-700 p-8">
    <h2 class="text-xl font-semibold text-white mb-1">Crear cuenta</h2>
    <p class="text-gray-400 text-sm mb-6">Regístrate para hacer tus pedidos</p>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <AppInput v-model="form.first_name" label="Nombre" placeholder="Irving" :error="errors.first_name" :disabled="loading" />
        <AppInput v-model="form.last_name" label="Apellido" placeholder="Martínez" :error="errors.last_name" :disabled="loading" />
      </div>
      <AppInput v-model="form.phone" label="Teléfono (WhatsApp)" type="tel" placeholder="+5219611234567" :error="errors.phone" :disabled="loading" />
      <AppInput v-model="form.email" label="Correo electrónico" type="email" placeholder="tu@email.com" :error="errors.email" :disabled="loading" />
      <AppAlert :message="errorMessage" />
      <AppAlert :message="successMessage" variant="success" />
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
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { register } from '../services/authService'

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const errors = ref<Record<string, string>>({})

const form = reactive({ first_name: '', last_name: '', phone: '', email: '' })

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''
  errors.value = {}

  loading.value = true
  try {
    await register(form)
    successMessage.value = '¡Registro exitoso! Ahora inicia sesión con tu número.'
    Object.assign(form, { first_name: '', last_name: '', phone: '', email: '' })
  } catch (err: any) {
    const data = err.response?.data
    if (data?.errors) {
      errors.value = Object.fromEntries(
        Object.entries(data.errors).map(([k, v]) => [k, Array.isArray(v) ? v[0] : String(v)])
      )
    } else {
      errorMessage.value = data?.message ?? 'Error al registrar'
    }
  } finally {
    loading.value = false
  }
}
</script>
