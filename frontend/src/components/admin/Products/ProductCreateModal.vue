<!-- frontend\src\components\admin\Products\ProductCreateModal.vue -->
<template>
  <transition name="modal-fade">
    <div v-if="isOpen" @click="closeModal"
      class="fixed inset-0 z-[110] flex items-center justify-center px-4 pt-10 sm:pt-0 backdrop-blur-sm bg-black/60 font-montserrat">
      <div @click.stop
        class="bg-white w-full max-w-7xl rounded-2xl shadow-2xl p-8 relative space-y-6 border border-[#0f2301]/10">
        <!-- Título do Modal -->
        <h2 class="text-2xl font-light italic text-[#3a5528] tracking-wide pr-8">Criar Novo Produto</h2>

        <!-- Botão fechar -->
        <button @click="closeModal"
          class="absolute top-6 right-6 text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
          <X />
        </button>

        <!-- Grid principal - Agora com 4 colunas -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Coluna esquerda (imagem + infos + descrição) - Span 2 -->
          <div class="md:col-span-2 space-y-6">
            <!-- Imagem + Infos -->
            <div class="flex flex-col sm:flex-row gap-6">
              <!-- Área de Imagens (aumentada) -->
              <div class="w-full sm:w-48 space-y-3">
                <!-- Imagem Principal (Quadrado Grande) -->
                <div
                  class="relative w-full h-44 bg-gray-100 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-50 transition-all group overflow-hidden"
                  :class="displayedCover ? 'border border-gray-300' : 'border-2 border-dashed border-gray-300'"
                  @click="selectAllImages" @dragover.prevent @drop="onDropOnCover">
                  <!-- Preview da imagem principal -->
                  <img v-if="displayedCover" :src="displayedCover.preview" class="w-full h-full object-cover"
                    alt="Imagem principal (Capa)" draggable="true" @dragstart="onDragStartImage(0)" />
                  <!-- Placeholder quando vazio -->
                  <div v-else class="text-center p-4">
                    <div class="text-gray-400 text-sm">Imagem Principal</div>
                    <div class="text-gray-300 text-xs mt-1">Clique para adicionar</div>
                  </div>

                  <!-- Botão remover (aparece no hover) -->
                  <span v-if="displayedCover"
                    class="absolute bottom-2 left-2 bg-black text-white text-xs px-2 py-0.5 rounded pointer-events-none">Capa</span>
                  <button v-if="displayedCover" @click.stop="removeCoverImage"
                    class="absolute top-2 right-2 w-6 h-6 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <X class="w-4 h-4 z-10" />
                  </button>
                </div>

              </div>

              <!-- Inputs principais -->
              <div class="flex-1 space-y-4">
                <div>
                  <label class="label">Nome</label>
                  <input v-model="form.name" class="input" placeholder="Nome do produto" />
                </div>
                <div>
                  <label class="label">Preço (R$)</label>
                  <input v-model.number="form.price" type="number" class="input" placeholder="Preço" step="0.01" />
                </div>
              </div>
            </div>

            <!-- Imagens Adicionais (Ocupando largura total do container) -->
            <div class="space-y-3">
              <div class="flex flex-wrap gap-2">
                <!-- Imagens existentes a partir da segunda -->
                <div v-for="(image, index) in displayedAdditional" :key="'img-' + index"
                  class="relative w-16 h-16 bg-gray-100 border border-gray-300 rounded-lg overflow-hidden cursor-pointer group flex-shrink-0"
                  draggable="true" @dragstart="onDragStartImage(getActualIdx(index))" @dragover.prevent
                  @drop="onDropImage(getActualIdx(index))">
                  <img :src="image.preview" class="w-full h-full object-cover"
                    :alt="'Imagem adicional ' + (index + 1)" />
                  <!-- Botão remover -->
                  <button @click.stop="removeAdditionalImage(index)"
                    class="absolute top-1 right-1 w-5 h-5 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <X class="w-3 h-3 z-10" />
                  </button>
                </div>

                <!-- Botão adicionar mais imagens (sempre visível) -->
                <div
                  class="w-16 h-16 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center cursor-pointer hover:border-gray-400 hover:bg-gray-100 transition-all flex-shrink-0"
                  @click="selectAllImages">
                  <span class="text-gray-400 text-lg">+</span>
                </div>
              </div>
            </div>

            <!-- Descrição -->
            <div>
              <label class="label">Descrição</label>
              <textarea v-model="form.description" rows="4" class="input resize-none"
                placeholder="Descrição do produto"></textarea>
            </div>
          </div>

          <!-- Coluna Tamanhos (meio) - Span 1 -->
          <div class="md:col-span-1 flex flex-col justify-start space-y-4 pt-[3px]">
            <div>
              <div class="flex items-center gap-2 mb-3">
                <h3 class="text-lg font-light italic text-[#3a5528] tracking-wide">Tamanhos</h3>
                <div class="relative group">
                  <CircleAlert class="h-4 w-4 text-[#3a5528]/60 hover:text-[#3a5528] cursor-pointer transition-colors"
                    stroke="currentColor" />
                  <div
                    class="absolute top-6 left-1/2 -translate-x-1/2 w-64 text-xs bg-[#0f2301] text-[#3a5528] border border-[#0f2301]/20 px-3 py-2 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-300 z-50">
                    Deixe o campo de tamanho vazio se o produto for tamanho único. Ele será salvo como
                    <strong>"Único"</strong>.
                  </div>
                </div>
                <div class="relative group">
                  <button type="button" @click="applyDefaultSizes"
                    class="flex items-center justify-center w-6 h-6 rounded-md text-[#3a5528]/50 hover:text-amber-500 hover:bg-amber-50 transition-all"
                    title="Aplicar tamanhos padrão">
                    <Star class="h-4 w-4" />
                  </button>
                  <div
                    class="absolute top-7 left-1/2 -translate-x-1/2 w-44 text-xs bg-[#0f2301] text-[#fffdf2] px-3 py-2 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-300 z-50 text-center">
                    Preencher com P, M, G, GG, XGG
                  </div>
                </div>
              </div>

              <div v-for="(variant, index) in form.variants" :key="index" class="flex items-center gap-2 mb-2">
                <input v-model="variant.size" placeholder="Tamanho" class="input w-1/2" />
                <input v-model.number="variant.stock" type="number" placeholder="Estoque" class="input w-1/2" />
                <button @click="removeVariant(index)"
                  class="text-[#9a382d] text-xl hover:text-[#9a382d]/80 transition-colors">×</button>
              </div>

              <button @click="addVariant"
                class="flex items-center justify-center gap-2 w-full px-4 py-2 border border-[#0f2301]/30 text-[#3a5528] rounded-lg hover:bg-[#0f2301]/30 transition-all italic text-sm tracking-wide">
                <span class="text-xl leading-none">+</span>
                <span>Adicionar tamanho</span>
              </button>
            </div>
          </div>

          <!-- NOVA COLUNA DIREITA (Categoria e Envio) - Span 1 -->
          <div class="md:col-span-1 flex flex-col justify-between space-y-4 pt-[3px]">
            <div class="space-y-4">
              <div>
                <h3 class="text-lg font-light italic text-[#3a5528] tracking-wide mb-3">Detalhes</h3>

                <div class="mb-4">
                  <label class="label">Categorias</label>
                  <MultiSelect v-model="form.category_ids" :items="categories" :loading="loadingCategories"
                    placeholder="Selecione as categorias" />
                </div>

                <div class="mb-4">
                  <label class="label">Coleção (Opcional)</label>
                  <RoccaSelect v-model="form.collection_id" :options="collectionOptions"
                    placeholder="Nenhuma coleção" />
                </div>

                <div class="mb-4">
                  <label class="label">Peso (kg)</label>
                  <input v-model.number="form.weight" type="number" step="0.01" class="input" placeholder="0.00" />
                </div>

                <div>
                  <label class="label mb-2 block">Dimensões (cm)</label>
                  <div class="grid grid-cols-3 gap-2">
                    <div>
                      <input v-model.number="form.dimensionC" type="number" class="input text-center px-1"
                        placeholder="C" title="Comprimento" />
                      <span class="text-[10px] text-[#3a5528]/70 text-center block mt-1">Comp.</span>
                    </div>
                    <div>
                      <input v-model.number="form.dimensionL" type="number" class="input text-center px-1"
                        placeholder="L" title="Largura" />
                      <span class="text-[10px] text-[#3a5528]/70 text-center block mt-1">Larg.</span>
                    </div>
                    <div>
                      <input v-model.number="form.dimensionA" type="number" class="input text-center px-1"
                        placeholder="A" title="Altura" />
                      <span class="text-[10px] text-[#3a5528]/70 text-center block mt-1">Alt.</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Botão Criar (movido para o final desta coluna) -->
            <button @click="createProduct" :disabled="loading"
              class="w-full py-3 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#0f2301]/90 transition-all disabled:opacity-50 italic tracking-wide font-light">
              <span class="flex items-center justify-center gap-2">
                {{ loading ? 'Criando...' : 'Criar Produto' }}
                <LoaderCircle v-if="loading" class="animate-spin w-4 h-4" />
              </span>
            </button>
          </div>
        </div>

        <!-- Inputs file invisíveis -->
        <input ref="allImagesInput" type="file" accept="image/*" multiple class="hidden" @change="handleImagesSelect" />
      </div>
    </div>
  </transition>
