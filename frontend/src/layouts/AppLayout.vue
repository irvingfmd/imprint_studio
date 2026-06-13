<template>
  <div class="min-h-screen bg-gray-900 flex">
    <!-- Sidebar -->
    <aside class="w-60 shrink-0 bg-gray-950 border-r border-gray-800 flex flex-col">
      <!-- Logo -->
      <div class="flex items-center gap-3 px-5 py-5 border-b border-gray-800">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <span class="font-semibold text-white text-sm">Imprint Studio</span>
      </div>

      <!-- Navegación -->
      <nav class="flex-1 px-3 py-4 space-y-0.5">
        <!-- Links de cliente -->
        <template v-if="!auth.isAdmin">
          <RouterLink
            to="/orders"
            class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors"
            :class="$route.path.startsWith('/orders') ? 'bg-blue-600/20 text-blue-400' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'"
          >
            <span>📦</span> Mis pedidos
          </RouterLink>
        </template>

        <!-- Links de admin -->
        <template v-else>
          <RouterLink
            v-for="link in adminLinks"
            :key="link.to"
            :to="link.to"
            class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors"
            :class="$route.path.startsWith(link.to) ? 'bg-blue-600/20 text-blue-400' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'"
          >
            <span>{{ link.icon }}</span> {{ link.label }}
          </RouterLink>
        </template>
      </nav>

      <!-- Usuario -->
      <div class="px-3 py-4 border-t border-gray-800">
        <div class="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-800 transition-colors">
          <div class="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 text-sm font-medium shrink-0">
            {{ initials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-200 truncate">{{ fullName }}</p>
            <p class="text-xs text-gray-500">{{ auth.isAdmin ? 'Administrador' : 'Cliente' }}</p>
          </div>
          <button @click="handleLogout" class="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors" title="Cerrar sesión">
            <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Salir
          </button>
        </div>
      </div>
    </aside>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { getMe } from '@/modules/auth/services/authService'

const auth = useAuthStore()
const router = useRouter()

const adminLinks = [
  { to: '/admin/dashboard', icon: '📊', label: 'Dashboard' },
  { to: '/admin/orders', icon: '📦', label: 'Pedidos' },
  { to: '/admin/payments', icon: '💳', label: 'Pagos' },
  { to: '/admin/config', icon: '⚙️', label: 'Configuración' },
]

const fullName = computed(() => {
  if (!auth.user) return '...'
  return `${auth.user.first_name} ${auth.user.last_name}`.trim()
})

const initials = computed(() => {
  if (!auth.user) return '?'
  return `${auth.user.first_name[0] ?? ''}${auth.user.last_name[0] ?? ''}`.toUpperCase()
})

async function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  if (auth.isAuthenticated && !auth.user) {
    try {
      const user = await getMe()
      auth.setUser(user)
    } catch {
      auth.logout()
      router.push('/login')
    }
  }
})
</script>
