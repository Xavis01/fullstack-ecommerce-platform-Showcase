<template>
  <div class="min-h-screen bg-[#fffdf2] font-montserrat text-[#0f2301]">

    <!-- Loading State -->
    <div v-if="loadingScreen" class="flex flex-col items-center justify-center min-h-[60vh] px-4">
      <div class="w-8 h-8 md:w-10 md:h-10 border-2 border-[#eaddcf] border-t-[#0f2301] rounded-full animate-spin mb-4">
      </div>
      <span class="text-[10px] md:text-xs uppercase tracking-[0.3em] font-bold text-[#3a5528] text-center">Carregando
        Coleção</span>
    </div>

    <!-- Product Content -->
    <div v-else-if="product" class="w-full px-4 py-8 sm:px-6 md:px-12 lg:px-24 md:py-12 lg:py-16">

      <!-- Main Grid Container: Stacked on mobile, side-by-side on lg -->
      <div class="flex flex-col lg:flex-row gap-8 md:gap-12 xl:gap-24">

        <!-- === GALLERY SECTION (Top on mobile, Left on desktop) === -->
        <div class="w-full lg:w-3/5 flex flex-col-reverse md:flex-row gap-3 sm:gap-4 md:gap-6 lg:gap-8">

          <!-- Thumbnails -->
          <div v-if="product.images && product.images.length > 1"
            class="flex md:flex-col gap-2 sm:gap-3 overflow-x-auto md:overflow-visible py-2 md:py-0 w-full md:w-20 lg:w-24 flex-shrink-0 scrollbar-hide">
            <button v-for="img in product.images" :key="img.id" @click="selectImage(img.url)"
              class="relative w-16 h-20 sm:w-20 sm:h-24 md:w-full md:h-28 flex-shrink-0 overflow-hidden transition-all duration-300 border"
              :class="currentImage === img.url ? 'border-[#0f2301]' : 'border-transparent opacity-60 hover:opacity-100'">
              <img :src="img.thumbnail_url || img.url" :alt="product.name" loading="lazy"
                class="w-full h-full object-cover grayscale-[20%] hover:grayscale-0 transition-all duration-500" />
            </button>
          </div>

          <!-- Main Image -->
          <div
            class="flex-1 aspect-[3/4] sm:aspect-[4/5] md:aspect-[3/4] relative overflow-hidden group bg-[#eaddcf]/20 w-full"
            @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
            <div 
              class="flex w-full h-full will-change-transform"
              :class="isDragging ? 'transition-none' : 'max-md:transition-transform max-md:duration-[400ms] max-md:ease-out'"
              :style="{ transform: `translateX(calc(-${Math.max(0, allImages.indexOf(currentImage))} * 100% + ${dragOffset}px))` }"
            >
              <div v-for="(img, idx) in allImages" :key="idx" class="w-full h-full flex-shrink-0 relative">
                <img :src="img" :alt="product.name"
                  class="w-full h-full object-cover transition-transform duration-[1500ms] ease-out lg:group-hover:scale-105"
                  @error="handleImageError" />
              </div>
            </div>
              
            <!-- Navigation Arrows -->
            <button v-if="allImages.length > 1" @click.stop="prevImage"
              class="absolute left-2 sm:left-4 top-1/2 -translate-y-1/2 w-8 h-8 md:w-10 md:h-10 bg-[#fffdf2]/90 hover:bg-[#fffdf2] text-[#0f2301] hidden md:flex items-center justify-center rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-lg border border-[#eaddcf] z-20">
              <ChevronLeft class="w-4 h-4 md:w-5 md:h-5" />
            </button>
            <button v-if="allImages.length > 1" @click.stop="nextImage"
              class="absolute right-2 sm:right-4 top-1/2 -translate-y-1/2 w-8 h-8 md:w-10 md:h-10 bg-[#fffdf2]/90 hover:bg-[#fffdf2] text-[#0f2301] hidden md:flex items-center justify-center rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-lg border border-[#eaddcf] z-20">
              <ChevronRight class="w-4 h-4 md:w-5 md:h-5" />
            </button>

            <div v-if="isNew"
              class="absolute top-4 left-4 md:top-6 md:left-6 bg-[#0f2301] text-[#fffdf2] px-2.5 py-1 md:px-3 md:py-1.5 text-[8px] md:text-[9px] font-bold tracking-[0.3em] uppercase z-20">
              Novo
            </div>
          </div>
        </div>

        <!-- === DETAILS SECTION (Bottom on mobile, Right on desktop) === -->
        <div class="w-full lg:w-2/5 flex flex-col pt-2 sm:pt-4 lg:pt-8 xl:pt-10">

          <!-- Header -->
          <div class="mb-6 md:mb-10">
            <p class="text-[9px] md:text-[10px] uppercase tracking-[0.3em] font-bold text-[#3a5528] mb-2 md:mb-4">
              {{ product.collection ? `Coleção ${product.collection}` : 'Coleção Exclusiva' }}
            </p>
            <h1
              class="text-3xl sm:text-4xl md:text-5xl font-light italic text-[#0f2301] mb-4 md:mb-6 tracking-tighter leading-tight">
              {{ product.name }}
            </h1>
            <p class="text-lg sm:text-xl md:text-2xl font-medium tracking-widest text-[#0f2301]">
              R$ {{ formatPrice(product.price) }}
            </p>
          </div>

          <!-- Divider -->
          <div class="w-full h-px bg-[#eaddcf] mb-6 md:mb-10"></div>

          <!-- Variants -->
          <div v-if="product.variants?.length" class="mb-8 md:mb-10">
            <div class="flex justify-between items-center mb-3 md:mb-4">
              <span class="text-[9px] md:text-[10px] uppercase font-bold tracking-[0.2em] text-[#0f2301]">Tamanho</span>
              <button v-if="selectedSize" @click="clearSelection"
                class="text-[9px] md:text-[10px] uppercase tracking-wider text-[#3a5528] hover:text-[#0f2301] underline decoration-[#eaddcf] hover:decoration-[#0f2301] transition-all p-2 -mr-2">
                Limpar
              </button>
            </div>

            <div class="flex flex-wrap gap-2 md:gap-3">
              <button v-for="variant in product.variants" :key="variant.id" @click="selectSize(variant)"
                :disabled="variant.stock <= 0"
                class="h-10 md:h-12 px-4 md:px-5 border text-[10px] md:text-xs font-bold tracking-widest uppercase transition-all duration-300"
                :class="[
                  selectedSize === variant.size
                    ? 'border-[#0f2301] bg-[#0f2301] text-[#fffdf2]'
                    : 'border-[#eaddcf] text-[#0f2301] hover:border-[#0f2301]',
                  variant.stock <= 0 ? 'opacity-50 !bg-gray-100 !text-gray-400 !border-gray-200 cursor-not-allowed hover:!border-gray-200' : ''
                ]">
                {{ variant.size }}
              </button>
            </div>

            <p v-if="selectedVariant && selectedVariant.stock < 5 && selectedVariant.stock > 0"
              class="mt-3 md:mt-4 text-[9px] md:text-[10px] uppercase tracking-wider text-[#9a382d] font-bold animate-pulse">
              Corra! Restam apenas {{ selectedVariant.stock }} unidades.
            </p>
          </div>

          <!-- Actions: Side-by-side on all screens -->
          <div class="flex flex-row gap-2 sm:gap-3 md:gap-4 h-12 md:h-14 mb-8 md:mb-10">
            <!-- Quantity -->
            <div
              class="flex w-[110px] sm:w-28 md:w-32 border border-[#0f2301] h-full items-center justify-between px-1 sm:px-2 flex-shrink-0"
              :class="{ 'opacity-50 pointer-events-none': selectedVariant && selectedVariant.stock <= 0 }">
              <button @click="decreaseQty"
                class="w-8 h-8 flex items-center justify-center text-[#0f2301] hover:bg-[#eaddcf] active:scale-90 transition-all rounded-sm">
                <Minus class="w-4 h-4" />
              </button>
              <input type="text" readonly :value="quantity"
                class="flex-1 text-center bg-transparent focus:outline-none text-[#0f2301] font-medium text-sm w-full" />
              <button @click="increaseQty"
                class="w-8 h-8 flex items-center justify-center text-[#0f2301] hover:bg-[#eaddcf] active:scale-90 transition-all rounded-sm">
                <Plus class="w-4 h-4" />
              </button>
            </div>

            <!-- Add to Cart CTA -->
            <button @click="addToCart"
              :disabled="loading || !selectedSize || (selectedVariant && selectedVariant.stock <= 0)"
              class="flex-1 h-full bg-[#0f2301] text-[#fffdf2] border border-[#0f2301] text-[8px] sm:text-[9px] md:text-[10px] font-bold uppercase tracking-[0.1em] sm:tracking-[0.2em] md:tracking-[0.3em] active:scale-[0.98] lg:hover:bg-[#fffdf2] lg:hover:text-[#0f2301] disabled:!bg-gray-200 disabled:!border-gray-200 disabled:!text-gray-500 disabled:cursor-not-allowed transition-all duration-300 md:duration-500 flex items-center justify-center gap-2 md:gap-3">
              <div v-if="loading"
                class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              <span v-else>{{ selectedVariant && selectedVariant.stock <= 0 ? 'Esgotado' : 'Adicionar à Sacola'
                  }}</span>
            </button>
          </div>

          <div v-if="!hasStock"
            class="text-center py-3 md:py-4 mb-8 md:mb-10 text-[#9a382d] text-[10px] md:text-xs font-bold uppercase tracking-widest border border-[#9a382d]/30 bg-[#9a382d]/5">
            Produto Esgotado
          </div>

          <!-- Shipping Box Premium -->
          <div class="border border-[#eaddcf] p-4 sm:p-5 md:p-6 mb-8 md:mb-12 bg-[#fffdf2]">
            <label
              class="block text-[9px] md:text-[10px] font-bold text-[#0f2301] uppercase tracking-[0.2em] mb-3 md:mb-4">
              Calcular Entrega
            </label>
            <div class="relative flex items-center border-b border-[#0f2301] pb-2">
              <input v-model="cep" type="text" placeholder="00000-000"
                class="w-full bg-transparent text-sm focus:outline-none placeholder-[#c7c6bd] text-[#0f2301] tracking-widest pr-8"
                @input="formatCep" @keyup.enter="calculateShipping" />
              <div v-if="loadingShipping"
                class="absolute right-0 w-4 h-4 border-2 border-[#0f2301] border-t-transparent rounded-full animate-spin">
              </div>
            </div>

            <!-- Shipping Results -->
            <div v-if="shippingOptions.length > 0" class="mt-4 space-y-2">
              <div v-for="opt in shippingOptions" :key="opt.id"
                class="flex flex-col sm:flex-row sm:items-center justify-between py-3 px-3 sm:px-4 bg-[#faf9f0] border border-[#eaddcf] rounded-lg gap-2 sm:gap-0">
                <div class="flex items-start sm:items-center gap-3">
                  <Truck class="w-4 h-4 text-[#3a5528] flex-shrink-0 mt-0.5 sm:mt-0" />
                  <div>
                    <p class="text-xs sm:text-sm font-medium text-[#0f2301] leading-tight">{{ opt.name }}</p>
                    <p class="text-[10px] sm:text-xs text-[#8c9e78] font-light mt-0.5">{{ opt.delivery_time }} dias
                      úteis</p>
                  </div>
                </div>
                <span class="font-medium text-[#0f2301] text-xs sm:text-sm whitespace-nowrap sm:text-right">R$ {{
                  opt.price.toFixed(2) }}</span>
              </div>

              <!-- Retirada em Mãos -->
              <div
                class="flex flex-col sm:flex-row sm:items-center justify-between py-3 px-3 sm:px-4 bg-[#faf9f0] border border-[#eaddcf] rounded-lg gap-2 sm:gap-0">
                <div class="flex items-start sm:items-center gap-3">
                  <MapPin class="w-4 h-4 text-[#3a5528] flex-shrink-0 mt-0.5 sm:mt-0" />
                  <div>
                    <p class="text-xs sm:text-sm font-medium text-[#0f2301] leading-tight">Retirada</p>
                    <p class="text-[10px] sm:text-xs text-[#8c9e78] font-light mt-0.5">Jardim Camburi - Vitória, ES</p>
                  </div>
                </div>
                <span
                  class="font-medium text-[#3a5528] text-xs sm:text-sm whitespace-nowrap sm:text-right">Grátis</span>
              </div>
            </div>

            <!-- Shipping Error -->
            <p v-if="shippingError" class="mt-3 text-xs text-[#9a382d] font-light">{{ shippingError }}</p>
          </div>

          <!-- Product Description -->
          <div class="mt-2 md:mt-4 pt-6 md:pt-8 border-t border-[#eaddcf]">
            <h3
              class="text-[9px] md:text-[10px] font-bold uppercase tracking-[0.2em] md:tracking-[0.3em] text-[#0f2301] mb-4 md:mb-6">
              Descrição</h3>
            <div
              class="font-light leading-[1.8] md:leading-[2] text-[#3a5528] text-sm md:text-base whitespace-pre-line">
              {{ product.description }}
            </div>
          </div>
        </div>
      </div>
    </div> <!-- Fechamento da DIV v-else-if="product" -->

    <!-- Error State -->
    <div v-else class="py-32 md:py-48 flex flex-col items-center justify-center text-center px-4">
      <h2 class="text-2xl md:text-3xl font-light italic text-[#0f2301] mb-6 tracking-tighter">Coleção Inacessível</h2>
      <router-link to="/produtos"
        class="px-8 md:px-10 py-3 md:py-4 border border-[#0f2301] text-[9px] md:text-[10px] font-bold text-[#0f2301] uppercase tracking-[0.2em] md:tracking-[0.3em] w-full max-w-[200px] hover:bg-[#0f2301] hover:text-[#fffdf2] transition-colors duration-500">
        Retornar à Loja
      </router-link>
    </div>

  </div> <!-- Fechamento da root min-h-screen DIV -->
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, Minus, Plus, Truck, MapPin } from 'lucide-vue-next'
import api from '@/api'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref(null)
const selectedSize = ref(null)
const selectedVariant = ref(null)
const currentImage = ref(null)
const loadingScreen = ref(false)
const loading = ref(false)
const quantity = ref(1)
const cep = ref('')
const activeTab = ref('desc')
const loadingShipping = ref(false)
const shippingOptions = ref([])
const shippingError = ref('')

