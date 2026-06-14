<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center p-6">
    <div class="text-center max-w-md">
      <p class="text-7xl font-bold text-gray-700 mb-4">404</p>
      <h1 class="text-xl font-semibold text-white mb-2">Página no encontrada</h1>
      <p class="text-gray-400 text-sm mb-8">La página que buscas no existe o fue movida.</p>
      <RouterLink
        to="/"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors"
      >
        ← Volver al inicio
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>
