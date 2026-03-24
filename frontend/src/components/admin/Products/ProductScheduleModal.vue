<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="closeModal"
            class="fixed inset-0 z-[110] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-lg rounded-2xl shadow-2xl p-8 relative space-y-6 border border-[#0f2301]/10">
                <!-- Botão fechar -->
                <button @click="closeModal"
                    class="absolute top-6 right-6 text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
                    <X />
                </button>

                <h2 class="text-2xl font-light italic text-[#3a5528] tracking-wide text-center">
                    {{ isScheduled ? 'Agendamento Atual' : 'Agendar Publicação' }}
                </h2>

                <div v-if="loading" class="flex flex-col items-center justify-center p-8">
                    <LoaderCircle class="animate-spin w-8 h-8 text-[#0f2301] mb-2" />
                    <p class="text-[#3a5528]/70 italic text-sm">Processando...</p>
                </div>

                <div v-else class="space-y-6">

                    <!-- MODO VISUALIZAÇÃO (Se já agendado e não editando) -->
                    <div v-if="isScheduled && !isEditing" class="text-center space-y-6">
                        <div class="bg-[#0f2301]/50 p-6 rounded-xl border border-[#0f2301]/20">
                            <p class="text-[#3a5528]/70 text-sm mb-1 italic">Este produto será publicado em:</p>
                            <p class="text-xl font-light italic text-[#3a5528] tracking-wide">{{ formattedDate }}</p>
                            <div
                                class="mt-4 flex items-center justify-center gap-2 text-[#3a5528] text-sm bg-[#0f2301] p-2 rounded-lg inline-block border border-[#0f2301]/20">
                                <Clock class="w-4 h-4" />
                                <span class="italic">Aguardando publicação</span>
                            </div>
                        </div>

                        <div class="flex gap-3">
                            <button @click="showCancelModal = true"
                                class="flex-1 py-3 px-4 bg-[#9a382d]/10 text-[#9a382d] rounded-lg hover:bg-[#9a382d]/20 transition-all italic tracking-wide flex items-center justify-center gap-2">
                                <Trash2 class="w-4 h-4" />
                                Cancelar Agendamento
                            </button>
                            <button @click="isEditing = true"
                                class="flex-1 py-3 px-4 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#0f2301]/90 transition-all italic tracking-wide flex items-center justify-center gap-2">
                                <CalendarDays class="w-4 h-4" />
                                Alterar Data
                            </button>
                        </div>
                    </div>

                    <!-- MODO EDIÇÃO/CRIAÇÃO -->
                    <div v-else class="space-y-4">
                        <div
                            class="bg-[#0f2301] text-[#fffdf2] p-4 rounded-xl text-sm mb-4 border border-[#0f2301]/20">
                            <p class="italic">Escolha a data e hora para publicar o produto <strong>{{ product?.name
                                    }}</strong>
                                automaticamente.</p>
                        </div>

                        <div class="flex flex-col gap-2">
                            <label class="text-sm font-light italic text-[#3a5528] tracking-wide">Data e Hora</label>
                            <RoccaDateTimePicker v-model="scheduledDate"
                                placeholder="Selecione data e hora de publicação" />
                            <p class="text-xs text-[#3a5528]/60 italic">O produto ficará privado até a data escolhida.
                            </p>
                        </div>

                        <div class="flex gap-3 pt-4">
                            <button v-if="isEditing && isScheduled" @click="isEditing = false"
                                class="px-6 py-3 bg-[#0f2301] text-[#3a5528] border border-[#0f2301]/20 rounded-lg hover:bg-[#0f2301]/80 transition-all italic tracking-wide">
                                Voltar
                            </button>

                            <button @click="saveSchedule"
                                class="flex-1 py-3 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#0f2301]/90 transition-all italic tracking-wide font-light flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
                                <span v-if="isEditing">Atualizar Agendamento</span>
                                <span v-else>Confirmar Agendamento</span>
                            </button>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    </transition>

    <!-- Modal de Confirmação de Cancelamento -->
    <ConfirmCancelScheduleModal :isOpen="showCancelModal" :product="product" @close="showCancelModal = false"
        @confirmed="handleCancelConfirmed" />
</template>

<script setup>
import { X, CalendarDays, Trash2, Clock, LoaderCircle } from 'lucide-vue-next'
import { ref, computed, watch } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import RoccaDateTimePicker from '@/components/common/RoccaDateTimePicker.vue'
import ConfirmCancelScheduleModal from './ConfirmCancelScheduleModal.vue'

const props = defineProps({
    isOpen: Boolean,
    product: Object
})

const emit = defineEmits(['close', 'updated'])
const toast = useToast()

const loading = ref(false)
const isEditing = ref(false)
const scheduledDate = ref('')
const showCancelModal = ref(false)

const isScheduled = computed(() => props.product?.is_scheduled)

const formattedDate = computed(() => {
    if (!props.product?.scheduled_publish_at) return ''
    const date = new Date(props.product.scheduled_publish_at)
    return date.toLocaleString('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    })
})

const closeModal = () => {
    emit('close')
    isEditing.value = false
    scheduledDate.value = ''
}

// Cancelar agendamento - agora abre modal de confirmação
const handleCancelConfirmed = () => {
    emit('updated')
    closeModal()
}

const saveSchedule = async () => {
    if (!scheduledDate.value) {
        toast.warning("Selecione uma data e hora")
        return
    }

    const dateObj = new Date(scheduledDate.value)
    if (dateObj <= new Date()) {
        toast.warning("A data deve ser futura")
        return
    }

    loading.value = true
    try {
        // Envia no formato ISO
        await api.post(`/admin/products/schedule/${props.product.id}`, {
            scheduled_publish_at: dateObj.toISOString()
        })
        toast.success("Agendamento salvo com sucesso!")
        emit('updated')
        closeModal()
    } catch (e) {
        console.error(e)
        toast.error(e.response?.data?.error || "Erro ao salvar agendamento")
    } finally {
        loading.value = false
    }
}

// Quando o modal abre, se ja estiver agendado, preenche o input (caso queira editar)
watch(() => props.isOpen, (newVal) => {
    if (newVal && props.product) {
        isEditing.value = false
        if (props.product.scheduled_publish_at) {
            // Formatar para datetime-local input: YYYY-MM-DDThh:mm
            const date = new Date(props.product.scheduled_publish_at)
            // Ajuste de fuso horário local para o input
            const offset = date.getTimezoneOffset()
            const localDate = new Date(date.getTime() - (offset * 60 * 1000))
            scheduledDate.value = localDate.toISOString().slice(0, 16)
        } else {
            scheduledDate.value = ''
        }
    }
})

</script>

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