</template>

<script setup>
import { CircleAlert, LoaderCircle, X, Star } from 'lucide-vue-next'
import { ref, watch, computed } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import MultiSelect from '@/components/admin/Products/MultiSelect.vue'
import RoccaSelect from '@/components/common/RoccaSelect.vue'

const props = defineProps({ isOpen: Boolean, initialProduct: Object })
const emit = defineEmits(['close', 'productCreated'])

const toast = useToast()
const loading = ref(false)

// Referências aos inputs file
const allImagesInput = ref(null)

// Estado das imagens
const allImages = ref([])
const noCover = ref(false)
const draggedItemIndex = ref(null)

// Computed: imagem de capa
const displayedCover = computed(() => {
  if (noCover.value || allImages.value.length === 0) return null
  return allImages.value[0]
})

// Computed: imagens adicionais
const displayedAdditional = computed(() => {
  if (noCover.value) return allImages.value
  return allImages.value.slice(1)
})

// Converte display index para index real no allImages
const getActualIdx = (displayIdx) => {
  return noCover.value ? displayIdx : displayIdx + 1
}

// Estado do formulário
const form = ref({
  name: '',
  description: '',
  category_ids: [],
  collection_id: null,
  price: 0,
  weight: 0,
  dimensionC: 0,
  dimensionL: 0,
  dimensionA: 0,
  variants: [{ size: '', stock: 0 }]
})