const hasStock = computed(() => product.value?.variants?.some(v => v.stock > 0))
const isNew = computed(() => {
  if (!product.value) return false
  const diff = new Date() - new Date(product.value.created_at)
  return Math.ceil(diff / (1000 * 60 * 60 * 24)) <= 30
})

// Image Navigation & Swipe Logic
const allImages = computed(() => {
  if (product.value?.images && product.value.images.length > 0) {
    return product.value.images.map(img => img.url)
  }
  return product.value && product.value.image_url ? [product.value.image_url] : []
})

const selectImage = (url) => {
  currentImage.value = url
}

const currentIndex = computed(() => {
  const idx = allImages.value.indexOf(currentImage.value)
  return idx === -1 ? 0 : idx
})

const nextImage = () => {
  if (allImages.value.length <= 1) return
  let nextIndex = currentIndex.value + 1
  if (nextIndex >= allImages.value.length) nextIndex = 0
  currentImage.value = allImages.value[nextIndex]
}

const prevImage = () => {
  if (allImages.value.length <= 1) return
  let prevIndex = currentIndex.value - 1
  if (prevIndex < 0) prevIndex = allImages.value.length - 1
  currentImage.value = allImages.value[prevIndex]
}

const touchStartX = ref(0)
const touchStartY = ref(0)
const isDragging = ref(false)
const dragOffset = ref(0)
let swipeAxisLocked = false
let isHorizontalDrag = false

