<template>
  <div class="bg-gray-800 rounded-2xl border border-gray-700 p-8">
    <h2 class="text-xl font-semibold text-white mb-1">Verificar código</h2>
    <p class="text-gray-400 text-sm mb-2">
      Ingresa el código enviado a
      <span class="text-gray-200 font-medium">{{ phone }}</span>
    </p>
    <p class="text-xs text-gray-500 mb-6">En desarrollo el código se imprime en la consola del servidor.</p>

    <form @submit.prevent="handleVerify" class="space-y-4">
      <AppInput
        v-model="otpCode"
        label="Código OTP"
        type="text"
        placeholder="123456"
        maxlength="6"
        :error="errors.otp"
        :disabled="loading"
      />
      <AppAlert :message="errorMessage" />
      <AppButton type="submit" size="lg" class="w-full" :loading="loading">
        Verificar
      </AppButton>
    </form>

    <button
      class="mt-4 w-full text-center text-sm text-gray-400 hover:text-gray-200 transition-colors"
      :disabled="resendCooldown > 0"
      @click="handleResend"
    >
      {{ resendCooldown > 0 ? `Reenviar en ${resendCooldown}s` : 'Reenviar código' }}
    </button>

    <p class="text-center text-sm text-gray-400 mt-4">
      <RouterLink to="/login" class="text-blue-400 hover:text-blue-300">← Cambiar número</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { verifyOtp, sendOtp, getMe } from '../services/authService'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const phone = ref(String(route.query.phone ?? ''))
const otpCode = ref('')
const loading = ref(false)
const errorMessage = ref('')
const errors = ref<Record<string, string>>({})
const resendCooldown = ref(0)

let timer: ReturnType<typeof setInterval>

function startCooldown() {
  resendCooldown.value = 60
  timer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(timer)
  }, 1000)
}

onMounted(startCooldown)
onUnmounted(() => clearInterval(timer))

async function handleVerify() {
  errorMessage.value = ''
  errors.value = {}

  if (!otpCode.value.trim()) {
    errors.value.otp = 'El código es obligatorio'
    return
  }

  loading.value = true
  try {
    const tokens = await verifyOtp(phone.value, otpCode.value.trim())
    auth.setTokens(tokens.access, tokens.refresh)
    const user = await getMe()
    auth.setUser(user)
    router.push(user.role === 'ADMIN' ? '/admin/dashboard' : '/orders')
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Código inválido o expirado'
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  if (resendCooldown.value > 0) return
  try {
    await sendOtp(phone.value)
    startCooldown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al reenviar'
  }
}
</script>
