<script setup>
import { ref, computed, watch } from 'vue'
import { Loader2, Package, Tags, Layers } from 'lucide-vue-next'
import SelectProductsModal from './SelectProductsModal.vue'
import SelectCategoriesModal from './SelectCategoriesModal.vue'
import SelectCollectionsModal from './SelectCollectionsModal.vue'

const props = defineProps({
    isOpen: { type: Boolean, required: true },
    editData: { type: Object, default: null },
    saving: { type: Boolean, default: false },
    loadingDetails: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'save'])

const defaultForm = () => ({
    nome: '',
    descricao: '',
    porcentagem: true,
    valor: null,
    frete_gratis: false,
    is_active: true,
    data_inicio: '',
    data_fim: '',
    gasto_minimo: null,
    gasto_maximo: null,
    uso_individual: true,
    excluir_item_com_desconto: true,
    limite_uso: null,
    limite_por_conta: null,

    produtos: false,
    excluir_produtos: false,
    categorias: false,
    excluir_categorias: false,
    colecoes: false,
    excluir_colecoes: false,

    product_coupons: [],
    category_coupons: [],
    collection_coupons: []
})

const formData = ref(defaultForm())

const showProdModal = ref(false)
const showCatModal = ref(false)
const showColModal = ref(false)

const isEditing = computed(() => !!props.editData)

const syncData = () => {
    if (props.editData) {
        formData.value = { ...defaultForm(), ...props.editData }
        if (formData.value.data_inicio && formData.value.data_inicio.includes('T')) formData.value.data_inicio = formData.value.data_inicio.split('T')[0]
        if (formData.value.data_fim && formData.value.data_fim.includes('T')) formData.value.data_fim = formData.value.data_fim.split('T')[0]
    } else {
        formData.value = defaultForm()
    }
}

watch(() => props.isOpen, (newVal) => {
    if (newVal) syncData()
})

watch(() => props.editData, () => {
    if (props.isOpen) syncData()
}, { deep: true })

const handleProdSave = (result) => {
    formData.value.product_coupons = result.selected
    formData.value.excluir_produtos = result.excluir
    formData.value.produtos = result.hasSelection
    showProdModal.value = false
}

const handleCatSave = (result) => {
    formData.value.category_coupons = result.selected
    formData.value.excluir_categorias = result.excluir
    formData.value.categorias = result.hasSelection
    showCatModal.value = false
}

const handleColSave = (result) => {
    formData.value.collection_coupons = result.selected
    formData.value.excluir_colecoes = result.excluir
    formData.value.colecoes = result.hasSelection
    showColModal.value = false
}

const closeModal = () => {
    emit('close')
}

const handleSubmit = () => {
    const payload = { ...formData.value }

    // Converter datas para ISO com timezone garantindo formato válido
    if (payload.data_inicio) payload.data_inicio = new Date(payload.data_inicio + 'T00:00:00Z').toISOString()
    else payload.data_inicio = null

    if (payload.data_fim) payload.data_fim = new Date(payload.data_fim + 'T23:59:59Z').toISOString()
    else payload.data_fim = null

    emit('save', payload)
}
</script>

