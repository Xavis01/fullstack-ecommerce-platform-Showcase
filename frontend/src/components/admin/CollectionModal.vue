<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="closeModal"
            class="fixed inset-0 z-[110] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <!-- Modal Content -->
            <div @click.stop
                class="bg-white w-full max-w-md rounded-2xl shadow-2xl p-8 relative space-y-6 border border-[#0f2301]/10"
                role="dialog" aria-modal="true">
                <!-- Botão fechar -->
                <button @click="closeModal"
                    class="absolute top-6 right-6 text-[#3a5528]/50 hover:text-[#3a5528] text-2xl transition-colors">
                    <i class="fas fa-times"></i>
                </button>

                <!-- Title -->
                <h3 class="text-2xl font-light italic text-[#3a5528] tracking-wide pr-8">
                    {{ isEditing ? 'Editar Coleção' : 'Nova Coleção' }}
                </h3>

                <form @submit.prevent="handleSubmit" class="space-y-6">
                    <!-- Nome da Coleção -->
                    <div class="space-y-2">
                        <label class="block text-sm font-light text-[#3a5528] mb-1 italic tracking-wide">
                            Nome da Coleção
                        </label>
                        <input type="text" v-model="formData.name" class="input w-full" placeholder="Ex: Verão 2026"
                            required />
                    </div>

                    <!-- Footer Buttons -->
                    <div class="flex justify-end gap-3 pt-2">
                        <button type="button" @click="closeModal"
                            class="px-4 py-2 text-[#3a5528] hover:bg-[#0f2301]/10 rounded-lg transition-colors font-light italic tracking-wide">
                            Cancelar
                        </button>
                        <button type="submit" :disabled="saving"
                            class="px-6 py-2 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#3a5528] transition-all shadow-sm font-light italic tracking-wide disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
                            <Loader2 v-if="saving" class="animate-spin" :size="15" />
                            <span>{{ isEditing ? 'Salvar' : 'Criar' }}</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Loader2 } from 'lucide-vue-next'

const props = defineProps({
    isOpen: { type: Boolean, required: true },
    editData: { type: Object, default: null },
    saving: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'save'])

const formData = ref({ name: '' })

const isEditing = computed(() => !!props.editData)

watch(() => props.isOpen, (newVal) => {
    if (newVal) {
        formData.value = props.editData ? { ...props.editData } : { name: '' }
    }
})

watch(() => props.editData, (newVal) => {
    if (newVal) formData.value = { ...newVal }
})

const closeModal = () => {
    emit('close')
    formData.value = { name: '' }
}

const handleSubmit = () => {
    emit('save', formData.value)
}
</script>

<style scoped>
.input {
    @apply px-3 py-2.5 border border-[#0f2301]/30 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#0f2301] focus:border-[#0f2301] transition-all bg-white;
    font-family: 'Montserrat', sans-serif;
    font-style: italic;
    letter-spacing: 0.025em;
    color: #3a5528;
}

.input::placeholder {
    color: rgba(83, 113, 61, 0.4);
    font-style: italic;
}

/* Transição suave */
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
