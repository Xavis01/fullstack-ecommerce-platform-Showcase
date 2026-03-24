<script setup>
import { ref } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import { LoaderCircle } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    product: Object
})

const emit = defineEmits(['close', 'confirmed'])
const toast = useToast()
const loading = ref(false)

const cancelSchedule = async () => {
    if (!props.product?.id) return

    loading.value = true
    try {
        await api.delete(`/admin/products/schedule/${props.product.id}`)
        toast.success('Agendamento cancelado com sucesso!')
        emit('confirmed')
        emit('close')
    } catch (error) {
        console.error('Erro ao cancelar agendamento:', error)
        toast.error('Erro ao cancelar agendamento')
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="$emit('close')"
            class="fixed inset-0 z-[110] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-md p-8 rounded-2xl shadow-2xl space-y-6 border border-[#0f2301]/10">
                <h2 class="text-xl font-light italic text-[#3a5528] mb-2 text-center tracking-wide">
                    Cancelar agendamento?
                </h2>
                <p class="text-sm italic text-[#3a5528]/70 text-center tracking-wide">
                    O produto <strong>{{ product?.name }}</strong> voltará a ficar privado
                </p>
                <div class="flex justify-center gap-4">
                    <button @click="$emit('close')"
                        class="px-6 py-2.5 bg-[#0f2301] text-[#3a5528] border border-[#0f2301]/20 rounded-lg hover:bg-[#0f2301]/80 transition-all italic tracking-wide">
                        Voltar
                    </button>
                    <button @click="cancelSchedule" :disabled="loading"
                        class="px-6 py-2.5 bg-[#9a382d] text-[#0f2301] rounded-lg hover:bg-[#9a382d]/90 transition-all disabled:opacity-50 italic tracking-wide flex items-center gap-2">
                        <span>{{ loading ? 'Cancelando...' : 'Confirmar' }}</span>
                        <LoaderCircle v-if="loading" class="animate-spin w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    </transition>
</template>

<style scoped>
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