const onTouchStart = (e) => {
  touchStartX.value = e.changedTouches[0].screenX
  touchStartY.value = e.changedTouches[0].screenY
  isDragging.value = true
  dragOffset.value = 0
  swipeAxisLocked = false
  isHorizontalDrag = false
}

const onTouchMove = (e) => {
  if (!isDragging.value || (swipeAxisLocked && !isHorizontalDrag)) return
  
  const currentX = e.changedTouches[0].screenX
  const currentY = e.changedTouches[0].screenY
  
  const xDiff = currentX - touchStartX.value
  const yDiff = currentY - touchStartY.value
  
  if (!swipeAxisLocked) {
    if (Math.abs(xDiff) > 10 || Math.abs(yDiff) > 10) {
      swipeAxisLocked = true
      if (Math.abs(xDiff) > Math.abs(yDiff)) {
        isHorizontalDrag = true
      }
    }
  }

  if (isHorizontalDrag) {
    // Feel de resistência visual nas pontas
    let newOffset = xDiff
    if (currentIndex.value === 0 && newOffset > 0) newOffset = newOffset * 0.3
    if (currentIndex.value === allImages.value.length - 1 && newOffset < 0) newOffset = newOffset * 0.3
    dragOffset.value = newOffset
    
    // Evita o scroll padrão da página
    if (e.cancelable) e.preventDefault()
  }
}

