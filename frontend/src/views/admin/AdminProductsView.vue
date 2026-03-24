<!-- frontend\src\views\admin\AdminProductsView.vue -->

<template>
  <div class="min-h-screen font-montserrat bg-[#fffdf2] pb-20">

    <!-- Header -->
    <div class="pt-8 px-10 mb-6">
      <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">Gerenciar Produtos
      </h1>
      <p class="text-[#8c9e78] font-light">Gerencie os produtos disponíveis na loja</p>
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
        <router-link to="/admin/produtos/lixeira">
          <button
            class="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#9a382d]/40 text-[#9a382d] text-sm font-light italic tracking-wide hover:bg-red-50 transition-all">
            <Trash2 class="w-4 h-4" />
            Lixeira
          </button>
        </router-link>

        <div class="w-px h-6 bg-[#0f2301]/20 mx-1"></div>

        <button
          class="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm"
          @click="openCreateModal">
          <span class="text-base leading-none">+</span> Novo Produto
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
                Status</th>
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
            <tr v-for="product in filteredProducts" :key="product.id" class="product-row">
              <td class="py-4 px-6 text-[#3a5528] font-light text-sm">{{ product.id }}</td>
              <td class="py-4 px-6">
                <img v-if="product.cover_images && product.cover_images.length > 0"
                  :src="product.cover_images[0].image_public_url" :alt="product.name"
                  class="w-14 h-14 object-cover rounded-lg border border-[#0f2301]/20 shadow-sm" />
                <div v-else
                  class="w-14 h-14 bg-[#0f2301] flex items-center justify-center rounded-lg border border-[#0f2301]/20 text-[#fffdf2]/50">
                  <ImageOff class="w-5 h-5" />
                </div>
              </td>
              <td class="py-4 px-6 text-[#3a5528] font-medium">{{ product.name }}</td>
              <td class="py-4 px-6 text-[#6b8555] font-light">R$ {{ product.price.toFixed(2) }}</td>
              <td class="py-4 px-6 text-[#6b8555] font-light">{{ product.stock }}</td>
              <td class="py-4 px-6">
                <button @click="openVisibilityModal(product)"
                  class="hover:scale-110 transition-all duration-200 cursor-pointer p-1.5 rounded-lg hover:bg-[#0f2301]/10"
                  :title="product.is_public ? 'Público (Clique para ocultar)' : 'Privado (Clique para publicar)'">
                  <Eye v-if="product.is_public" class="w-5 h-5" style="color: #0f2301;" />
                  <EyeOff v-else class="w-5 h-5" style="color: #9a382d;" />
                </button>
                <div v-if="product.is_scheduled"
                  class="flex items-center gap-1 mt-1 text-xs italic text-yellow-700 bg-yellow-100 px-2 py-0.5 rounded-full w-fit">
                  <CalendarClock class="w-3 h-3" />
                  <span>Agendado</span>
                </div>
              </td>
              <td class="py-4 px-6">
                <div class="flex gap-3 items-center">
                  <button title="Agendar Publicação"
                    class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                    @click="openScheduleModal(product)">
                    <CalendarClock :size="17" />
                  </button>
                  <button title="Ver Detalhes"
                    class="text-[#0f2301] hover:text-[#2c3e20] hover:scale-110 transition-all p-1"
                    @click="openViewModal(product)">
                    <FolderSearch :size="17" />
                  </button>
                  <button title="Editar" class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                    @click="openEditModal(product)">
                    <Pencil :size="17" />
                  </button>
                  <button title="Duplicar"
                    class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                    @click="openDuplicateModal(product)">
                    <Copy :size="17" />
                  </button>
                  <button v-if="product.is_active" title="Deletar" @click="openDeleteModal(product.id)"
                    class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1">
                    <Trash2 :size="17" />
                  </button>
                  <button v-else title="Restaurar" @click="openRestoreModal(product.id)"
                    class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1">
                    <RotateCcw :size="17" />
                  </button>
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
      Nenhum produto cadastrado ainda.
    </div>

    <!-- Floating bulk delete -->
    <div class="fixed bottom-8 right-12 flex gap-3 z-50">
      <button v-if="selectedIds.length >= 1" @click="openDeleteMultiple(selectedIds)"
        class="px-6 py-3 bg-[#9a382d] text-[#fffdf2] rounded-xl shadow-xl hover:bg-[#9a382d]/90 transition-all text-sm italic tracking-wide">
        Deletar {{ selectedIds.length }} produto{{ selectedIds.length > 1 ? 's' : '' }}
      </button>
      <button v-if="selectedIds.length > 0" @click="cancelSelect"
        class="px-6 py-3 bg-[#0f2301] text-[#fffdf2] rounded-xl shadow-xl hover:bg-[#0f2301]/70 transition-all text-sm italic tracking-wide">
        Cancelar
      </button>
    </div>

    <!-- Modals -->
    <ProductCreateModal :isOpen="showCreateModal" :initialProduct="duplicateProduct" @close="closeCreateModal"
      @productCreated="handleProductCreated" />
    <ConfirmDeleteModal :isOpen="showDeleteModal" :productId="selectedProductId" @close="closeDeleteModal"
      @deleted="handleDeleted" />
    <ConfirmMultipleDelete :isOpen="showDeleteMultipleModal" :productIds="selectedProductIds"
      @close="closeDeleteMultipleModal" @deleted="handleDeletedMultiple" />
    <ConfirmRestoreModal :isOpen="showRestoreModal" :productId="selectedProductId" @close="closeRestoreModal"
      @restaured="handleRestaured" />
    <ProductEditModal :isOpen="showEditModal" :product="selectedProductId" @close="closeEditModal"
      @productUpdated="handleProductUpdated" />
    <ProductViewModal :isOpen="showViewModal" :product="selectedProductId" @close="showViewModal = false" />
    <ProductScheduleModal :isOpen="showScheduleModal" :product="selectedProductForSchedule" @close="closeScheduleModal"
      @updated="handleScheduleUpdated" />
    <ConfirmToggleVisibilityModal :isOpen="showVisibilityModal" :product="selectedProduct"
      :newStatus="pendingVisibilityStatus" @close="showVisibilityModal = false"
      @confirmed="handleVisibilityConfirmed" />
  </div>
