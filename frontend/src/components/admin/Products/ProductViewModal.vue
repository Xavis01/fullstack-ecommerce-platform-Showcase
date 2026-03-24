<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="closeModal"
            class="fixed inset-0 z-[110] flex items-center pt-10 sm:pt-0 justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-7xl rounded-2xl shadow-2xl p-8 relative space-y-6 border border-[#0f2301]/10">
                <!-- Título do Modal -->
                <h2 class="text-2xl font-light italic text-[#3a5528] tracking-wide pr-8">Visualizar Produto</h2>

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
                                <!-- Imagem principal -->
                                <div class="relative w-full h-44 bg-gray-100 rounded-xl flex items-center justify-center overflow-hidden"
                                    :class="mainImage ? 'border border-gray-300' : 'border-2 border-dashed border-gray-300'">
                                    <!-- Spinner até carregar -->
                                    <div v-if="loadingMainImage"
                                        class="absolute inset-0 flex items-center justify-center bg-gray-200 animate-pulse z-10">
                                        <LoaderCircle class="w-6 h-6 text-gray-500 animate-spin" />
                                    </div>

                                    <!-- Imagem ou placeholder -->
                                    <template v-if="!loadingMainImage">
                                        <img v-if="mainImage" :src="mainImage.preview || mainImage.image_public_url"
                                            :style="{ display: mainImageLoaded ? '' : 'none' }"
                                            @load="mainImageLoaded = true"
                                            class="w-full h-full object-cover rounded-xl transition-opacity duration-500"
                                            alt="Imagem principal" />
                                        <div v-else class="text-center p-4">
                                            <div class="text-gray-400 text-sm">Imagem Principal</div>
                                            <div class="text-gray-300 text-xs mt-1">Sem imagem</div>
                                        </div>
                                        <span v-if="mainImage"
                                            class="absolute bottom-2 left-2 bg-black text-white text-xs px-2 py-0.5 rounded">Capa</span>
                                    </template>
                                </div>

                            </div>

                            <!-- Dados principais -->
                            <div class="flex-1 space-y-4">
                                <div>
                                    <label class="label">Nome</label>
                                    <input v-model="form.name" class="input cursor-not-allowed bg-gray-100"
                                        placeholder="Nome do produto" readonly disabled />
                                </div>

                                <div>
                                    <label class="label">Preço (R$)</label>
                                    <input v-model.number="form.price" type="number"
                                        class="input cursor-not-allowed bg-gray-100" placeholder="Preço" readonly
                                        disabled />
                                </div>
                            </div>
                        </div>

                        <!-- Imagens Adicionais (Ocupando largura total do container) -->
                        <div v-if="additionalImages.length > 0" class="space-y-3">
                            <!-- <label class="label block mb-2 text-sm text-[#3a5528]/70">Imagens Adicionais</label> -->
                            <div class="flex flex-wrap gap-2">
                                <div v-for="(image, idx) in additionalImages" :key="image.id || image.preview"
                                    class="relative w-16 h-16 bg-gray-100 border border-gray-300 rounded-lg overflow-hidden flex-shrink-0">
                                    <div v-if="!loadedAdditionalIndexes.includes(idx)"
                                        class="absolute inset-0 flex items-center justify-center bg-gray-200 animate-pulse z-0">
                                        <LoaderCircle class="w-4 h-4 text-gray-500 animate-spin" />
                                    </div>

                                    <img v-if="image.preview || image.image_public_url"
                                        :src="image.preview || image.image_public_url"
                                        :style="{ display: loadedAdditionalIndexes.includes(idx) ? '' : 'none' }"
                                        @load="() => { if (!loadedAdditionalIndexes.includes(idx)) loadedAdditionalIndexes.push(idx) }"
                                        class="w-full h-full object-cover transition-opacity duration-300"
                                        alt="Imagem adicional" />
                                </div>
                            </div>
                        </div>

                        <!-- Descrição -->
                        <div>
                            <label class="label">Descrição</label>
                            <textarea v-model="form.description" rows="4"
                                class="input resize-none cursor-not-allowed bg-gray-100"
                                placeholder="Descrição do produto" readonly disabled></textarea>
                        </div>
                    </div>

                    <!-- Coluna Tamanhos (meio) - Span 1 -->
                    <div class="md:col-span-1 flex flex-col justify-start space-y-4 pt-[3px]">
                        <div>
                            <h3 class="text-lg font-light italic text-[#3a5528] tracking-wide mb-3">Tamanhos</h3>
                            <div v-for="(variant, index) in form.variants" :key="index"
                                class="flex items-center gap-2 mb-2">
                                <input v-model="variant.size" placeholder="Tamanho"
                                    class="input w-1/2 cursor-not-allowed bg-gray-100" readonly disabled />
                                <input v-model.number="variant.stock" type="number" placeholder="Estoque"
                                    class="input w-1/2 cursor-not-allowed bg-gray-100" readonly disabled />
                            </div>
                        </div>
                    </div>

                    <!-- NOVA COLUNA DIREITA (Categoria e Envio) - Span 1 -->
                    <div class="md:col-span-1 flex flex-col justify-start space-y-4 pt-[3px]">
                        <div class="space-y-4">
                            <div>
                                <h3 class="text-lg font-light italic text-[#3a5528] tracking-wide mb-3">Detalhes</h3>

                                <div class="mb-4">
                                    <label class="label">Categoria</label>
                                    <div
                                        class="w-full px-3 py-2.5 border border-[#0f2301]/20 rounded-lg shadow-sm bg-[#0f2301]/10 flex items-center gap-2 min-h-[42px]">
                                        <Loader2 v-if="loadingCategoryName"
                                            class="w-4 h-4 animate-spin text-[#3a5528]/50 shrink-0" />
                                        <span class="text-sm italic tracking-wide"
                                            style="font-family: 'Montserrat', sans-serif;"
                                            :class="loadingCategoryName ? 'text-[#3a5528]/40' : 'text-[#3a5528]/70'">
                                            {{ loadingCategoryName ? 'Carregando...' : form.category_name }}
                                        </span>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <label class="label">Coleção</label>
                                    <input :value="form.collection || 'Nenhuma coleção'"
                                        class="input cursor-not-allowed bg-gray-100 text-[#3a5528]/70 bg-[#0f2301]/30"
                                        readonly disabled />
                                </div>

                                <div class="mb-4">
                                    <label class="label">Peso (kg)</label>
                                    <input v-model.number="form.weight" type="number" step="0.01"
                                        class="input cursor-not-allowed bg-gray-100" placeholder="0.00" readonly
                                        disabled />
                                </div>

                                <div>
                                    <label class="label mb-2 block">Dimensões (cm)</label>
                                    <div class="grid grid-cols-3 gap-2">
                                        <div>
                                            <input v-model.number="form.dimensionC" type="number"
                                                class="input text-center px-1 cursor-not-allowed bg-gray-100"
                                                placeholder="C" title="Comprimento" readonly disabled />
                                            <span
                                                class="text-[10px] text-[#3a5528]/70 text-center block mt-1">Comp.</span>
                                        </div>
                                        <div>
                                            <input v-model.number="form.dimensionL" type="number"
                                                class="input text-center px-1 cursor-not-allowed bg-gray-100"
                                                placeholder="L" title="Largura" readonly disabled />
                                            <span
                                                class="text-[10px] text-[#3a5528]/70 text-center block mt-1">Larg.</span>
                                        </div>
                                        <div>
                                            <input v-model.number="form.dimensionA" type="number"
                                                class="input text-center px-1 cursor-not-allowed bg-gray-100"
                                                placeholder="A" title="Altura" readonly disabled />
                                            <span
                                                class="text-[10px] text-[#3a5528]/70 text-center block mt-1">Alt.</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/api'