const categories = ref([])

const loadingCategories = ref(false)

const fetchCategories = async () => {
  loadingCategories.value = true
  try {
    const { data } = await api.get('/admin/categories/list')
    categories.value = data
  } catch (error) {
    console.error('Erro ao buscar categorias:', error)
  } finally {
    loadingCategories.value = false
  }
}

const collections = ref([])
const loadingCollections = ref(false)

const fetchCollections = async () => {
  loadingCollections.value = true
  try {
    const { data } = await api.get('/admin/collections/list')
    collections.value = data
  } catch (error) {
    console.error('Erro ao buscar coleções:', error)
  } finally {
    loadingCollections.value = false
  }
}

// Computed mappings for RoccaSelect
const collectionOptions = computed(() => [
  { value: null, label: 'Nenhuma' },
  ...collections.value.map(c => ({ value: c.id, label: c.name }))
])

// Função para limpar o formulário e imagens
const resetForm = () => {
  form.value = {
    name: '',
    description: '',
    category_ids: [],
    collection_id: null,
    price: 0,
    weight: 0,
    dimensionC: 0,
    dimensionL: 0,
    dimensionA: 0,
    variants: [{ size: '', stock: 0 }]
  }
  allImages.value = []
  noCover.value = false
}

// Funções para seleção de imagens
const selectAllImages = () => {
  allImagesInput.value?.click()
}

