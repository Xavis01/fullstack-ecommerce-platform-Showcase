<script setup>
import { ref } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import { LoaderCircle, Eye, EyeOff } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    product: Object,
    newStatus: Boolean // true = público, false = privado
})

const emit = defineEmits(['close', 'confirmed'])
const toast = useToast()
const loading = ref(false)

const toggleVisibility = async () => {
    if (!props.product?.id) return

    loading.value = true
    try {
        const res = await api.put(`/admin/products/toggle-public/${props.product.id}`)

        const statusText = res.data.is_public ? 'público' : 'privado'
        toast.success(`Produto agora está ${statusText}!`)
        emit('confirmed')
        emit('close')
    } catch (error) {
        console.error('Erro ao alterar visibilidade:', error)
        toast.error('Erro ao alterar visibilidade do produto')
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
                <div class="flex flex-col items-center gap-4">
                    <div :class="[
                        'p-4 rounded-full',
                        newStatus ? 'bg-[#0f2301]/10' : 'bg-[#9a382d]/10'
                    ]">
                        <Eye v-if="newStatus" class="w-8 h-8 text-[#0f2301]" />
                        <EyeOff v-else class="w-8 h-8 text-[#9a382d]" />
                    </div>

                    <h2 class="text-xl font-light italic text-[#3a5528] text-center tracking-wide">
                        Alterar visibilidade?
                    </h2>

                    <p class="text-sm italic text-[#3a5528]/70 text-center tracking-wide">
                        <template v-if="newStatus">
                            O produto <strong>{{ product?.name }}</strong> ficará <strong
                                class="text-[#0f2301]">visível</strong> para os clientes
                        </template>
                        <template v-else>
                            O produto <strong>{{ product?.name }}</strong> ficará <strong
                                class="text-[#9a382d]">oculto</strong> dos clientes
                        </template>
                    </p>
                </div>

                <div class="flex justify-center gap-4">
                    <button @click="$emit('close')"
                        class="px-6 py-2.5 bg-[#0f2301] text-[#fffdf2] border border-[#0f2301]/20 rounded-lg hover:bg-[#0f2301]/80 transition-all italic tracking-wide">
                        Cancelar
                    </button>
                    <button @click="toggleVisibility" :disabled="loading" :class="[
                        'px-6 py-2.5 rounded-lg hover:opacity-90 transition-all disabled:opacity-50 italic tracking-wide flex items-center gap-2',
                        newStatus
                            ? 'bg-[#0f2301] text-[#fffdf2]'
                            : 'bg-[#9a382d] text-[#fffdf2]'
                    ]">
                        <span>{{ loading ? 'Alterando...' : 'Confirmar' }}</span>
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