import { LoaderCircle, X, CircleAlert, Loader2 } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    product: Object,
})

const emit = defineEmits(['close'])

const loadingMainImage = ref(true)
const mainImageLoaded = ref(false)
const loadingCategoryName = ref(false)

const form = ref({
    name: '',
    description: '',
    collection: '',
    price: 0,
    weight: 0,
    dimensionC: 0,
    dimensionL: 0,
    dimensionA: 0,
    category_name: '',
    variants: [],
})

const existingImages = ref([]) // [{id, image_url, is_cover}]
const mainImage = ref(null) // {id?, image_url?, preview?, file?, is_new?}
const additionalImages = ref([]) // [{id?, image_url?, preview?, file?, is_new?}]
const loadedAdditionalIndexes = ref([])

// Watch para carregar dados e imagens igual ao modal de edição
watch(
    () => props.isOpen,
    async (open) => {
        if (open && props.product) {
            mainImage.value = null
            additionalImages.value = []
            loadedAdditionalIndexes.value = []
            existingImages.value = []
            loadingMainImage.value = true
            mainImageLoaded.value = false

            // Reset form
            form.value = {
                name: '',
                description: '',
                collection: '',
                price: 0,
                variants: [],
            }

            // Popula form com dados do produto

            // Busca nome da categoria se houver ID
            let categoryName = 'Sem Categoria'
            if (props.product.category_ids && props.product.category_ids.length > 0) {
                // Idealmente, o backend retornaria o nome, ou buscaríamos na lista de categorias.
                // Como é view, vamos tentar buscar todas as categorias para pegar o nome
                // Ou, mais simples, o backend já retorna o nome da categoria no list_products? Não, só IDs.
                // Vamos implementar um fetchCategories rápido aqui também para garantir o nome.
            }
            // Update: Vou buscar a lista de categorias aqui para exibir o nome correto

            form.value = {
                name: props.product.name,
                description: props.product.description,
                collection: props.product.collection,
                price: props.product.price,
                weight: props.product.weight || 0,
                dimensionC: props.product.dimensionC || 0,
                dimensionL: props.product.dimensionL || 0,
                dimensionA: props.product.dimensionA || 0,
                category_name: '', // Será preenchido
                variants: props.product.variants.map((v) => ({
                    size: v.size === 'Único' ? '' : v.size,
                    stock: v.stock,
                })),
            }

            // Fetch categoria nome
            try {
                loadingCategoryName.value = true
                if (props.product.category_ids && props.product.category_ids.length > 0) {
                    const { data } = await api.get('/admin/categories/list')
                    const cat = data.find(c => c.id === props.product.category_ids[0])
                    form.value.category_name = cat ? cat.name : 'Sem Categoria'
                } else {
                    form.value.category_name = 'Sem Categoria'
                }
            } catch (e) {
                console.error("Erro ao buscar categorias para view", e)
                form.value.category_name = 'Erro ao carregar'
            } finally {
                loadingCategoryName.value = false
            }

            // Carrega imagens via API
            try {
                const { data } = await api.get(`/admin/products/${props.product.id}/images`)
                existingImages.value = data
                const cover = data.find((img) => img.is_cover)
                mainImage.value = cover ? { ...cover } : null
                additionalImages.value = data.filter((img) => !img.is_cover).map((img) => ({ ...img }))
            } catch (error) {
                // Opcional: lidar com erro
                mainImage.value = null
                additionalImages.value = []
            } finally {
                loadingMainImage.value = false
            }
        }
    }
)

function closeModal() {
    emit('close')
}
</script>

<style scoped>
.input {
    @apply w-full px-3 py-2.5 border border-[#0f2301]/20 rounded-lg shadow-sm bg-[#0f2301]/20 text-[#3a5528]/70 cursor-not-allowed;
    font-family: 'Montserrat', sans-serif;
    font-style: italic;
    letter-spacing: 0.025em;
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
</style>
```
