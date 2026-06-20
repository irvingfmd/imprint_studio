<template>
  <div ref="container" class="w-full rounded-lg overflow-hidden bg-gray-900 border border-gray-700" :style="{ height: height }">
    <div v-if="loading" class="flex items-center justify-center h-full text-gray-500 text-sm">Cargando modelo 3D...</div>
    <div v-if="error" class="flex items-center justify-center h-full text-red-400 text-xs px-4 text-center">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { STLLoader } from 'three/addons/loaders/STLLoader.js'

const props = withDefaults(defineProps<{
  url: string
  height?: string
}>(), {
  height: '300px',
})

const container = ref<HTMLDivElement | null>(null)
const loading = ref(true)
const error = ref('')

let renderer: THREE.WebGLRenderer | null = null
let animationId: number | null = null

function init() {
  if (!container.value) return

  const width = container.value.clientWidth
  const height = container.value.clientHeight

  const scene = new THREE.Scene()
  scene.background = new THREE.Color(0x111827)

  const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 2000)
  camera.position.set(0, 0, 100)

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.value.appendChild(renderer.domElement)

  const controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(50, 50, 50)
  scene.add(directionalLight)
  const backLight = new THREE.DirectionalLight(0xffffff, 0.3)
  backLight.position.set(-50, -50, -50)
  scene.add(backLight)

  const loader = new STLLoader()
  loader.load(
    props.url,
    (geometry) => {
      geometry.computeBoundingBox()
      geometry.center()

      const material = new THREE.MeshPhongMaterial({
        color: 0x2563eb,
        specular: 0x444444,
        shininess: 30,
      })
      const mesh = new THREE.Mesh(geometry, material)
      scene.add(mesh)

      const box = new THREE.Box3().setFromObject(mesh)
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      camera.position.set(0, 0, maxDim * 1.8)
      controls.update()

      loading.value = false
    },
    undefined,
    () => {
      error.value = 'No se pudo cargar el modelo 3D.'
      loading.value = false
    },
  )

  function animate() {
    animationId = requestAnimationFrame(animate)
    controls.update()
    renderer!.render(scene, camera)
  }
  animate()

  const resizeObserver = new ResizeObserver(() => {
    if (!container.value || !renderer) return
    const w = container.value.clientWidth
    const h = container.value.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  })
  resizeObserver.observe(container.value)
}

onMounted(init)

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) {
    renderer.dispose()
    renderer.domElement.remove()
  }
})

watch(() => props.url, () => {
  if (renderer) {
    renderer.dispose()
    renderer.domElement.remove()
    renderer = null
  }
  loading.value = true
  error.value = ''
  init()
})
</script>
