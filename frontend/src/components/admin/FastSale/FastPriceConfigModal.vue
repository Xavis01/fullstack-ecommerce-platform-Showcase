<template>
    <transition name="modal-fade">
        <div v-if="isOpen"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 pt-16 font-montserrat"
            @click="close">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col" @click.stop>
                <!-- Header -->
                <div
                    class="p-6 border-b border-[#0f2301]/10 flex justify-between items-center bg-[#fcf9f0] rounded-t-xl">
                    <h2 class="text-2xl font-light italic text-[#3a5528] flex items-center gap-2">
                        Configurar Preços
                        <span class="text-sm bg-[#0f2301]/10 px-2 py-0.5 rounded-full not-italic font-normal">
                            Venda Rápida
                        </span>
                    </h2>
                    <button @click="close"
                        class="text-[#3a5528] hover:text-[#9a382d] transition-colors p-1 rounded-full hover:bg-black/5">
                        <X class="w-6 h-6" />
                    </button>
                </div>

                <!-- Controls -->
                <div class="p-6 border-b border-[#0f2301]/10 bg-white">
                    <div class="flex gap-4">
                        <div class="relative flex-1">
                            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#3a5528]/50" />
                            <input v-model="searchQuery" type="text" placeholder="Buscar produto..."
                                class="w-full pl-10 pr-4 py-2 border border-[#0f2301]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f2301] text-[#3a5528] placeholder-[#3a5528]/50 font-light" />
                        </div>
                    </div>
                </div>

                <!-- Product List -->
                <div class="max-h-[350px] overflow-y-auto p-0 bg-white">
                    <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-[#3a5528]/70">
                        <LoaderCircle class="w-10 h-10 animate-spin mb-4" />
                        <p class="animate-pulse">Carregando produtos...</p>
                    </div>

                    <table v-else class="w-full text-left border-collapse">
                        <thead class="sticky top-0 bg-[#e4e3db] shadow-sm z-10">
                            <tr>
                                <th class="p-4 font-medium text-[#3a5528] text-sm tracking-wide">Produto</th>
                                <th class="p-4 font-medium text-[#3a5528] text-sm tracking-wide w-40">Preço Padrão</th>
                                <th class="p-4 font-medium text-[#3a5528] text-sm tracking-wide w-48">Preço Evento</th>
                                <th class="p-4 font-medium text-[#3a5528] text-sm tracking-wide w-20 text-center">Reset
                                </th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-[#0f2301]/10">
                            <tr v-for="product in filteredProducts" :key="product.id"
                                class="hover:bg-[#f0efe9] transition-colors group">
                                <td class="p-4">
                                    <div class="font-medium text-[#3a5528]">{{ product.name }}</div>
                                    <div class="text-xs text-[#3a5528]/60 italic">{{ product.collection || 'Sem coleção'
                                        }}</div>
                                </td>
                                <td class="p-4 text-[#3a5528]/70">
                                    R$ {{ product.price.toFixed(2) }}
                                </td>
                                <td class="p-4">
                                    <div class="relative">
                                        <span
                                            class="absolute left-3 top-1/2 -translate-y-1/2 text-[#3a5528] text-sm">R$</span>
                                        <input type="number" v-model.number="product.temp_fast_price" step="0.01"
                                            class="w-full pl-9 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f2301] text-[#3a5528] font-medium transition-colors"
                                            :class="hasChanged(product) ? 'border-[#0f2301] bg-[#0f2301]/5' : 'border-[#0f2301]/30'" />
                                    </div>
                                </td>
                                <td class="p-4 text-center">
                                    <button @click="resetToDefault(product)" :disabled="isDefault(product)"
                                        title="Redefinir para preço padrão"
                                        class="p-2 rounded-lg text-[#3a5528] hover:bg-[#9a382d]/10 hover:text-[#9a382d] transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-[#3a5528]">
                                        <RotateCcw class="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="filteredProducts.length === 0">
                                <td colspan="4" class="p-8 text-center text-[#3a5528]/50 italic">
                                    Nenhum produto encontrado.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Footer -->
                <div
                    class="p-6 border-t border-[#0f2301]/10 bg-[#fcf9f0] rounded-b-xl flex justify-between items-center">
                    <div class="text-sm text-[#3a5528]/70 hidden sm:block">
                        <span v-if="changedCount > 0" class="font-bold text-[#0f2301]">
                            {{ changedCount }} alterações pendentes
                        </span>
                        <span v-else>Nenhuma alteração pendente</span>
                    </div>
                    <div class="flex gap-3 w-full sm:w-auto">
                        <button @click="close"
                            class="px-6 py-2 border border-[#0f2301] text-[#3a5528] rounded-lg hover:bg-[#0f2301]/10 transition-colors flex-1 sm:flex-none">
                            Cancelar
                        </button>
                        <button @click="saveChanges" :disabled="changedCount === 0 || saving"
                            class="px-6 py-2 bg-[#0f2301] text-white rounded-lg hover:bg-[#0f2301]/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed flex-1 sm:flex-none shadow-lg shadow-[#0f2301]/20">
                            <LoaderCircle v-if="saving" class="w-4 h-4 animate-spin" />
                            <span v-else>Salvar Alterações</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X, Search, RotateCcw, LoaderCircle } from 'lucide-vue-next'
import api from '@/api'
import { useToast } from 'vue-toastification'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close', 'refresh'])
const toast = useToast()

const products = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')

// Buscar produtos
const fetchProducts = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/products/list')
        // Mapear produtos e adicionar campo temporário para edição
        products.value = response.data.map(p => ({
            ...p,
            temp_fast_price: p.fast_price !== undefined ? p.fast_price : p.price
        }))
    } catch (error) {
        console.error('Erro ao buscar produtos:', error)
        toast.error('Erro ao carregar produtos')
    } finally {
        loading.value = false
    }
}

// Watch para carregar produtos ao abrir
watch(() => props.isOpen, (newVal) => {
    if (newVal) {
        fetchProducts()
        searchQuery.value = ''
    }
})

// Filtragem
const filteredProducts = computed(() => {
    if (!searchQuery.value) return products.value
    const query = searchQuery.value.toLowerCase()
    return products.value.filter(p =>
        p.name.toLowerCase().includes(query) ||
        (p.collection && p.collection.toLowerCase().includes(query))
    )
})

// Helpers de estado
const hasChanged = (product) => {
    return product.temp_fast_price !== product.fast_price
}

const isDefault = (product) => {
    return product.temp_fast_price === product.price
}

const changedCount = computed(() => {
    return products.value.filter(p => hasChanged(p)).length
})

// Ações
const resetToDefault = (product) => {
    product.temp_fast_price = product.price
}

const saveChanges = async () => {
    if (changedCount.value === 0) return

    saving.value = true
    try {
        // Filtrar apenas os modificados
        const updates = products.value
            .filter(p => hasChanged(p))
            .map(p => ({
                id: p.id,
                fast_price: p.temp_fast_price
            }))

        await api.put('/admin/products/fast-prices/bulk-update', { updates })

        toast.success(`${updates.length} preços atualizados!`)
        emit('refresh') // Opcional, para atualizar parent se necessário
        close()
    } catch (error) {
        console.error('Erro ao salvar:', error)
        toast.error('Erro ao salvar alterações')
    } finally {
        saving.value = false
    }
}

const close = () => {
    emit('close')
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}
</style>