</template>

<script setup>
import { Trash2, Pencil, Eye, Copy, LoaderCircle, RotateCcw, FolderSearch, EyeOff, ImageOff, Image, CalendarClock, Search } from 'lucide-vue-next'
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import ProductCreateModal from '@/components/admin/Products/ProductCreateModal.vue'
import ProductEditModal from '@/components/admin/Products/ProductEditModal.vue'
import ConfirmDeleteModal from '@/components/admin/Products/ConfirmDeleteModal.vue'
import ConfirmRestoreModal from '@/components/admin/Products/trash/ConfirmRestoreModal.vue'
import ConfirmMultipleDelete from '../../components/admin/Products/ConfirmMultipleDelete.vue'
import ProductViewModal from '@/components/admin/Products/ProductViewModal.vue'
import ProductScheduleModal from '@/components/admin/Products/ProductScheduleModal.vue'
import ConfirmToggleVisibilityModal from '@/components/admin/Products/ConfirmToggleVisibilityModal.vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'

const toast = useToast()
const showRestoreModal = ref(false)
const showDeleteModal = ref(false)
const selectedProductId = ref(null)
const showCreateModal = ref(false)
const userStore = useUserStore()
const products = ref([])
const statusFilter = ref('ativo')
const loading = ref(true)
const searchTerm = ref('')
const router = useRouter()
const showEditModal = ref(false)
const duplicateProduct = ref(null)
const selectedIds = ref([])
const showDeleteMultipleModal = ref(false)
const selectedProductIds = ref([])
const showViewModal = ref(false)

const showScheduleModal = ref(false)
const selectedProductForSchedule = ref(null)
const showVisibilityModal = ref(false)
const selectedProduct = ref(null)
const pendingVisibilityStatus = ref(false)

function openScheduleModal(product) {
  selectedProductForSchedule.value = product
  showScheduleModal.value = true
}

function closeScheduleModal() {
  showScheduleModal.value = false
  selectedProductForSchedule.value = null
}

function handleScheduleUpdated() {
  fetchProducts()
}

// Abrir modal de confirmação de visibilidade
function openVisibilityModal(product) {
  selectedProduct.value = product
  pendingVisibilityStatus.value = !product.is_public // Inverter o status atual
  showVisibilityModal.value = true
}

// Após confirmação, atualizar o produto
async function handleVisibilityConfirmed() {
  await fetchProducts()
  selectedProduct.value = null
}

function openViewModal(product) {
  selectedProductId.value = product
  showViewModal.value = true
}

function cancelSelect() {
  selectedIds.value = []        // limpa seleção dos checkboxes
  selectedProductIds.value = [] // opcional: reseta múltiplos
}

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
    // Seleciona todos os IDs dos produtos
    selectedIds.value = products.value.map(p => p.id)
  } else {
    // Desmarca tudo
    selectedIds.value = []
  }
}




function openDeleteMultiple(ids) {
  selectedProductIds.value = ids
  showDeleteMultipleModal.value = true
}

function handleDeletedMultiple() {
  selectedIds.value = selectedIds.value.filter(id => !selectedProductIds.value.includes(id))
  selectedProductIds.value = []
  showDeleteMultipleModal.value = false
  fetchProducts()
}

function closeDeleteMultipleModal() {
  showDeleteMultipleModal.value = false
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await api.get(`/admin/products/list?status=ativo`)
    // const res = await api.get(`/admin/products/list?status=${statusFilter.value}`) pro filtro comentado lá em cima
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


function openDuplicateModal(product) {
  // Remove o id e variantes id para evitar colisão
  const duplicated = JSON.parse(JSON.stringify(product))
  delete duplicated.id
  if (duplicated.variants) {
    duplicated.variants = duplicated.variants.map(v => {
      const { size, stock } = v
      return { size, stock }
    })
  }
  // Garante que o peso e dimensões venham preenchidos
  duplicated.weight = product.weight || 0
  duplicated.dimensionC = product.dimensionC || 0
  duplicated.dimensionL = product.dimensionL || 0
  duplicated.dimensionA = product.dimensionA || 0
  
  duplicateProduct.value = duplicated
  showCreateModal.value = true
}



function openEditModal(product) {
  selectedProductId.value = product
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  selectedProductId.value = null
}

function handleProductUpdated() {
  fetchProducts()
  closeEditModal()
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

function getToken() {
  return localStorage.getItem('token')
}


function openCreateModal() {
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
  duplicateProduct.value = null
}

function handleProductCreated() {
  fetchProducts()
  closeCreateModal()
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-row {
  background-color: #ffffff;
  transition: background-color 0.15s ease;
}

.product-row:hover {
  background-color: #f0efe9;
}

/* Customização das checkboxes */
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
  background-color: #0f2301/10;
}

.custom-checkbox:checked {
  background-color: #fffdf2;
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
