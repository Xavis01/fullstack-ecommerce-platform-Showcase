<template>
  <section class="min-h-screen bg-[#fffdf2] px-4 py-8 sm:px-6 sm:py-12 md:p-16">
    <div class="max-w-7xl mx-auto w-full">
      <!-- Loading State -->
      <div v-if="loadingScreen" class="flex flex-col items-center justify-center mt-12 md:mt-16 text-[#3a5528] gap-3">
        <LoaderCircle class="w-8 h-8 md:w-10 md:h-10 animate-spin" />
        <span class="text-sm md:text-base font-light italic tracking-wide">
          Carregando Produtos...
        </span>
      </div>

      <!-- Products Grid -->
      <div v-else-if="products.length > 0"
        class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4 md:gap-6 lg:gap-8">
        <div v-for="(product, index) in products" :key="product.id" class="relative"
          :draggable="editModeStore.isEditMode" @dragstart="onDragStart(index, $event)"
          @dragover.prevent="onDragOver(index)" @drop="onDrop(index)" @dragend="onDragEnd"
          :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
          <!-- Edit mode overlay -->
          <div v-if="editModeStore.isEditMode"
            class="absolute inset-0 z-20 rounded-sm pointer-events-none transition-all duration-200"
            :class="dragOverIndex === index ? 'ring-2 ring-[#861e1f] ring-offset-1 bg-[#861e1f]/10' : 'ring-1 ring-dashed ring-[#0f2301]/30'">
            <div
              class="absolute top-1 left-1 bg-[#0f2301]/70 backdrop-blur-[2px] rounded px-1.5 py-0.5 flex items-center gap-1">
              <GripVertical class="w-3 h-3 text-white" />
              <span class="text-[9px] text-white font-bold uppercase tracking-wider">#{{ index + 1 }}</span>
            </div>
          </div>

          <ProductCard :product="product" />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center mt-16 md:mt-24 text-[#8c9e78]">
        <p class="text-base md:text-lg font-light italic tracking-wide text-center">
          Nenhum produto disponível no momento.
        </p>
      </div>
    </div>

    <!-- Save Order Button (Edit Mode) -->
    <Teleport to="body">
      <Transition name="slide-up">
        <button v-if="editModeStore.isEditMode" @click="saveShopOrder" :disabled="isSavingOrder"
          class="fixed bottom-6 right-4 md:bottom-8 md:right-8 z-[200] flex items-center gap-2.5 px-5 py-3.5 bg-[#0f2301] text-[#fffdf2] rounded-full shadow-2xl font-bold text-xs uppercase tracking-widest hover:bg-[#1a3805] active:scale-95 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed">
          <Check v-if="!isSavingOrder" class="w-4 h-4" />
          <LoaderCircle v-else class="w-4 h-4 animate-spin" />
          {{ isSavingOrder ? 'Salvando...' : 'Salvar Alterações' }}
        </button>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import ProductCard from '@/components/shop/ProductCard.vue'
import { LoaderCircle, GripVertical, Check } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import { useEditModeStore } from '@/stores/editMode'

const loadingScreen = ref(false)
const toast = useToast()
const products = ref([])
const editModeStore = useEditModeStore()

// Drag-and-drop state
const dragFromIndex = ref(null)
const dragOverIndex = ref(null)
const isSavingOrder = ref(false)

const onDragStart = (index, event) => {
  dragFromIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOver = (index) => {
  dragOverIndex.value = index
}

const onDrop = (toIndex) => {
  if (dragFromIndex.value === null || dragFromIndex.value === toIndex) {
    dragOverIndex.value = null
    return
  }
  const updated = [...products.value]
  const [moved] = updated.splice(dragFromIndex.value, 1)
  updated.splice(toIndex, 0, moved)
  products.value = updated
  dragFromIndex.value = null
  dragOverIndex.value = null
}

const onDragEnd = () => {
  dragFromIndex.value = null
  dragOverIndex.value = null
}

const saveShopOrder = async () => {
  isSavingOrder.value = true
  try {
    const order = products.value.map(p => p.id)
    await api.put('/admin/products/shop/reorder', { order })
    toast.success('Ordem dos produtos salva com sucesso!')
    editModeStore.disableEditMode()
  } catch (e) {
    console.error(e)
    toast.error('Erro ao salvar ordem dos produtos')
  } finally {
    isSavingOrder.value = false
  }
}

const products_list = async () => {
  loadingScreen.value = true
  try {
    const res = await api.get('/products/list')
    products.value = res.data
  } catch (err) {
    console.error('Erro ao carregar produtos:', err)
    toast.error('Erro ao carregar produtos')
  } finally {
    loadingScreen.value = false
  }
}

onMounted(async () => {
  products_list()
})

</script>

<style scoped>
/* Slide-up transition for save button */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(120%);
  opacity: 0;
}
</style>