const onTouchEnd = (e) => {
  if (!isDragging.value) return
  isDragging.value = false
  
  if (isHorizontalDrag) {
    // threshold visual (exemplo dinâmico dependendo da tela)
    const swipeThreshold = window.innerWidth * 0.15 
    if (dragOffset.value > swipeThreshold) {
      prevImage()
    } else if (dragOffset.value < -swipeThreshold) {
      nextImage()
    }
  }
  
  dragOffset.value = 0
  isHorizontalDrag = false
  swipeAxisLocked = false
}

watch(currentImage, () => { /* Logic ok */ })

onMounted(async () => {
  loadingScreen.value = true
  try {
    const res = await api.get(`/products/list/${route.params.id}`)
    product.value = res.data
    currentImage.value = product.value.image_url
    if (product.value.variants?.length) {
      const available = product.value.variants.find(v => v.stock > 0)
      selectSize(available || product.value.variants[0])
    }
  } catch (e) {
    // Bloqueia acesso a produtos "EM BREVE" (403) ou não encontrados (404)
    if (e.response?.status === 403 || e.response?.status === 404) {
      router.replace('/produtos')
      return
    }
    console.error(e)
  } finally {
    loadingScreen.value = false
  }
})

const selectSize = (variant) => {
  selectedSize.value = variant.size
  selectedVariant.value = variant
}

