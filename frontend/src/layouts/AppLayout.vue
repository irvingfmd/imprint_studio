<template>
  <div class="min-h-screen bg-gray-900 flex">
    <!-- Sidebar -->
    <aside
      :class="[
        'shrink-0 bg-gray-950 border-r border-gray-800 flex flex-col transition-all duration-200',
        collapsed ? 'w-16' : 'w-60',
      ]"
    >
      <!-- Logo + toggle -->
      <div class="flex items-center gap-3 px-3 py-4 border-b border-gray-800" :class="collapsed ? 'justify-center' : 'px-4'">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <span v-if="!collapsed" class="font-semibold text-white text-sm">Imprint Studio</span>
        <button
          v-if="!collapsed"
          @click="collapsed = true"
          class="ml-auto text-gray-500 hover:text-gray-300 transition-colors"
          title="Colapsar menú"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" /></svg>
        </button>
      </div>

      <!-- Botón expandir (colapsado) -->
      <button
        v-if="collapsed"
        @click="collapsed = false"
        class="mx-auto mt-2 text-gray-500 hover:text-gray-300 transition-colors"
        title="Expandir menú"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" /></svg>
      </button>

      <!-- Navegación -->
      <nav class="flex-1 px-2 py-3 space-y-1 overflow-y-auto">
        <!-- Links de cliente -->
        <template v-if="!auth.isAdmin">
          <SidebarLink to="/orders" :collapsed="collapsed" :active="$route.path.startsWith('/orders')" label="Mis pedidos">
            <template #icon><IconPackage /></template>
          </SidebarLink>
          <SidebarLink to="/faq" :collapsed="collapsed" :active="$route.path === '/faq'" label="Preguntas frecuentes">
            <template #icon><IconHelp /></template>
          </SidebarLink>
        </template>

        <!-- Links de admin -->
        <template v-else>
          <!-- Principal -->
          <SidebarSection v-if="!collapsed" label="Principal" />
          <SidebarLink to="/admin/dashboard" :collapsed="collapsed" :active="$route.path === '/admin/dashboard'" label="Dashboard">
            <template #icon><IconChart /></template>
          </SidebarLink>
          <SidebarLink to="/admin/orders" :collapsed="collapsed" :active="$route.path.startsWith('/admin/orders')" label="Pedidos">
            <template #icon><IconPackage /></template>
          </SidebarLink>
          <SidebarLink to="/admin/production" :collapsed="collapsed" :active="$route.path === '/admin/production'" label="Producción">
            <template #icon><IconCalendar /></template>
          </SidebarLink>

          <!-- Finanzas -->
          <SidebarSection v-if="!collapsed" label="Finanzas" />
          <SidebarLink to="/admin/payments" :collapsed="collapsed" :active="$route.path.startsWith('/admin/payments')" label="Pagos">
            <template #icon><IconCreditCard /></template>
          </SidebarLink>
          <SidebarLink to="/admin/discounts" :collapsed="collapsed" :active="$route.path.startsWith('/admin/discounts')" label="Descuentos">
            <template #icon><IconTag /></template>
          </SidebarLink>

          <!-- Catálogo -->
          <SidebarSection v-if="!collapsed" label="Catálogo" />
          <SidebarLink to="/admin/printers" :collapsed="collapsed" :active="$route.path.startsWith('/admin/printers')" label="Impresoras">
            <template #icon><IconPrinter /></template>
          </SidebarLink>
          <SidebarLink to="/admin/materials" :collapsed="collapsed" :active="$route.path.startsWith('/admin/materials')" label="Materiales">
            <template #icon><IconBeaker /></template>
          </SidebarLink>

          <!-- Sistema -->
          <SidebarSection v-if="!collapsed" label="Sistema" />
          <SidebarLink to="/admin/users" :collapsed="collapsed" :active="$route.path.startsWith('/admin/users')" label="Usuarios">
            <template #icon><IconUsers /></template>
          </SidebarLink>
          <SidebarLink to="/admin/config" :collapsed="collapsed" :active="$route.path.startsWith('/admin/config')" label="Configuración">
            <template #icon><IconSettings /></template>
          </SidebarLink>
        </template>
      </nav>

      <!-- Usuario -->
      <div class="px-2 py-3 border-t border-gray-800">
        <div :class="['flex items-center gap-2 px-2 py-2 rounded-lg', collapsed ? 'justify-center' : '']">
          <div class="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 text-xs font-medium shrink-0">
            {{ initials }}
          </div>
          <template v-if="!collapsed">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-200 truncate">{{ fullName }}</p>
              <p class="text-xs text-gray-500">{{ auth.isAdmin ? 'Admin' : 'Cliente' }}</p>
            </div>
            <div class="flex items-center gap-1.5">
              <LanguageSwitcher />
              <button @click="handleLogout" class="text-gray-500 hover:text-gray-300 transition-colors" title="Cerrar sesión">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </template>
        </div>
        <button
          v-if="collapsed"
          @click="handleLogout"
          class="w-full mt-1 flex justify-center text-gray-500 hover:text-gray-300 transition-colors py-1"
          title="Cerrar sesión"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </aside>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LanguageSwitcher from '@/components/ui/LanguageSwitcher.vue'
