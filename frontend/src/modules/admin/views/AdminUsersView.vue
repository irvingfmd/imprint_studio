<template>
  <div class="p-6 max-w-4xl">
    <div class="mb-6">
      <h1 class="text-xl font-semibold text-white">Usuarios</h1>
      <p class="text-gray-400 text-sm mt-0.5">Gestión de clientes y administradores</p>
    </div>

    <!-- Filtro por rol -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="opt in roleFilters"
        :key="opt.value"
        :class="[
          'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
          activeFilter === opt.value
            ? 'bg-blue-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700',
        ]"
        @click="setFilter(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 bg-gray-800 rounded-xl animate-pulse" />
    </div>

    <div v-else-if="filtered.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">👥</div>
      <p class="text-gray-400">No hay usuarios con este filtro</p>
    </div>

    <div v-else class="space-y-2">
      <AppCard v-for="user in filtered" :key="user.id">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-9 h-9 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 text-sm font-semibold shrink-0">
              {{ initials(user) }}
            </div>
            <div class="min-w-0">
              <p class="text-gray-100 font-medium text-sm truncate">
                {{ fullName(user) || user.phone }}
              </p>
              <p class="text-gray-500 text-xs">{{ user.phone }}</p>
              <p v-if="user.email" class="text-gray-600 text-xs">{{ user.email }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <span :class="[
              'px-2 py-0.5 rounded-full text-xs font-medium',
              user.role === 'ADMIN'
                ? 'bg-purple-600/20 text-purple-300 border border-purple-700'
                : 'bg-gray-700 text-gray-300 border border-gray-600',
            ]">
              {{ user.role === 'ADMIN' ? 'Admin' : 'Cliente' }}
            </span>

            <div class="flex gap-1.5">
              <AppButton
                v-if="user.role === 'CUSTOMER'"
                size="sm"
                variant="secondary"
                :loading="changing === user.id"
                @click="handleRoleChange(user, 'ADMIN')"
              >
                Promover
              </AppButton>
              <AppButton
                v-else
                size="sm"
                variant="ghost"
                :loading="changing === user.id"
                @click="handleRoleChange(user, 'CUSTOMER')"
              >
                Degradar
              </AppButton>
            </div>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Paginación -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4 text-sm text-gray-400">
      <AppButton size="sm" variant="ghost" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
        ← Anterior
      </AppButton>
      <span>Página {{ currentPage }} de {{ totalPages }}</span>
      <AppButton size="sm" variant="ghost" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        Siguiente →
      </AppButton>
    </div>

    <AppAlert :message="errorMessage" class="mt-4" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppAlert from '@/components/ui/AppAlert.vue'
import { listAdminUsers, updateUserRole } from '../services/adminService'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/composables/useToast'
import type { AdminUser } from '@/types'

const auth = useAuthStore()
const toast = useToast()

const users = ref<AdminUser[]>([])
const loading = ref(true)
const errorMessage = ref('')
const changing = ref<string | null>(null)
const activeFilter = ref<'ALL' | 'CUSTOMER' | 'ADMIN'>('ALL')
const currentPage = ref(1)
const totalPages = ref(1)
const PAGE_SIZE = 20

const roleFilters = [
  { value: 'ALL', label: 'Todos' },
  { value: 'CUSTOMER', label: 'Clientes' },
  { value: 'ADMIN', label: 'Admins' },
] as const

const filtered = computed(() => {
  if (activeFilter.value === 'ALL') return users.value
  return users.value.filter(u => u.role === activeFilter.value)
})

function fullName(user: AdminUser): string {
  return `${user.first_name} ${user.last_name}`.trim()
}

function initials(user: AdminUser): string {
  return `${user.first_name[0] ?? ''}${user.last_name[0] ?? ''}`.toUpperCase() || '?'
}

async function load(page: number) {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminUsers({ page, page_size: PAGE_SIZE })
    users.value = result.results
    totalPages.value = result.num_pages ?? 1
    currentPage.value = page
  } catch {
    errorMessage.value = 'Error al cargar los usuarios.'
  } finally {
    loading.value = false
  }
}

function setFilter(value: typeof activeFilter.value) {
  activeFilter.value = value
}

async function goToPage(page: number) {
  await load(page)
}

async function handleRoleChange(user: AdminUser, newRole: 'CUSTOMER' | 'ADMIN') {
  if (user.id === auth.user?.id) {
    errorMessage.value = 'No puedes cambiar tu propio rol.'
    return
  }
  changing.value = user.id
  try {
    const updated = await updateUserRole(user.id, newRole)
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
    errorMessage.value = ''
    toast.show(`Rol de ${fullName(user) || user.phone} actualizado a ${newRole === 'ADMIN' ? 'Admin' : 'Cliente'}.`)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.message ?? 'Error al cambiar el rol.'
  } finally {
    changing.value = null
  }
}

onMounted(() => load(1))
</script>