<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click.self="closeModal"
            class="fixed inset-0 z-[110] flex items-center justify-center pt-20 sm:pt-8 px-4 pb-8 backdrop-blur-sm bg-black/60 font-montserrat">

            <div
                class="bg-white w-full max-w-4xl rounded-2xl shadow-2xl relative flex flex-col max-h-[75vh] border border-[#0f2301]/10 overflow-hidden">
                <!-- Loading Overlay -->
                <div v-if="loadingDetails"
                    class="absolute inset-0 bg-white/50 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center">
                    <Loader2 class="animate-spin text-[#0f2301] mb-2" :size="32" />
                    <span class="text-[#0f2301] text-sm font-light italic">Carregando dados do cupom...</span>
                </div>

                <!-- Header -->
                <div
                    class="px-8 py-6 border-b border-[#eaddcf] flex justify-between items-center bg-[#fffdf2] shrink-0">
                    <h3 class="text-2xl font-light italic text-[#3a5528] tracking-wide">
                        {{ isEditing ? 'Editar Cupom' : 'Novo Cupom' }}
                    </h3>
                    <button @click="closeModal"
                        class="text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <form id="couponForm" @submit.prevent="handleSubmit" class="flex flex-col flex-1 overflow-hidden">
                    <!-- Form Body -->
                    <div class="flex-1 overflow-y-auto p-6 bg-[#fffdf2]/40">
                        <div class="space-y-6">

                            <!-- Seção 1: Infos Básicas -->
                            <div class="bg-white p-5 rounded-xl border border-[#eaddcf] shadow-sm space-y-4">
                                <h4 class="text-lg font-medium italic text-[#3a5528] border-b border-[#eaddcf] pb-2">
                                    Informações Básicas</h4>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                                    <div class="space-y-1.5">
                                        <label class="block text-sm font-light text-[#3a5528] italic tracking-wide">Nome
                                            do
                                            Cupom *</label>
                                        <input type="text" v-model="formData.nome" class="input w-full py-2"
                                            placeholder="Ex: VERAO2026" required />
                                    </div>

                                    <div class="space-y-1.5">
                                        <label
                                            class="block text-sm font-light text-[#3a5528] italic tracking-wide">Descrição
                                            (Interna)</label>
                                        <input type="text" v-model="formData.descricao" class="input w-full py-2"
                                            placeholder="Ex: Promoção de fim de ano" />
                                    </div>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
                                    <!-- Tipo de Desconto -->
                                    <div class="space-y-2">
                                        <label class="block text-sm font-light text-[#3a5528] italic tracking-wide">Tipo
                                            do
                                            Desconto *</label>
                                        <div class="flex gap-4">
                                            <label
                                                class="flex items-center gap-2 cursor-pointer group select-none relative">
                                                <input type="radio" :value="true" v-model="formData.porcentagem"
                                                    class="peer hidden" />
                                                <div
                                                    class="w-5 h-5 rounded-full border border-[#0f2301] flex items-center justify-center transition-colors peer-checked:bg-[#0f2301] bg-transparent group-hover:bg-[#0f2301]/20">
                                                    <div
                                                        class="w-2 h-2 bg-white rounded-full opacity-0 peer-checked:opacity-100 transition-opacity">
                                                    </div>
                                                </div>
                                                <span class="text-[#3a5528] text-sm relative z-10">Porcentagem
                                                    (%)</span>
                                            </label>
                                            <label
                                                class="flex items-center gap-2 cursor-pointer group select-none relative">
                                                <input type="radio" :value="false" v-model="formData.porcentagem"
                                                    class="peer hidden" />
                                                <div
                                                    class="w-5 h-5 rounded-full border border-[#0f2301] flex items-center justify-center transition-colors peer-checked:bg-[#0f2301] bg-transparent group-hover:bg-[#0f2301]/20">
                                                    <div
                                                        class="w-2 h-2 bg-white rounded-full opacity-0 peer-checked:opacity-100 transition-opacity">
                                                    </div>
                                                </div>
                                                <span class="text-[#3a5528] text-sm relative z-10">Valor Fixo
                                                    (R$)</span>
                                            </label>
                                        </div>
                                    </div>

                                    <div class="space-y-1.5">
                                        <label class="block text-sm font-light text-[#3a5528] italic tracking-wide">
                                            Valor do Desconto *
                                        </label>
                                        <div class="relative">
                                            <span v-if="!formData.porcentagem"
                                                class="absolute left-3 top-1/2 -translate-y-1/2 text-[#3a5528]/60 font-light text-sm pt-[1px]">R$</span>
                                            <input type="number" step="0.01" min="0" v-model="formData.valor"
                                                class="input w-full py-2 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                                :style="{ paddingLeft: !formData.porcentagem ? '2.25rem' : '1rem', paddingRight: formData.porcentagem ? '2.25rem' : '1rem' }"
                                                placeholder="0.00" required />
                                            <span v-if="formData.porcentagem"
                                                class="absolute right-3 top-1/2 -translate-y-1/2 text-[#3a5528]/60 font-light text-sm pt-[1px]">%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Seção 2: Regras e Validade -->
                            <div class="bg-white p-5 rounded-xl border border-[#eaddcf] shadow-sm space-y-4">
                                <h4 class="text-lg font-medium italic text-[#3a5528] border-b border-[#eaddcf] pb-2">
                                    Regras
                                    de Validade</h4>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div class="space-y-1.5">
                                        <label class="block text-sm font-light text-[#3a5528] italic tracking-wide">Data
                                            Início</label>
                                        <input type="date" v-model="formData.data_inicio" class="input w-full py-2" />
                                    </div>
                                    <div class="space-y-1.5">
                                        <label class="block text-sm font-light text-[#3a5528] italic tracking-wide">Data
                                            Fim</label>
                                        <input type="date" v-model="formData.data_fim" class="input w-full py-2" />
                                    </div>

                                    <div class="space-y-1.5">
                                        <label
                                            class="block text-sm font-light text-[#3a5528] italic tracking-wide">Gasto
                                            Mínimo (R$)</label>
                                        <input type="number" step="0.01" min="0" v-model="formData.gasto_minimo"
                                            class="input w-full py-2" placeholder="Sem mínimo" />
                                    </div>
                                    <div class="space-y-1.5">
                                        <label
                                            class="block text-sm font-light text-[#3a5528] italic tracking-wide">Gasto
                                            Máximo (R$)</label>
                                        <input type="number" step="0.01" min="0" v-model="formData.gasto_maximo"
                                            class="input w-full py-2" placeholder="Sem máximo" />
                                    </div>

                                    <div class="space-y-1.5">
                                        <label
                                            class="block text-sm font-light text-[#3a5528] italic tracking-wide">Limite
                                            de Usos Totais</label>
                                        <input type="number" min="1" step="1" v-model="formData.limite_uso"
                                            class="input w-full py-2" placeholder="Usos ilimitados totais" />
                                    </div>
                                    <div class="space-y-1.5">
                                        <label
                                            class="block text-sm font-light text-[#3a5528] italic tracking-wide">Limite
                                            por Conta (Cliente)</label>
                                        <input type="number" min="1" step="1" v-model="formData.limite_por_conta"
                                            class="input w-full py-2" placeholder="Usos ilimitados por cliente" />
                                    </div>
                                </div>
                            </div>

                            <!-- Seção 3: Restrições / Produtos Associados -->
                            <div class="bg-white p-5 rounded-xl border border-[#eaddcf] shadow-sm space-y-4">
                                <h4 class="text-lg font-medium italic text-[#3a5528] border-b border-[#eaddcf] pb-2">
                                    Vínculos & Restrições</h4>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3">
                                    <label
                                        class="flex items-center gap-3 cursor-pointer group p-2 hover:bg-[#0f2301]/30 rounded-lg transition-colors text-left w-full select-none relative">
                                        <input type="checkbox" v-model="formData.frete_gratis" class="peer hidden" />
                                        <div
                                            class="w-5 h-5 rounded bg-white border border-[#0f2301] flex items-center justify-center transition-colors shrink-0 peer-checked:bg-[#0f2301] peer-checked:border-[#0f2301]">
                                            <i
                                                class="fas fa-check text-white text-xs opacity-0 peer-checked:opacity-100 transition-opacity"></i>
                                        </div>
                                        <span class="text-[#3a5528] text-sm relative z-10">Oferece Frete Grátis?</span>
                                    </label>

                                    <label
                                        class="flex items-center gap-3 cursor-pointer group p-2 hover:bg-[#0f2301]/30 rounded-lg transition-colors text-left w-full select-none relative">
                                        <input type="checkbox" v-model="formData.uso_individual" class="peer hidden" />
                                        <div
                                            class="w-5 h-5 rounded bg-white border border-[#0f2301] flex items-center justify-center transition-colors shrink-0 peer-checked:bg-[#0f2301] peer-checked:border-[#0f2301]">
                                            <i
                                                class="fas fa-check text-white text-xs opacity-0 peer-checked:opacity-100 transition-opacity"></i>
                                        </div>
                                        <span class="text-[#3a5528] text-sm relative z-10">Apenas Uso Individual (Não
                                            comba com
                                            outros)</span>
                                    </label>

                                    <label
                                        class="flex items-center gap-3 cursor-pointer group p-2 hover:bg-[#0f2301]/30 rounded-lg transition-colors text-left w-full select-none relative">
                                        <input type="checkbox" v-model="formData.excluir_item_com_desconto"
                                            class="peer hidden" />
                                        <div
                                            class="w-5 h-5 rounded bg-white border border-[#0f2301] flex items-center justify-center transition-colors shrink-0 peer-checked:bg-[#0f2301] peer-checked:border-[#0f2301]">
                                            <i
                                                class="fas fa-check text-white text-xs opacity-0 peer-checked:opacity-100 transition-opacity"></i>
                                        </div>
                                        <span class="text-[#3a5528] text-sm relative z-10">Excluir produtos que já
                                            possuem
                                            desconto</span>
                                    </label>

                                    <label
                                        class="flex items-center gap-3 cursor-pointer group p-2 hover:bg-[#0f2301]/30 rounded-lg transition-colors text-left w-full select-none relative">
                                        <input type="checkbox" v-model="formData.is_active" class="peer hidden" />
                                        <div
                                            class="w-5 h-5 rounded bg-white border border-[#0f2301] flex items-center justify-center transition-colors shrink-0 peer-checked:bg-[#0f2301] peer-checked:border-[#0f2301]">
                                            <i
                                                class="fas fa-check text-white text-xs opacity-0 peer-checked:opacity-100 transition-opacity"></i>
                                        </div>
                                        <span class="text-[#3a5528] text-sm font-semibold relative z-10">Cupom Ativo
                                            Imediatamente?</span>
                                    </label>
                                </div>

                                <div class="mt-6 pt-6 border-t border-[#eaddcf] grid grid-cols-1 sm:grid-cols-3 gap-4">
                                    <!-- Box Produtos -->
                                    <button type="button" @click="showProdModal = true"
                                        class="flex flex-col items-center justify-center p-4 border border-[#0f2301]/30 rounded-xl hover:bg-[#0f2301]/40 transition-all gap-2"
                                        :class="formData.product_coupons.length ? 'bg-[#0f2301]/20 border-[#0f2301]' : ''">
                                        <Package class="w-6 h-6 text-[#0f2301]" />
                                        <span class="text-sm text-[#3a5528] font-medium">Produtos Específicos</span>
                                        <span class="text-xs text-[#8c9e78]">{{ formData.product_coupons.length }}
                                            selecionados</span>
                                    </button>

                                    <!-- Box Categorias -->
                                    <button type="button" @click="showCatModal = true"
                                        class="flex flex-col items-center justify-center p-4 border border-[#0f2301]/30 rounded-xl hover:bg-[#0f2301]/40 transition-all gap-2"
                                        :class="formData.category_coupons.length ? 'bg-[#0f2301]/20 border-[#0f2301]' : ''">
                                        <Tags class="w-6 h-6 text-[#0f2301]" />
                                        <span class="text-sm text-[#3a5528] font-medium">Categorias Específicas</span>
                                        <span class="text-xs text-[#8c9e78]">{{ formData.category_coupons.length }}
                                            selecionadas</span>
                                    </button>

                                    <!-- Box Coleções -->
                                    <button type="button" @click="showColModal = true"
                                        class="flex flex-col items-center justify-center p-4 border border-[#0f2301]/30 rounded-xl hover:bg-[#0f2301]/40 transition-all gap-2"
                                        :class="formData.collection_coupons.length ? 'bg-[#0f2301]/20 border-[#0f2301]' : ''">
                                        <Layers class="w-6 h-6 text-[#0f2301]" />
                                        <span class="text-sm text-[#3a5528] font-medium">Coleções Específicas</span>
                                        <span class="text-xs text-[#8c9e78]">{{ formData.collection_coupons.length }}
                                            selecionadas</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div class="px-8 py-4 border-t border-[#eaddcf] flex justify-end gap-3 bg-[#fffdf2] shrink-0">
                        <button type="button" @click="closeModal"
                            class="px-6 py-2.5 text-[#3a5528] border border-[#3a5528]/20 hover:bg-[#e4e3db] rounded-lg transition-colors font-light italic tracking-wide">
                            Cancelar
                        </button>
                        <button type="submit" :disabled="saving"
                            class="px-8 py-2.5 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#3a5528] transition-all shadow-md font-light italic tracking-wide disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
                            <Loader2 v-if="saving" class="animate-spin" :size="15" />
                            <span>{{ isEditing ? 'Salvar Alterações' : 'Criar Cupom' }}</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </transition>

    <!-- Sub-modals -->
    <SelectProductsModal :is-open="showProdModal" @close="showProdModal = false" @save="handleProdSave"
        :initial-selected="formData.product_coupons" :initial-excluir="formData.excluir_produtos" />

    <SelectCategoriesModal :is-open="showCatModal" @close="showCatModal = false" @save="handleCatSave"
        :initial-selected="formData.category_coupons" :initial-excluir="formData.excluir_categorias" />

    <SelectCollectionsModal :is-open="showColModal" @close="showColModal = false" @save="handleColSave"
        :initial-selected="formData.collection_coupons" :initial-excluir="formData.excluir_colecoes" />
</template>

<style scoped>
.input {
    @apply px-4 py-2.5 border border-[#0f2301]/30 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#0f2301]/50 focus:border-[#0f2301] transition-all bg-white;
    font-family: 'Montserrat', sans-serif;
    color: #3a5528;
}

.input::placeholder {
    color: rgba(83, 113, 61, 0.4);
    font-style: italic;
    font-weight: 300;
}

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
    transform: translateY(-20px) scale(0.98);
    opacity: 0;
}

.modal-fade-leave-to>div {
    transform: translateY(-10px) scale(0.98);
    opacity: 0;
}
</style>
