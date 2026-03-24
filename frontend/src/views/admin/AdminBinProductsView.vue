<template>
  <div class="min-h-screen font-montserrat bg-[#fffdf2] pb-20">

    <!-- Header -->
    <div class="pt-8 px-10 mb-6">
      <div class="flex items-center gap-3 mb-1">
        <router-link to="/admin/produtos">
          <button title="Voltar"
            class="flex items-center justify-center w-8 h-8 rounded-lg border border-[#0f2301]/30 text-[#3a5528] hover:bg-[#0f2301]/60 transition-all">
            <ChevronLeft class="w-4 h-4" />
          </button>
        </router-link>
        <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic tracking-wide flex items-center gap-3">
          Lixeira de Produtos
          <Trash2 class="w-5 h-5" />
        </h1>
      </div>
      <p class="text-[#8c9e78] font-light pl-11">Produtos removidos ficam aqui antes de serem excluídos permanentemente
      </p>
    </div>

    <!-- Toolbar -->
    <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <!-- Search Bar -->
      <div class="relative group w-96">
        <input v-model="searchTerm" type="text" placeholder="Pesquisar por nome..."
          class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
        <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
      </div>

      <!-- Botões direita -->
      <div class="flex gap-2 items-center">
        <button :disabled="products.length === 0" :class="products.length > 0
          ? 'border-[#0f2301]/40 text-[#3a5528] hover:bg-[#0f2301]/50'
          : 'border-[#0f2301]/20 text-[#3a5528]/40 cursor-not-allowed'"
          class="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-light italic tracking-wide transition-all"
          @click="openRestoreAllModal">
          <RotateCcw class="w-4 h-4" />
          Restaurar Tudo
        </button>

        <div class="w-px h-6 bg-[#0f2301]/20 mx-1"></div>

        <button :disabled="products.length === 0" :class="products.length > 0
          ? 'border-[#9a382d]/40 text-[#9a382d] hover:bg-red-50'
          : 'border-[#9a382d]/20 text-[#9a382d]/40 cursor-not-allowed'"
          class="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-light italic tracking-wide transition-all"
          @click="openDeleteAllModal">
          <Trash2 class="w-4 h-4" />
          Limpar Lixeira
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <LoaderCircle class="animate-spin text-[#3a5528] w-10 h-10" />
    </div>

    <!-- Table -->
    <div v-else-if="products.length > 0" class="px-10">
      <div class="bg-white/50 backdrop-blur-sm rounded-lg overflow-hidden shadow-sm border border-[#eaddcf]">
        <table class="w-full text-sm">
          <thead class="bg-[#e4e3db] border-b border-[#eaddcf]">
            <tr>
              <th
                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                #ID</th>
              <th
                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                Imagem</th>
              <th
                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                Nome</th>
              <th
                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                Preço</th>
              <th
                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                Estoque</th>

              <th
                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                Ações</th>
              <th
                class="py-4 px-6 text-center font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" class="custom-checkbox w-4 h-4"
                  title="Marcar/Desmarcar todos" />
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#eaddcf]">
            <tr v-for="product in filteredProducts" :key="product.id" class="bin-row">
              <td class="py-4 px-6 text-[#3a5528] font-light text-sm">{{ product.id }}</td>
              <td class="py-4 px-6">
                <img v-if="product.cover_images && product.cover_images.length > 0"
                  :src="product.cover_images[0].image_public_url" :alt="product.name"
                  class="w-14 h-14 object-cover rounded-lg border border-[#0f2301]/20 shadow-sm opacity-70" />
                <div v-else
                  class="w-14 h-14 bg-[#0f2301] flex items-center justify-center rounded-lg border border-[#0f2301]/20 text-[#fffdf2]/50">
                  <ImageOff class="w-5 h-5" />
                </div>
              </td>
              <td class="py-4 px-6 text-[#3a5528] font-medium">{{ product.name }}</td>
              <td class="py-4 px-6 text-[#6b8555] font-light">R$ {{ product.price.toFixed(2) }}</td>
              <td class="py-4 px-6 text-[#6b8555] font-light">{{ product.stock }}</td>

              <td class="py-4 px-6">
                <div class="flex gap-3 items-center">
                  <button @click="openViewModal(product)" title="Ver Detalhes"
                    class="text-[#3a5528] hover:text-[#2c3e20] hover:scale-110 transition-all p-1">
                    <FolderSearch :size="17" />
                  </button>
                  <button title="Restaurar" @click="openRestoreModal(product.id)"
                    class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1">
                    <RotateCcw :size="17" />
                  </button>
                  <button title="Deletar Permanentemente" :disabled="product.has_orders || product.has_cart_items"
                    @click="openDeleteModal(product.id)"
                    :class="['text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1', product.has_orders || product.has_cart_items ? 'opacity-30 cursor-not-allowed' : '']">
                    <Trash2 :size="17" />
                  </button>
                  <div v-if="product.has_orders || product.has_cart_items" class="relative group">
                    <CircleAlert class="h-5 w-5 text-yellow-600 hover:text-yellow-700 cursor-pointer" />
                    <div
                      class="absolute top-7 right-0 w-64 text-xs bg-yellow-50 text-yellow-800 border border-yellow-300 px-3 py-2 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-300 z-50">
                      Não é possível deletar esse produto permanentemente, pois ele está associado a um
                      <strong>carrinho</strong> ou um <strong>pedido</strong>.
                    </div>
                  </div>
                </div>
              </td>
              <td class="py-4 px-6 text-center">
                <input type="checkbox" v-model="selectedIds" :value="product.id" class="custom-checkbox w-4 h-4" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="px-10 text-center text-[#3a5528] mt-12 italic text-sm">
      Lixeira vazia.
    </div>

    <!-- Floating bulk restore -->
    <div class="fixed bottom-8 right-12 flex gap-3 z-50">
      <button v-if="selectedIds.length >= 1" @click="openRestoreMultiple(selectedIds)"
        class="px-6 py-3 bg-[#0f2301] text-[#fffdf2] rounded-xl shadow-xl hover:bg-[#0f2301]/90 transition-all text-sm italic tracking-wide">
        Restaurar {{ selectedIds.length }} produto{{ selectedIds.length > 1 ? 's' : '' }}
      </button>
      <button v-if="selectedIds.length > 0" @click="cancelSelect"
        class="px-6 py-3 bg-[#0f2301]/50 text-[#fffdf2] rounded-xl shadow-xl hover:bg-[#0f2301]/70 transition-all text-sm italic tracking-wide">
        Cancelar
      </button>
    </div>

    <ConfirmHardDeleteModal :isOpen="showDeleteModal" :productId="selectedProductId" @close="closeDeleteModal"
      @deleted="handleDeleted" />
    <ConfirmHardDeleteAllModal :isOpen="showDeleteAllModal" @close="closeDeleteAllModal" @deleted="handleDeletedAll" />
    <ConfirmRestoreModal :isOpen="showRestoreModal" :productId="selectedProductId" @close="closeRestoreModal"
      @restaured="handleRestaured" />
    <ConfirmRestoreAllModal :isOpen="showRestoreAllModal" @close="closeRestoreAllModal"
      @restaured="handleRestauredAll" />
    <ProductViewModal :isOpen="showViewModal" :product="selectedProduct" @close="showViewModal = false" />
  </div>
