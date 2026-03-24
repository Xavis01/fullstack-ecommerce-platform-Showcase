<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="closeModal"
            class="fixed inset-0 z-50 flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-md rounded-2xl shadow-2xl relative overflow-hidden border border-[#0f2301]/10">

                <!-- Header -->
                <div class="bg-[#0f2301] px-8 py-5 flex items-center gap-3">
                    <UserPlus class="text-[#0f2301]" :size="20" />
                    <h2 class="text-lg font-['Montserrat'] font-light italic tracking-widest text-[#0f2301] uppercase">
                        Criar Usuário
                    </h2>
                    <button @click="closeModal"
                        class="ml-auto text-[#0f2301]/60 hover:text-[#0f2301] transition-colors">
                        <X :size="20" />
                    </button>
                </div>

                <!-- Body -->
                <div class="px-8 py-6 space-y-5">
                    <!-- Nome -->
                    <div>
                        <label class="label">Nome Completo</label>
                        <input v-model="form.name" type="text" placeholder="Nome do usuário" class="input" 
                            @input="form.name = form.name.replace(/[^a-zA-ZÀ-ÖØ-öø-ÿ\s\'-]/g, '')" />
                    </div>

                    <!-- Email -->
                    <div>
                        <label class="label">Email</label>
                        <input v-model="form.email" type="email" placeholder="email@exemplo.com" class="input" />
                    </div>

                    <!-- Senha -->
                    <div>
                        <label class="label">Senha</label>
                        <div class="relative">
                            <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" class="input pr-10" />
                            <button type="button" @click="showPassword = !showPassword" tabindex="-1"
                                class="absolute right-3 top-1/2 -translate-y-1/2 text-[#8c9e78] hover:text-[#3a5528] transition-colors focus:outline-none">
                                <Eye v-if="!showPassword" :size="20" stroke-width="1.5" />
                                <EyeOff v-else :size="20" stroke-width="1.5" />
                            </button>
                        </div>
                    </div>

                    <!-- Admin toggle -->
                    <div class="flex items-center gap-3 pt-1">
                        <button @click="form.is_admin = !form.is_admin"
                            :class="form.is_admin ? 'bg-[#0f2301] border-[#0f2301]' : 'bg-white border-[#0f2301]/30'"
                            class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all">
                            <Check v-if="form.is_admin" class="text-[#0f2301]" :size="12" />
                        </button>
                        <span class="text-sm font-['Montserrat'] italic text-[#3a5528] tracking-wide uppercase">
                            Conceder Acesso Administrativo
                        </span>
                    </div>
                </div>

                <!-- Footer -->
                <div class="px-8 pb-7 flex gap-3">
                    <button @click="closeModal"
                        class="flex-1 py-2.5 rounded-lg border border-[#0f2301]/30 text-[#3a5528] text-sm font-light italic tracking-wide hover:bg-[#0f2301]/40 transition-all">
                        Cancelar
                    </button>
                    <button @click="submit" :disabled="saving"
                        class="flex-1 py-2.5 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all disabled:opacity-60 flex items-center justify-center gap-2">
                        <Loader2 v-if="saving" class="animate-spin" :size="16" />
                        <span>{{ saving ? 'Salvando...' : 'Criar Usuário' }}</span>
                    </button>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api'
import { X, UserPlus, Check, Loader2, Eye, EyeOff } from 'lucide-vue-next'

const props = defineProps({ isOpen: Boolean })
const emit = defineEmits(['close', 'created'])
const toast = useToast()

const saving = ref(false)
const showPassword = ref(false)
const form = ref({ name: '', email: '', password: '', is_admin: false })

watch(() => props.isOpen, (open) => {
    if (open) {
        form.value = { name: '', email: '', password: '', is_admin: false }
        showPassword.value = false
    }
})

async function submit() {
    if (!form.value.name || !form.value.email || !form.value.password) {
        toast.warning('Preencha todos os campos obrigatórios.')
        return
    }
    saving.value = true
    try {
        await api.post('/admin/users/create', form.value)
        toast.success('Usuário criado com sucesso!')
        emit('created')
        closeModal()
    } catch (e) {
        toast.error(e.response?.data?.error || 'Erro ao criar usuário.')
    } finally {
        saving.value = false
    }
}

function closeModal() { emit('close') }
</script>

<style scoped>
.input {
    @apply w-full px-4 py-2.5 border border-[#0f2301]/20 rounded-lg shadow-sm bg-[#0f2301]/10 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#0f2301]/60 transition-colors;
    font-family: 'Montserrat', sans-serif;
    font-style: italic;
    letter-spacing: 0.025em;
}

.label {
    @apply block text-sm font-light text-[#3a5528] mb-1.5;
    font-family: 'Montserrat', sans-serif;
    font-style: italic;
}

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