// Handlers para upload de imagens
const handleImagesSelect = (event) => {
  const files = Array.from(event.target.files)

  if (noCover.value && files.length > 0) {
    // Se não tem capa, primeira imagem selecionada vira capa
    const coverFile = files.shift()
    allImages.value.unshift({ file: coverFile, preview: URL.createObjectURL(coverFile) })
    noCover.value = false
  }

  files.forEach(file => {
    allImages.value.push({
      file: file,
      preview: URL.createObjectURL(file)
    })
  })
  event.target.value = ''
}

// Remove imagem de capa (NÃO auto-promove)
const removeCoverImage = () => {
  if (allImages.value.length === 0) return
  const image = allImages.value[0]
  if (image?.preview) URL.revokeObjectURL(image.preview)
  allImages.value.splice(0, 1)
  noCover.value = true
}

// Remove imagem adicional (por display index)
const removeAdditionalImage = (displayIdx) => {
  const actualIdx = getActualIdx(displayIdx)
  const image = allImages.value[actualIdx]
  if (image?.preview) URL.revokeObjectURL(image.preview)
  allImages.value.splice(actualIdx, 1)
}

// HTML5 Drag and Drop handlers
const onDragStartImage = (index) => {
  draggedItemIndex.value = index
}

const onDropImage = (targetIndex) => {
  const draggedIndex = draggedItemIndex.value
  if (draggedIndex === null || draggedIndex === targetIndex) return

  const item = allImages.value.splice(draggedIndex, 1)[0]
  allImages.value.splice(targetIndex, 0, item)

  draggedItemIndex.value = null
}

// Drop na área de capa
const onDropOnCover = () => {
  const draggedIndex = draggedItemIndex.value
  if (draggedIndex === null) return

  if (noCover.value) {
    if (draggedIndex !== 0) {
      const item = allImages.value.splice(draggedIndex, 1)[0]
      allImages.value.splice(0, 0, item)
    }
    noCover.value = false
  } else {
    if (draggedIndex !== 0) {
      const item = allImages.value.splice(draggedIndex, 1)[0]
      allImages.value.splice(0, 0, item)
    }
  }

  draggedItemIndex.value = null
}

// Adicionar e remover variantes
const addVariant = () => {
  form.value.variants.push({ size: '', stock: 0 })
}

const removeVariant = (index) => {
  form.value.variants.splice(index, 1)
}

// Preencher tamanhos padrão
const applyDefaultSizes = () => {
  form.value.variants = [
    { size: 'P', stock: 0 },
    { size: 'M', stock: 0 },
    { size: 'G', stock: 0 },
    { size: 'GG', stock: 0 },
    { size: 'XGG', stock: 0 },
  ]
}

// Fechar modal e limpar
const closeModal = () => {
  // Limpar URLs de preview para evitar vazamentos de memória
  allImages.value.forEach(img => {
    if (img?.preview) {
      URL.revokeObjectURL(img.preview)
    }
  })

  emit('close')
  resetForm()
}