</template>

<script setup>
import { Trash2, RotateCcw, Eye, ChevronLeft, CircleAlert, FolderSearch, EyeOff, LoaderCircle, ImageOff, Search } from 'lucide-vue-next'
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import ConfirmRestoreModal from '@/components/admin/Products/trash/ConfirmRestoreModal.vue'
import ConfirmRestoreAllModal from '../../components/admin/Products/trash/ConfirmRestoreAllModal.vue'
import ConfirmHardDeleteModal from '../../components/admin/Products/trash/ConfirmHardDeleteModal.vue'
import ConfirmHardDeleteAllModal from '../../components/admin/Products/trash/ConfirmHardDeleteAllModal.vue'
import ProductViewModal from '@/components/admin/Products/ProductViewModal.vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'

const toast = useToast()
const showRestoreModal = ref(false)
const showRestoreAllModal = ref(false)
const showDeleteModal = ref(false)
const showDeleteAllModal = ref(false)
const showViewModal = ref(false)
const selectedProductId = ref(null)
const selectedProduct = ref(null)
const userStore = useUserStore()
const products = ref([])
const loading = ref(true)
const router = useRouter()
const selectedIds = ref([])
const searchTerm = ref('')

const filteredProducts = computed(() => {
  if (!searchTerm.value) return products.value
  const term = searchTerm.value.toLowerCase()
  return products.value.filter(p => p.name?.toLowerCase().includes(term))
})

const allSelected = computed(() => {
  return filteredProducts.value.length > 0 && selectedIds.value.length === filteredProducts.value.length
})

function toggleSelectAll(event) {
  if (event.target.checked) {
    selectedIds.value = filteredProducts.value.map(p => p.id)
  } else {
    selectedIds.value = []
  }
}

function cancelSelect() {
  selectedIds.value = []
}

function openRestoreMultiple(ids) {
  toast.info('Funcionalidade de restauração múltipla será implementada em breve')
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await api.get(`/admin/products/list/bin`)
    products.value = res.data
  } catch (err) {
    console.error(err)
    if (!userStore.is_admin && !userStore.is_logged) {
      toast.error('Sessão expirada, faça Login novamente')
      router.push('/login')
    } else {
      toast.error('Erro ao buscar produtos')
    }
  } finally {
    loading.value = false
  }
}

function openDeleteModal(productId) {
  selectedProductId.value = productId
  showDeleteModal.value = true
}

function handleDeleted() {
  selectedProductId.value = null
  showDeleteModal.value = false
  fetchProducts()
}

function closeDeleteModal() {
  showDeleteModal.value = false
}

function openDeleteAllModal() {
  showDeleteAllModal.value = true
}

function handleDeletedAll() {
  showDeleteAllModal.value = false
  fetchProducts()
}

function closeDeleteAllModal() {
  showDeleteAllModal.value = false
}

function openRestoreModal(productId) {
  selectedProductId.value = productId
  showRestoreModal.value = true
}

function handleRestaured() {
  selectedProductId.value = null
  showRestoreModal.value = false
  fetchProducts()
}

function closeRestoreModal() {
  showRestoreModal.value = false
}

function openRestoreAllModal() {
  showRestoreAllModal.value = true
}

function handleRestauredAll() {
  showRestoreAllModal.value = false
  fetchProducts()
}

function closeRestoreAllModal() {
  showRestoreAllModal.value = false
}

function openViewModal(product) {
  selectedProduct.value = product
  showViewModal.value = true
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.bin-row {
  background-color: #ffffff;
  transition: background-color 0.15s ease;
}

.bin-row:hover {
  background-color: #f0efe9;
}

.custom-checkbox {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  width: 1rem;
  height: 1rem;
  border: 2px solid #0f2301;
  border-radius: 0.25rem;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.custom-checkbox:hover {
  border-color: #0f2301;
}

.custom-checkbox:checked {
  background-color: #0f2301;
  border-color: #0f2301;
}

.custom-checkbox:checked::after {
  content: '';
  position: absolute;
  left: 0.25rem;
  top: 0.05rem;
  width: 0.35rem;
  height: 0.6rem;
  border: solid #0f2301;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-checkbox:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
