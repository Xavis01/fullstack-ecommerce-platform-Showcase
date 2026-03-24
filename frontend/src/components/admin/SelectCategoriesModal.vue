<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Loader2 } from 'lucide-vue-next'
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
        selectedIds.value = new Set(props.initialSelected.map(p => p.category_id))
        isExcluir.value = props.initialExcluir
        searchTerm.value = ''
        if (items.value.length === 0) fetchItems()
    }
})

const fetchItems = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/categories/list')
        items.value = response.data.map(p => ({
            id: p.id,
            name: p.name
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
        .map(i => ({ category_id: i.id, category_name: i.name, excluir: isExcluir.value }))

    emit('save', {
        selected: selectedData,
        excluir: isExcluir.value,
        hasSelection: selectedData.length > 0
    })
}
</script>

<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click.self="emit('close')"
            class="fixed inset-0 z-[60] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat p-4">

            <div
                class="bg-white w-full max-w-2xl max-h-[85vh] flex flex-col rounded-2xl shadow-2xl relative border border-[#0f2301]/10 overflow-hidden">
                <div class="px-8 py-6 border-b border-[#eaddcf] flex justify-between items-center bg-[#0f2301]/30">
                    <h3 class="text-2xl font-light italic text-[#3a5528] tracking-wide">
                        Selecionar Categorias
                    </h3>
                    <button @click="emit('close')"
                        class="text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="px-8 py-4 border-b border-[#eaddcf] flex flex-col gap-4 bg-white">
                    <div
                        class="flex items-center gap-3 bg-[#0f2301]/50 px-4 py-2 rounded-lg border border-[#eaddcf] w-fit">
                        <span class="text-sm text-[#3a5528] font-light italic">Essas categorias:</span>
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

                    <div class="relative w-full group">
                        <input v-model="searchTerm" type="text" placeholder="Buscar categoria..."
                            class="w-full bg-[#0f2301]/20 border border-[#3a5528]/20 rounded-lg py-2 pl-10 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors font-light" />
                        <Search :size="18"
                            class="absolute left-3 top-1/2 -translate-y-1/2 text-[#3a5528]/60 group-focus-within:text-[#3a5528]" />
                    </div>
                </div>

                <div class="flex-1 overflow-y-auto p-4 bg-[#fffdf2]/30">
                    <div v-if="loading" class="flex justify-center py-12">
                        <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
                    </div>

                    <div v-else-if="filteredItems.length === 0"
                        class="text-center py-12 text-[#8c9e78] italic font-light">
                        Nenhuma categoria encontrada.
                    </div>

                    <div v-else class="flex flex-col gap-2">
                        <div v-for="item in filteredItems" :key="item.id" @click="toggleSelect(item.id)"
                            class="px-4 py-3 border rounded-xl flex justify-between items-center transition-all bg-white hover:shadow-sm cursor-pointer"
                            :class="selectedIds.has(item.id) ? 'border-[#0f2301] bg-[#0f2301]/20' : 'border-[#eaddcf] hover:border-[#3a5528]/40'">

                            <span class="text-[#3a5528] font-medium">{{ item.name }}</span>

                            <div class="w-6 h-6 rounded-md border flex items-center justify-center transition-colors"
                                :class="selectedIds.has(item.id) ? 'bg-[#0f2301] border-[#0f2301] text-white' : 'border-[#8c9e78]/50'">
                                <i v-if="selectedIds.has(item.id)" class="fas fa-check text-xs"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="px-8 py-4 border-t border-[#eaddcf] flex justify-between items-center bg-white">
                    <span class="text-sm text-[#8c9e78] italic">
                        {{ selectedIds.size }} selecionadas
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
