<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Loader2, Check } from 'lucide-vue-next'
import api from '@/api'

const props = defineProps({
    isOpen: Boolean,
    initialSelected: { type: Array, default: () => [] },
    initialExcluir: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'save'])

const items = ref([])
const loading = ref(false)
const searchTerm = ref('')

const selectedIds = ref(new Set())
const isExcluir = ref(false)

watch(() => props.isOpen, (val) => {
    if (val) {
        selectedIds.value = new Set(props.initialSelected.map(p => p.product_id))
        isExcluir.value = props.initialExcluir
        searchTerm.value = ''
        if (items.value.length === 0) fetchItems()
    }
})

const fetchItems = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/products/list')
        items.value = response.data.map(p => ({
            id: p.id,
            name: p.name,
            image: p.image_url || null
        }))
    } catch (err) {
        console.error(err)
    } finally {
        loading.value = false
    }
}

const filteredItems = computed(() => {
    if (!searchTerm.value) return items.value
    const term = searchTerm.value.toLowerCase()
    return items.value.filter(i => i.name.toLowerCase().includes(term))
})

const toggleSelect = (id) => {
    if (selectedIds.value.has(id)) {
        selectedIds.value.delete(id)
    } else {
        selectedIds.value.add(id)
    }
}

const handleSave = () => {
    const selectedData = items.value
        .filter(i => selectedIds.value.has(i.id))
        .map(i => ({ product_id: i.id, product_name: i.name, excluir: isExcluir.value }))

    emit('save', {
        selected: selectedData,
        excluir: isExcluir.value,
        hasSelection: selectedData.length > 0
    })
}
</script>

<template>
    <Teleport to="body">
        <transition name="modal-fade">
        <div v-if="isOpen" @click.self="emit('close')"
            class="fixed inset-0 z-[110] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat p-4">

            <div
                class="bg-white w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl shadow-2xl relative border border-[#0f2301]/10 overflow-hidden">
                <!-- Header -->
                <div class="px-8 py-5 border-b border-[#eaddcf] flex justify-between items-center bg-white relative">
                    <h3 class="text-2xl font-light italic text-[#3a5528] tracking-wide relative z-10 w-1/3">
                        Selecionar Produtos
                    </h3>
                    <div class="w-1/3 flex justify-center h-8">
                        <img src="/rocca_logo.png" alt="ROCCA" class="h-full opacity-90 object-contain" />
                    </div>
                    <div class="w-1/3 flex justify-end">
                        <button @click="emit('close')"
                            class="text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>

                <!-- Toolbar (Search & Toggle) -->
                <div
                    class="px-8 py-4 border-b border-[#eaddcf] flex flex-col sm:flex-row gap-4 justify-between items-center bg-white">
                    <!-- Search -->
                    <div class="relative w-full sm:w-96 group">
                        <input v-model="searchTerm" type="text" placeholder="Buscar produto..."
                            class="w-full bg-transparent border border-[#3a5528]/20 rounded-lg py-2 pl-10 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors font-light" />
                        <Search :size="18"
                            class="absolute left-3 top-1/2 -translate-y-1/2 text-[#3a5528]/60 group-focus-within:text-[#3a5528]" />
                    </div>

                    <!-- Excluir Toggle -->
                    <div class="flex items-center gap-3">
                        <span class="text-sm text-[#3a5528] font-light italic">Esses produtos:</span>
                        <div class="flex bg-white rounded-lg p-1 border border-[#eaddcf] shadow-sm">
                            <button @click="isExcluir = false"
                                :class="!isExcluir ? 'bg-[#0f2301] text-white shadow' : 'text-[#8c9e78] hover:bg-[#e4e3db]'"
                                class="px-3 py-1 text-sm rounded-md transition-all font-medium">
                                Podem usar
                            </button>
                            <button @click="isExcluir = true"
                                :class="isExcluir ? 'bg-[#9a382d] text-white shadow' : 'text-[#8c9e78] hover:bg-[#e4e3db]'"
                                class="px-3 py-1 text-sm rounded-md transition-all font-medium">
                                NÃO podem usar
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="flex-1 overflow-y-auto p-8 bg-[#fffdf2]/30">
                    <div v-if="loading" class="flex justify-center py-12">
                        <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
                    </div>

                    <div v-else-if="filteredItems.length === 0"
                        class="text-center py-12 text-[#8c9e78] italic font-light">
                        Nenhum produto encontrado.
                    </div>

                    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        <div v-for="item in filteredItems" :key="item.id" @click="toggleSelect(item.id)"
                            class="border rounded-xl cursor-default transition-all duration-200 overflow-hidden flex flex-col bg-white hover:shadow-md cursor-pointer"
                            :class="selectedIds.has(item.id) ? 'border-[#0f2301] ring-2 ring-[#0f2301]/30 shadow-sm' : 'border-[#eaddcf] hover:border-[#3a5528]/40'">

                            <div class="aspect-square bg-gray-100 relative">
                                <img v-if="item.image" :src="item.image" :alt="item.name"
                                    class="w-full h-full object-cover" />
                                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">Sem
                                    Foto</div>

                                <div v-if="selectedIds.has(item.id)"
                                    class="absolute top-2 right-2 w-6 h-6 bg-[#0f2301] rounded-full flex items-center justify-center shadow-sm">
                                    <Check :size="14" stroke-width="3" class="text-[#f8f6f0]" />
                                </div>
                            </div>

                            <div class="p-3 bg-white">
                                <p class="text-sm font-medium text-[#3a5528] line-clamp-2 leading-tight"
                                    :title="item.name">
                                    {{ item.name }}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="px-8 py-4 border-t border-[#eaddcf] flex justify-between items-center bg-white">
                    <span class="text-sm text-[#8c9e78] italic">
                        {{ selectedIds.size }} selecionados
                    </span>
                    <div class="flex gap-3">
                        <button @click="emit('close')"
                            class="px-5 py-2 text-[#0f2301] hover:bg-[#e4e3db] rounded-lg transition-colors italic tracking-wide">
                            Cancelar
                        </button>
                        <button @click="handleSave"
                            class="px-8 py-2 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#3a5528] transition-all shadow-md italic tracking-wide">
                            Salvar Seleção
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </transition>
    </Teleport>
</template>

<style scoped>
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
    transform: scale(0.95);
    opacity: 0;
}

.modal-fade-leave-to>div {
    transform: scale(0.95);
    opacity: 0;
}
</style>
