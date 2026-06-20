// Router principal con guards de autenticación y rol
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Rutas de autenticación
    {
      path: '/login',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        { path: '', name: 'login', component: () => import('@/modules/auth/views/LoginView.vue') },
        { path: '/register', name: 'register', component: () => import('@/modules/auth/views/RegisterView.vue') },
        { path: '/otp', name: 'otp', component: () => import('@/modules/auth/views/OtpView.vue') },
      ],
    },

    // Rutas de cliente
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/orders' },
        { path: 'orders', name: 'orders', component: () => import('@/modules/orders/views/OrderListView.vue') },
        { path: 'orders/new', name: 'order-create', component: () => import('@/modules/orders/views/OrderCreateView.vue') },
        { path: 'orders/:id', name: 'order-detail', component: () => import('@/modules/orders/views/OrderDetailView.vue') },
      ],
    },

    // Rutas admin
    {
      path: '/admin',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/modules/admin/views/AdminDashboardView.vue') },
        { path: 'orders', name: 'admin-orders', component: () => import('@/modules/admin/views/AdminOrderListView.vue') },
        { path: 'orders/new', name: 'admin-order-create', component: () => import('@/modules/admin/views/AdminOrderCreateView.vue') },
        { path: 'orders/:id', name: 'admin-order-detail', component: () => import('@/modules/admin/views/AdminOrderDetailView.vue') },
        { path: 'payments', name: 'admin-payments', component: () => import('@/modules/admin/views/AdminPaymentsView.vue') },
        { path: 'users', name: 'admin-users', component: () => import('@/modules/admin/views/AdminUsersView.vue') },
        { path: 'config', name: 'admin-config', component: () => import('@/modules/admin/views/AdminConfigView.vue') },
        { path: 'printers', name: 'admin-printers', component: () => import('@/modules/admin/views/AdminPrintersView.vue') },
        { path: 'materials', name: 'admin-materials', component: () => import('@/modules/admin/views/AdminMaterialsView.vue') },
        { path: 'production', name: 'admin-production', component: () => import('@/modules/admin/views/AdminProductionView.vue') },
        { path: 'discounts', name: 'admin-discounts', component: () => import('@/modules/admin/views/AdminDiscountsView.vue') },
      ],
    },

    // Públicas (sin auth)
    { path: '/faq', name: 'faq', component: () => import('@/modules/faq/views/FAQView.vue') },
    { path: '/cotizar', name: 'public-quote', component: () => import('@/modules/quotes/views/PublicQuoteView.vue') },

    // 404
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  // Cargar usuario si hay token pero aún no tenemos info de rol
  if (to.meta.requiresAuth && auth.isAuthenticated && !auth.user) {
    try {
      const { getMe } = await import('@/modules/auth/services/authService')
      const user = await getMe()
      auth.setUser(user)
    } catch {
      await auth.logout()
      return { name: 'login' }
    }
  }

  // Admin que accede a rutas de cliente → redirigir a dashboard
  if (!to.meta.requiresAdmin && to.meta.requiresAuth && auth.isAdmin) {
    return { path: '/admin/dashboard' }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { path: '/orders' }
  }

  return true
})

export default router
