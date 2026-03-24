<template>
    <transition name="modal-fade">
        <div v-if="isOpen"
            class="fixed inset-0 z-[100] flex items-center justify-center mt-24 px-4 backdrop-blur-sm bg-black/60 font-montserrat"
            @click="$emit('close')">

            <!-- Modal Content -->
            <div @click.stop
                class="relative w-full max-w-sm bg-[#fffdf2] rounded-2xl shadow-2xl overflow-hidden border border-[#0f2301]/10 flex flex-col p-6 text-center">

                <h2 class="text-xl font-medium tracking-tight text-[#3a5528] mb-4">Cancelar Pedido</h2>

                <p class="text-[#8c9e78] font-light text-sm mb-8 leading-relaxed">
                    Tem certeza que deseja cancelar este pedido? Seus itens serão automaticamente retornados ao seu
                    carrinho de compras e esta ação não poderá ser desfeita.
                </p>

                <div class="flex gap-3 mt-auto">
                    <button @click="$emit('cancel', order.order_id)" :disabled="loading"
                        class="flex-1 py-2.5 rounded-xl border border-red-200 text-red-600 bg-transparent hover:bg-red-50 transition-colors font-light tracking-wide text-sm flex justify-center items-center disabled:opacity-50">
                        <Loader2 v-if="loading" class="w-4 h-4 mr-2 animate-spin" />
                        {{ loading ? 'Cancelando...' : 'Sim, cancelar' }}
                    </button>
                    <button @click="$emit('close')" :disabled="loading"
                        class="flex-1 py-2.5 rounded-xl bg-[#3a5528] text-[#fffdf2] hover:bg-[#0f2301] transition-colors font-light tracking-wide text-sm disabled:opacity-50">
                        Não
                    </button>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { Loader2 } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    order: Object,
    loading: Boolean
})

const emit = defineEmits(['close', 'cancel'])
</script>

<style scoped>
/* Transição suave e profissional para modal padrão Rocca */
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease;
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
