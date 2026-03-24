<template>
  <transition name="modal-fade">
    <div v-if="isOpen" @click="closeModal"
      class="fixed inset-0 z-[110] flex items-center justify-center px-4 pt-10 sm:pt-0 backdrop-blur-sm bg-black/60 font-montserrat">
      <div @click.stop
        class="bg-white w-full max-w-7xl rounded-2xl shadow-2xl p-8 relative space-y-6 border border-[#0f2301]/10">
        <!-- Título do Modal -->
        <h2 class="text-2xl font-light italic text-[#3a5528] tracking-wide pr-8">Editar Produto</h2>

        <!-- Botão Fechar -->
        <button @click="closeModal"
          class="absolute top-6 right-6 text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
          <X />
        </button>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Coluna Esquerda — Imagens + Infos - Span 2 -->
          <div class="md:col-span-2 space-y-6">
            <div class="flex flex-col sm:flex-row gap-6">
              <!-- Área de Imagens -->
              <div class="w-full sm:w-48 space-y-3">
                <!-- Imagem principal (Capa) -->
                <div
                  class="relative w-full h-44 bg-gray-100 rounded-xl flex items-center justify-center cursor-pointer group overflow-hidden"
                  :class="displayedCover ? 'border border-gray-300' : 'border-2 border-dashed border-gray-300'"
                  @click="selectAllImages" @dragover.prevent @drop="onDropOnCover">
                  <!-- Mostra spinner até saber se tem imagem -->
                  <div v-if="loadingMainImage"
                    class="absolute inset-0 flex items-center justify-center bg-gray-200 animate-pulse z-10">
                    <LoaderCircle class="w-6 h-6 text-gray-500 animate-spin" />
                  </div>

                  <!-- Só mostra imagem OU placeholder se não está mais carregando -->
                  <template v-if="!loadingMainImage">
                    <img v-if="displayedCover" :src="displayedCover.preview || displayedCover.image_public_url"
                      :style="{ display: mainImageLoaded ? '' : 'none' }" @load="mainImageLoaded = true"
                      class="w-full h-full object-cover rounded-xl transition-opacity duration-500"
                      alt="Imagem principal (Capa)" draggable="true" @dragstart="onDragStartImage(0)" />
                    <div v-else class="text-center p-4">
                      <div class="text-gray-400 text-sm">Imagem Principal</div>
                      <div class="text-gray-300 text-xs mt-1">Clique para adicionar</div>
                    </div>
                    <span v-if="displayedCover"
                      class="absolute bottom-2 left-2 bg-black text-white text-xs px-2 py-0.5 rounded pointer-events-none">Capa</span>
                    <button v-if="displayedCover" @click.stop="removeCoverImage"
                      class="absolute top-2 right-2 w-6 h-6 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <X class="w-4 h-4 z-10" />
                    </button>
                  </template>
                </div>

              </div>

              <!-- Dados principais -->
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
                <div v-for="(image, idx) in displayedAdditional" :key="image.id || image.preview"
                  class="relative w-16 h-16 bg-gray-100 border border-gray-300 rounded-lg overflow-hidden cursor-pointer group flex-shrink-0"
                  draggable="true" @dragstart="onDragStartImage(getActualIdx(idx))" @dragover.prevent
                  @drop="onDropImage(getActualIdx(idx))">
                  <!-- Spinner loader aparece enquanto a imagem não é carregada -->
                  <div v-if="!loadedAdditionalKeys.has(image.id || image.preview)"
                    class="absolute inset-0 flex items-center justify-center bg-gray-200 animate-pulse z-0">
                    <LoaderCircle class="w-4 h-4 text-gray-500 animate-spin" />
                  </div>

                  <!-- A imagem só aparece quando já terminou de baixar -->
                  <img v-if="image.preview || image.image_public_url" :src="image.preview || image.image_public_url"
                    :style="{ display: loadedAdditionalKeys.has(image.id || image.preview) ? '' : 'none' }"
                    @load="() => loadedAdditionalKeys.add(image.id || image.preview)"
                    class="w-full h-full object-cover transition-opacity duration-300" alt="Imagem adicional" />

                  <button @click.stop="removeAdditionalImage(idx)"
                    class="absolute top-1 right-1 w-5 h-5 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <X class="w-3 h-3 z-10" />
                  </button>
                </div>
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
                  <CircleAlert
                    class="h-4 w-4 text-[#3a5528]/60 hover:text-[#3a5528] cursor-pointer transition-colors" />
                  <div
                    class="absolute top-6 left-1/2 -translate-x-1/2 w-64 text-xs bg-[#0f2301] text-[#3a5528] border border-[#0f2301]/20 px-3 py-2 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-300 z-50">
                    Deixe o campo de tamanho vazio se o produto for tamanho único: será salvo como
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

            <!-- Botão Salvar (movido para o final desta coluna) -->
            <button :disabled="loading" @click="saveAll"
              class="w-full py-3 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#0f2301]/90 transition-all disabled:opacity-50 italic tracking-wide font-light">
              <span class="flex items-center justify-center gap-2">
                {{ loading ? 'Salvando...' : 'Salvar Alterações' }}
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
import { LoaderCircle, X, CircleAlert, Star } from 'lucide-vue-next'
import { ref, reactive, watch, computed } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import MultiSelect from '@/components/admin/Products/MultiSelect.vue'
import RoccaSelect from '@/components/common/RoccaSelect.vue'