const clearSelection = () => {
  selectedSize.value = null
  selectedVariant.value = null
  // Opcional: Auto-scroll to top ou focar em algo
}

const sizeMap = {
  'P': 'Small - P', 'M': 'Medium - M', 'G': 'Large - G',
  'GG': 'XLarge - GG', 'XGG': 'XXLarge - XGG',
  'S': 'Small - S', 'L': 'Large - L', 'XL': 'XLarge - XL', 'XXL': 'XXLarge - XXL'
}

function getSizeLabel(size) {
  return sizeMap[size] || size
}

function formatPrice(val) {
  return Number(val).toFixed(2).replace('.', ',')
}

function formatCep() {
  let v = cep.value.replace(/\D/g, '')
  if (v.length > 5) v = v.slice(0, 5) + '-' + v.slice(5, 8)
  cep.value = v

  if (v.replace(/\D/g, '').length === 8) {
    calculateShipping()
  }
}

function decreaseQty() { if (quantity.value > 1) quantity.value-- }
function increaseQty() { quantity.value++ }

async function addToCart() {
  if (!selectedSize.value) return
  loading.value = true
  try {
    const vId = selectedVariant.value.product_variant_id || selectedVariant.value.id
    await cartStore.addItem(product.value, vId, selectedSize.value, quantity.value)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Handler para erro de imagem
const handleImageError = (e) => {
  // e.target.src = '/placeholder.png' // Opcional
}

async function calculateShipping() {
  const cleanCep = cep.value.replace(/\D/g, '')
  if (cleanCep.length < 8 || !product.value) return

  loadingShipping.value = true
  shippingError.value = ''
  shippingOptions.value = []

  try {
    const res = await api.post('/shipping/calculate', {
      cep: cleanCep,
      products: [{ product_id: product.value.id, quantity: quantity.value }]
    })
    shippingOptions.value = res.data.shipping_options
  } catch (err) {
    shippingError.value = err.response?.data?.error || 'Erro ao calcular frete. Verifique o CEP.'
  } finally {
    loadingShipping.value = false
  }
}
</script>

<style scoped>
/* Tailwind utilities handle almost everything */
</style>