import { getMe } from '@/modules/auth/services/authService'

const auth = useAuthStore()
const router = useRouter()
const collapsed = ref(false)

const fullName = computed(() => {
  if (!auth.user) return '...'
  return `${auth.user.first_name} ${auth.user.last_name}`.trim()
})

const initials = computed(() => {
  if (!auth.user) return '?'
  return `${auth.user.first_name[0] ?? ''}${auth.user.last_name[0] ?? ''}`.toUpperCase()
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(async () => {
  if (auth.isAuthenticated && !auth.user) {
    try {
      const user = await getMe()
      auth.setUser(user)
    } catch {
      await auth.logout()
      router.push('/login')
    }
  }
})

// --- Componentes inline del sidebar ---

const SidebarLink = {
  props: { to: String, collapsed: Boolean, active: Boolean, label: String },
  setup(props: any, { slots }: any) {
    return () => h(RouterLink, {
      to: props.to,
      class: [
        'flex items-center gap-2.5 rounded-lg text-sm transition-colors',
        props.collapsed ? 'justify-center px-2 py-2' : 'px-3 py-2',
        props.active ? 'bg-blue-600/15 text-blue-400' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60',
      ],
      title: props.collapsed ? props.label : undefined,
    }, {
      default: () => [
        h('span', { class: 'w-5 h-5 shrink-0 flex items-center justify-center' }, slots.icon?.()),
        !props.collapsed ? h('span', { class: 'truncate' }, props.label) : null,
      ],
    })
  },
}

const SidebarSection = {
  props: { label: String },
  setup(props: any) {
    return () => h('p', { class: 'text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 pt-4 pb-1' }, props.label)
  },
}

// --- Íconos SVG inline ---
const icon = (d: string) => ({
  setup() {
    return () => h('svg', { class: 'w-5 h-5', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor', 'stroke-width': '1.5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d }),
    ])
  },
})

const IconChart = icon('M3 13h2v8H3zm6-4h2v12H9zm6-3h2v15h-2zm6-2h2v17h-2z')
const IconPackage = icon('M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4')
const IconCalendar = icon('M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z')
const IconCreditCard = icon('M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z')
const IconTag = icon('M7 7h.01M7 3h5a1.99 1.99 0 011.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z')
const IconPrinter = icon('M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2M6 14h12v8H6z')
const IconBeaker = icon('M9 3v2m6-2v2M9 5a2 2 0 00-2 2v1.6a2 2 0 01-.4 1.2L4 13.5a2 2 0 00-.4 1.2V19a2 2 0 002 2h12.8a2 2 0 002-2v-4.3a2 2 0 00-.4-1.2L17.4 9.8a2 2 0 01-.4-1.2V7a2 2 0 00-2-2H9z')
const IconUsers = icon('M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z')
const IconSettings = icon('M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z')
const IconHelp = icon('M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z')
</script>