const props = defineProps({ isOpen: Boolean, product: Object })
const emit = defineEmits(['close', 'productUpdated'])
const toast = useToast()
const loading = ref(false)
const mainImageLoaded = ref(false)


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
  variants: []
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

// ============================= IMAGENS =============================
const allImages = ref([]) // Array flat de todas as imagens
const noCover = ref(false) // true = capa foi removida explicitamente
const draggedItemIndex = ref(null)

const allImagesInput = ref(null)
const loadedAdditionalKeys = reactive(new Set()) // Tracking por ID/preview ao invés de index
const loadingMainImage = ref(true)

// Computed: imagem de capa (primeira do array, se noCover = false)
const displayedCover = computed(() => {
  if (noCover.value || allImages.value.length === 0) return null
  return allImages.value[0]
})

// Computed: imagens adicionais (todas se noCover, senão slice(1))
const displayedAdditional = computed(() => {
  if (noCover.value) return allImages.value
  return allImages.value.slice(1)
})

// Converte display index (das adicionais) para index real no allImages
const getActualIdx = (displayIdx) => {
  return noCover.value ? displayIdx : displayIdx + 1
}

// Busque imagens atuais sempre que abrir modal
const fetchProductImages = async () => {
  loadingMainImage.value = true
  if (!props.product?.id) {
    allImages.value = []
    loadingMainImage.value = false
    return
  }

  const { data } = await api.get(`/admin/products/${props.product.id}/images`)
  allImages.value = data.map(img => ({ ...img }))
  noCover.value = false
  loadingMainImage.value = false
}

const selectAllImages = () => allImagesInput.value?.click()

// Adiciona imagens
const handleImagesSelect = (event) => {
  const files = Array.from(event.target.files)

  if (noCover.value && files.length > 0) {
    // Se não tem capa, a primeira imagem selecionada vira capa
    const coverFile = files.shift()
    allImages.value.unshift({ file: coverFile, preview: URL.createObjectURL(coverFile), is_new: true })
    noCover.value = false
  }

  // Restante vai pra lista de adicionais
  files.forEach(file => {
    allImages.value.push({ file, preview: URL.createObjectURL(file), is_new: true })
  })
  event.target.value = ''
}

// Remove imagem de capa (NÃO auto-promove)
const removeCoverImage = () => {
  if (allImages.value.length === 0) return
  const img = allImages.value[0]
  if (img?.preview) URL.revokeObjectURL(img.preview)
  allImages.value.splice(0, 1)
  noCover.value = true // Capa fica vazia, NÃO promove a segunda imagem
}

