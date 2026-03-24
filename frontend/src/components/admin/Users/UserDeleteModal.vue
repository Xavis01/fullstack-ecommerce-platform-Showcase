<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="closeModal"
            class="fixed inset-0 z-50 flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-sm rounded-2xl shadow-2xl relative overflow-hidden border border-[#0f2301]/10">

                <!-- Header -->
                <div class="bg-red-700/80 px-8 py-5 flex items-center gap-3">
                    <Trash2 class="text-white" :size="20" />
                    <h2 class="text-lg font-['Montserrat'] font-light italic tracking-widest text-white uppercase">
                        Excluir Usuário
                    </h2>
                    <button @click="closeModal" class="ml-auto text-white/60 hover:text-white transition-colors">
                        <X :size="20" />
                    </button>
                </div>

                <!-- Body -->
                <div class="px-8 py-7 text-center space-y-3">
                    <p class="text-[#3a5528] font-light">Tem certeza que deseja excluir o usuário</p>
                    <p class="text-[#3a5528] font-semibold italic text-lg">{{ user?.name }}</p>
                    <p class="text-[#8c9e78] text-sm">Esta ação não pode ser desfeita.</p>
                </div>

                <!-- Footer -->
                <div class="px-8 pb-7 flex gap-3">
                    <button @click="closeModal"
                        class="flex-1 py-2.5 rounded-lg border border-[#0f2301]/30 text-[#3a5528] text-sm font-light italic tracking-wide hover:bg-[#0f2301]/40 transition-all">
                        Cancelar
                    </button>
                    <button @click="confirm" :disabled="deleting"
                        class="flex-1 py-2.5 rounded-lg bg-red-600 text-white text-sm font-light italic tracking-wide hover:bg-red-700 transition-all disabled:opacity-60 flex items-center justify-center gap-2">
                        <Loader2 v-if="deleting" class="animate-spin" :size="16" />
                        <span>{{ deleting ? 'Excluindo...' : 'Excluir' }}</span>
                    </button>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api'
import { X, Trash2, Loader2 } from 'lucide-vue-next'

const props = defineProps({ isOpen: Boolean, user: Object })
const emit = defineEmits(['close', 'deleted'])
const toast = useToast()
const deleting = ref(false)

async function confirm() {
    deleting.value = true
    try {
        await api.delete(`/admin/users/delete/${props.user.id}`)
        toast.success('Usuário excluído com sucesso!')
        emit('deleted')
        closeModal()
    } catch (e) {
        toast.error(e.response?.data?.error || 'Erro ao excluir usuário.')
    } finally {
        deleting.value = false
    }
}

function closeModal() { emit('close') }
</script>

<style scoped>
.modal-fade-enter-active {
    transition: opacity 0.3s ease;
}

.modal-fade-leave-active {
    transition: opacity 0.25s ease;
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
