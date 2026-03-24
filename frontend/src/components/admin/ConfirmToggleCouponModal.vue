<script setup>
import { ref } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import { LoaderCircle, Info } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    coupon: Object,
})
const emit = defineEmits(['close', 'toggled'])

const loading = ref(false)
const toast = useToast()

async function toggleCoupon() {
    if (!props.coupon) return

    loading.value = true
    try {
        await api.patch(`/admin/coupons/toggle_active/${props.coupon.id}`, {
            is_active: !props.coupon.is_active
        })
        toast.success(`Cupom ${!props.coupon.is_active ? 'ativado' : 'desativado'} com sucesso!`)
        emit('toggled')
    } catch (err) {
        toast.error(err.response?.data?.error || 'Erro ao alterar status do cupom')
        console.error(err)
    } finally {
        loading.value = false
        emit('close')
    }
}
</script>

<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="emit('close')"
            class="fixed inset-0 z-[110] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-md p-8 rounded-2xl shadow-2xl space-y-6 border border-[#0f2301]/10">
                <h2 class="text-xl font-light italic text-[#3a5528] mb-2 text-center tracking-wide">
                    Certeza que deseja <span class="font-semibold">{{ coupon?.is_active ? 'desativar' : 'ativar'
                    }}</span> o cupom "{{ coupon?.nome }}"?
                </h2>
                <p
                    class="text-sm italic text-[#0f2301]/90 mb-6 text-center font-medium tracking-wide flex items-center justify-center gap-2">
                    <Info class="w-4 h-4" />
                    {{ coupon?.is_active ? 'Clientes não poderão mais utilizar este cupom.' : 'Este cupom passará a funcionar imediatamente(se estiver dentro da validade e regras).' }}
                </p>
                <div class="flex justify-center gap-4">
                    <button @click="emit('close')"
                        class="px-6 py-2.5 bg-[#9a382d] text-[#fffdf2] border border-[#0f2301]/20 rounded-lg hover:bg-[#9a382d]/80 transition-all italic tracking-wide">
                        Cancelar
                    </button>
                    <button @click="toggleCoupon" :disabled="loading"
                        class="px-6 py-2.5 text-[#fffdf2] rounded-lg transition-all disabled:opacity-50 italic tracking-wide flex items-center gap-2"
                        :class="coupon?.is_active ? 'bg-[#0f2301] hover:bg-[#0f2301]/90' : 'bg-[#0f2301] hover:bg-[#0f2301]/90'">
                        <span>{{ loading ? 'Processando...' : 'Confirmar' }}</span>
                        <LoaderCircle v-if="loading" class="animate-spin w-4 h-4" />
                    </button>
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
    transform: translateY(-20px);
    opacity: 0;
}

.modal-fade-leave-to>div {
    transform: translateY(-10px);
    opacity: 0;
}
</style>