// Remove imagem adicional (por display index)
const removeAdditionalImage = (displayIdx) => {
  const actualIdx = getActualIdx(displayIdx)
  const img = allImages.value[actualIdx]
  if (img?.preview) URL.revokeObjectURL(img.preview)
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
    // Sem capa: mover o item arrastado para posição 0 e restaurar capa
    if (draggedIndex !== 0) {
      const item = allImages.value.splice(draggedIndex, 1)[0]
      allImages.value.splice(0, 0, item)
    }
    noCover.value = false
  } else {
    // Com capa: comportamento normal de reorder
    if (draggedIndex !== 0) {
      const item = allImages.value.splice(draggedIndex, 1)[0]
      allImages.value.splice(0, 0, item)
    }
  }

  draggedItemIndex.value = null
}

// UX e validações variantes
const addVariant = () => form.value.variants.push({ size: '', stock: 0 })
const removeVariant = idx => form.value.variants.splice(idx, 1)

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

// Carregar dados produto ao abrir
watch(() => props.isOpen, (open) => {
  if (open && props.product) {
    // 1️⃣ Limpe o estado ANTES de buscar dados novos
    allImages.value = []
    noCover.value = false
    loadingMainImage.value = true
    mainImageLoaded.value = false
    loadedAdditionalKeys.clear()

    // 2️⃣ Limpe o estado do form
    form.value = {
      name: '',
      description: '',
      category_ids: [],
      collection_id: null,
      price: 0,
      variants: []
    }

    // Só depois popule os campos com os novos dados
    form.value = {
      name: props.product.name,
      description: props.product.description,
      category_ids: props.product.category_ids || [],
      collection_id: props.product.collection_ids && props.product.collection_ids.length > 0 ? props.product.collection_ids[0]
        : null,
      price: props.product.price,
      weight: props.product.weight || 0,
      dimensionC: props.product.dimensionC || 0,
      dimensionL: props.product.dimensionL || 0,
      dimensionA: props.product.dimensionA || 0,
      variants: props.product.variants.map(v => ({
        size: v.size === 'Único' ? '' : v.size,
        stock: v.stock
      }))
    }
    fetchProductImages()
    fetchCategories()
    fetchCollections()
  }
})


// Atualizar **imagens** do produto
const updateImages = async () => {
  const formData = new FormData()

  let fileIndex = 0;

  allImages.value.forEach((img) => {
    if (img.is_new) {
      formData.append('images_order[]', `file:${fileIndex}`);
      formData.append('images', img.file);
      fileIndex++;
    } else {
      formData.append('images_order[]', `id:${img.id}`);
    }
  });

  await api.post(`/admin/products/${props.product.id}/update-images`, formData)
}

// Atualizar **dados** e **imagens** do produto
const saveAll = async () => {
  // Validações UX
  if (!form.value.name.trim()) return toast.error('O nome é obrigatório.')
  if (!form.value.description.trim()) return toast.error('A descrição é obrigatória.')
  if (!form.value.price || isNaN(form.value.price) || form.value.price <= 0) return toast.error('Informe um preço válido.')
  const variantesValidas = form.value.variants.filter(v => parseInt(v.stock) >= 0)
  if (allImages.value.length === 0) return toast.error('Adicione ao menos uma imagem.')
  if (variantesValidas.length === 0) return toast.error('Adicione pelo menos um tamanho.')

  loading.value = true
  try {
    // Atualiza dados do produto
    await api.put(`/admin/products/update/${props.product.id}`, {
      ...form.value,
      collection_ids: form.value.collection_id ? [form.value.collection_id] : [],
      variants: variantesValidas.map(v => ({ ...v, size: v.size.trim() || 'Único' }))
    })
    // Atualiza imagens
    await updateImages()
    toast.success('Produto atualizado!')
    emit('productUpdated')
    closeModal()
  } catch (err) {
    toast.error('Erro ao salvar alterações.')
  } finally {
    loading.value = false
  }
}

// Fechar e limpar previews locais
const closeModal = () => {
  allImages.value.forEach(img => { if (img?.preview) URL.revokeObjectURL(img.preview) })
  emit('close')
}
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

.absolute button {
  transition: background-color 0.2s;
}

.absolute button:hover {
  background-color: rgba(0, 0, 0, 0.85);
}
</style>