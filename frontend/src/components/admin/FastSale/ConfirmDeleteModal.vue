<template>
    <transition name="modal-fade">
        <div v-if="isOpen"
            class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm font-montserrat"
            @click="close">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 relative" @click.stop>

                <div class="text-center">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-[#9a382d]/10 mb-4">
                        <Trash2 class="h-6 w-6 text-[#9a382d]" />
                    </div>

                    <h3 class="text-lg font-medium text-[#3a5528] mb-2">Excluir Venda</h3>
                    <p class="text-sm text-gray-500 mb-6">
                        Tem certeza que deseja excluir esta venda? <br>
                        <span class="font-bold text-[#3a5528]">O estoque dos itens será restaurado.</span>
                    </p>

                    <div class="flex gap-3 justify-center">
                        <button @click="close"
                            class="px-4 py-2 border border-[#0f2301]/30 rounded-lg text-[#3a5528] hover:bg-[#0f2301]/50 transition-colors w-full">
                            Cancelar
                        </button>
                        <button @click="confirm" :disabled="loading"
                            class="px-4 py-2 bg-[#9a382d] text-white rounded-lg hover:bg-[#9a382d]/90 transition-colors w-full flex items-center justify-center gap-2">
                            <LoaderCircle v-if="loading" class="w-4 h-4 animate-spin" />
                            Excluir
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref } from 'vue'
import { Trash2, LoaderCircle } from 'lucide-vue-next'
import api from '@/api'
import { useToast } from 'vue-toastification'

const props = defineProps({
    isOpen: Boolean,
    saleId: Number
})

const emit = defineEmits(['close', 'deleted'])
const toast = useToast()
const loading = ref(false)

const close = () => {
    emit('close')
}

const confirm = async () => {
    loading.value = true
    try {
        await api.delete(`/fast-sales/${props.saleId}`)
        toast.success("Venda excluída e estoque restaurado!")
        emit('deleted')
    } catch (error) {
        console.error(error)
        toast.error("Erro ao excluir venda")
    } finally {
        loading.value = false
    }
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