// Função para upload das imagens após criar o produto
const uploadProductImages = async (productId) => {
  if (allImages.value.length === 0) return

  const formData = new FormData()
  allImages.value.forEach(img => {
    formData.append('images', img.file)
  })

  try {
    await api.post(`/admin/products/${productId}/upload-images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  } catch (error) {
    toast.error('Erro ao enviar imagens: ' + (error.response?.data?.error || error.message))
    throw error
  }
}

// Criação do produto com validações
const createProduct = async () => {
  // Validações básicas
  if (!form.value.name.trim()) {
    toast.error('O nome do produto é obrigatório.')
    return
  }

  if (!form.value.description.trim()) {
    toast.error('A descrição é obrigatória.')
    return
  }

  if (!form.value.price || isNaN(form.value.price) || form.value.price <= 0) {
    toast.error('Informe um preço válido.')
    return
  }

  const variantsComEstoque = form.value.variants.filter(v => parseInt(v.stock) >= 0)

  if (variantsComEstoque.length === 0) {
    toast.error('Adicione pelo menos um tamanho.')
    return
  }

  // Substitui tamanhos vazios por "Único"
  const variantsCorrigidas = variantsComEstoque.map(v => ({
    ...v,
    size: v.size.trim() || 'Único'
  }))

  const payload = {
    ...form.value,
    collection_ids: form.value.collection_id ? [form.value.collection_id] : [],
    variants: variantsCorrigidas
  }

  loading.value = true
  try {
    // 1. Criar o produto
    const response = await api.post('/admin/products/create', payload)
    const productId = response.data.product_id

    // 2. Upload das imagens (se houver)
    if (allImages.value.length > 0) {
      await uploadProductImages(productId)
    }

    toast.success('Produto criado com sucesso!')
    emit('productCreated')
    closeModal()

  } catch (err) {
    toast.error('Erro ao criar produto: ' + (err.response?.data?.error || err.message))
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Quando o modal abrir
watch(() => props.isOpen, (isNowOpen) => {
  if (isNowOpen) {
    fetchCategories()
    fetchCollections()
    if (props.initialProduct) {
      // Preenche os dados com o produto a ser duplicado
      form.value = {
        name: props.initialProduct.name + ' (Cópia)',
        description: props.initialProduct.description,
        collection_id: props.initialProduct.collection_ids && props.initialProduct.collection_ids.length > 0 ? props.initialProduct.collection_ids[0] : null,
        category_ids: props.initialProduct.category_ids || [],
        price: props.initialProduct.price,
        weight: props.initialProduct.weight || 0,
        dimensionC: props.initialProduct.dimensionC || 0,
        dimensionL: props.initialProduct.dimensionL || 0,
        dimensionA: props.initialProduct.dimensionA || 0,
        variants: props.initialProduct.variants.map(v => ({
          size: v.size,
          stock: v.stock
        }))
      }
    } else {
      resetForm()
    }
  }
})
</script>

<style scoped>
.input {
  @apply w-full px-3 py-2.5 border border-[#0f2301]/30 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#0f2301] focus:border-[#0f2301] transition-all bg-white;
  font-family: 'Montserrat', sans-serif;
  font-style: italic;
  letter-spacing: 0.025em;
  color: #3a5528;
}

.input::placeholder {
  color: rgba(83, 113, 61, 0.4);
  font-style: italic;
}

.label {
  @apply block text-sm font-light text-[#3a5528] mb-2;
  font-family: 'Montserrat', sans-serif;
  font-style: italic;
  letter-spacing: 0.025em;
}

/* Transição suave e profissional para modal */
.modal-fade-enter-active {
  transition: opacity 0.3s ease, backdrop-filter 0.3s ease;
}

.modal-fade-leave-active {
  transition: opacity 0.25s ease, backdrop-filter 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active>div {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}

.modal-fade-leave-active>div {
  transition: transform 0.25s cubic-bezier(0.7, 0, 0.84, 0), opacity 0.25s ease;
}

.modal-fade-enter-from>div {
  transform: translateY(-20px);
  opacity: 0;
}

.modal-fade-leave-to>div {
  transform: translateY(-10px);
  opacity: 0;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 8px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: #0f2301;
  border-radius: 4px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #0f2301;
  border-radius: 4px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #3a5528;
}

/* Melhorias para os botões de remover */
.absolute button {
  transition: background-color 0.2s;
}

.absolute button:hover {
  background-color: rgba(0, 0, 0, 0.85);
}
</style>
```
