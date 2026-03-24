<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import { Settings, Save, AlertCircle, Loader2, Phone, Eye, EyeOff, Mail, MailCheck, ShieldCheck, LoaderCircle } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'

const userStore = useUserStore()
const router = useRouter()
const toast = useToast()

const loading = ref(true)
const saving = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const formData = ref({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: ''
})

// ─── Estado de verificação de e-mail ─────────────────────────────────────────
const emailVerificationPanel = ref(false)   // Mostra painel de OTP
const pendingEmail = ref('')                 // Novo e-mail aguardando confirmação
const verifyCode = ref('')                   // Código digitado
const verifyError = ref('')
const verifyLoading = ref(false)
const resending = ref(false)
const resendCooldown = ref(0)
const timerSeconds = ref(900)
let timerInterval = null
let cooldownInterval = null

import { computed } from 'vue'
const formatTimer = computed(() => {
    const m = Math.floor(timerSeconds.value / 60).toString().padStart(2, '0')
    const s = (timerSeconds.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
})

const startTimer = () => {
    clearInterval(timerInterval)
    timerSeconds.value = 900
    timerInterval = setInterval(() => {
        if (timerSeconds.value > 0) timerSeconds.value--
        else clearInterval(timerInterval)
    }, 1000)
}

const startCooldown = () => {
    resendCooldown.value = 60
    clearInterval(cooldownInterval)
    cooldownInterval = setInterval(() => {
        if (resendCooldown.value > 0) resendCooldown.value--
        else clearInterval(cooldownInterval)
    }, 1000)
}

// ────────────────────────────────────────────────────────────────────────────

const fetchProfile = async () => {
    loading.value = true
    try {
        const response = await api.get('/me')
        formData.value.name = response.data.name
        formData.value.email = response.data.email
        formData.value.phone = response.data.phone || ''
    } catch (error) {
        toast.error('Erro ao carregar dados do perfil')
    } finally {
        loading.value = false
    }
}

const handleSave = async () => {
    if (formData.value.password && formData.value.password !== formData.value.confirmPassword) {
        toast.error('As senhas não coincidem.')
        return
    }

    saving.value = true
    try {
        const payload = {
            name: formData.value.name,
            email: formData.value.email,
            phone: formData.value.phone
        }
        if (formData.value.password) {
            payload.password = formData.value.password
        }

        const response = await api.put('/user/profile', payload)

        // Se o backend pediu verificação de e-mail
        if (response.data.email_verification_required) {
            pendingEmail.value = response.data.pending_email
            emailVerificationPanel.value = true
            verifyCode.value = ''
            verifyError.value = ''
            startTimer()
            startCooldown()
            toast.info(`Código enviado para ${pendingEmail.value}`)
            return
        }

        // Atualização normal (sem mudança de e-mail)
        if (response.data.token) {
            userStore.user = response.data.user
            localStorage.setItem('token', response.data.token)
        }
        toast.success(response.data.message || 'Perfil atualizado com sucesso!')
        formData.value.password = ''
        formData.value.confirmPassword = ''
    } catch (error) {
        toast.error(error.response?.data?.error || 'Erro ao salvar alterações.')
    } finally {
        saving.value = false
    }
}

const handleVerifyEmailChange = async () => {
    if (verifyCode.value.length < 6) return
    verifyLoading.value = true
    verifyError.value = ''
    try {
        const res = await api.post('/auth/verify-email', {
            email: pendingEmail.value,
            code: verifyCode.value,
            purpose: 'change_email'
        })
        // Atualiza token e store
        if (res.data.token) {
            userStore.user = res.data.user
            localStorage.setItem('token', res.data.token)
        }
        // Atualiza o campo de e-mail no formulário
        formData.value.email = pendingEmail.value
        emailVerificationPanel.value = false
        clearInterval(timerInterval)
        clearInterval(cooldownInterval)
        toast.success('E-mail atualizado com sucesso!')
    } catch (err) {
        const status = err.response?.status
        if (status === 410) {
            verifyError.value = 'Código expirado. Clique em "Reenviar código".'
        } else {
            verifyError.value = err.response?.data?.error || 'Código incorreto. Tente novamente.'
        }
    } finally {
        verifyLoading.value = false
    }
}

const handleResendEmailChange = async () => {
    resending.value = true
    try {
        await api.post('/auth/send-verification', {
            email: pendingEmail.value,
            purpose: 'change_email'
        })
        startTimer()
        startCooldown()
        verifyError.value = ''
        toast.success('Novo código enviado!')
    } catch (err) {
        toast.error(err.response?.data?.error || 'Erro ao reenviar código.')
    } finally {
        resending.value = false
    }
}

const cancelEmailVerification = () => {
    emailVerificationPanel.value = false
    // Restaura o e-mail original
    fetchProfile()
    clearInterval(timerInterval)
    clearInterval(cooldownInterval)
    verifyCode.value = ''
    verifyError.value = ''
}

const formatPhone = () => {
    let v = formData.value.phone.replace(/\D/g, '')
    if (v.length > 0) v = '(' + v
    if (v.length > 3) v = v.slice(0, 3) + ') ' + v.slice(3)
    if (v.length > 10) v = v.slice(0, 10) + '-' + v.slice(10, 14)
    formData.value.phone = v
}

onMounted(() => {
    if (!localStorage.getItem('token')) {
        router.push('/')
        return
    }
    fetchProfile()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pt-4 pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-8 max-w-3xl mx-auto">
            <h1
                class="text-3xl font-['Montserrat'] font-light text-[#3a5528] italic mb-2 tracking-wide flex items-center gap-3">
                <Settings :size="32" class="text-[#0f2301]" />
                Minha Conta
            </h1>
            <p class="text-[#8c9e78] font-light">Gerencie suas informações pessoais e credenciais de acesso.</p>
        </div>

        <!-- Content -->
        <div class="px-4 sm:px-10 max-w-3xl mx-auto">
            <div v-if="loading" class="flex justify-center py-20">
                <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
            </div>

            <div v-else
                class="bg-white/70 backdrop-blur-sm border border-[#eaddcf] rounded-2xl shadow-sm overflow-hidden relative">
                <div class="absolute top-0 left-0 w-full h-2 bg-[#0f2301]"></div>

                <div class="p-8 sm:p-10 space-y-8">

                    <!-- Dados Pessoais -->
                    <section>
                        <h2 class="text-lg font-['Montserrat'] italic font-medium text-[#3a5528] mb-4">Dados Pessoais
                        </h2>

                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-light text-[#8c9e78] mb-1">Nome Completo</label>
                                <input v-model="formData.name" type="text"
                                    @input="formData.name = formData.name.replace(/[^a-zA-ZÀ-ÖØ-öø-ÿ\s\'-]/g, '')"
                                    class="w-full bg-[#faf9f0] border border-[#eaddcf] rounded-xl px-4 py-3 text-[#3a5528] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors"
                                    placeholder="Seu nome" />
                            </div>

                            <div>
                                <label class="block text-sm font-light text-[#8c9e78] mb-1 flex items-center gap-1">
                                    <Mail class="w-3.5 h-3.5" /> E-mail
                                </label>
                                <input v-model="formData.email" type="email"
                                    class="w-full bg-[#faf9f0] border border-[#eaddcf] rounded-xl px-4 py-3 text-[#3a5528] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors"
                                    placeholder="seu@email.com" />
                                <p class="text-xs text-[#8c9e78] font-light mt-1 italic">
                                    Ao alterar, enviaremos um código de confirmação para o novo endereço.
                                </p>
                            </div>

                            <div>
                                <label class="block text-sm font-light text-[#8c9e78] mb-1 flex items-center gap-1">
                                    <Phone class="w-3.5 h-3.5" /> Telefone
                                </label>
                                <input v-model="formData.phone" type="text"
                                    class="w-full bg-[#faf9f0] border border-[#eaddcf] rounded-xl px-4 py-3 text-[#3a5528] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors"
                                    placeholder="(27) 99999-9999" maxlength="15" @input="formatPhone" />
                            </div>
                        </div>
                    </section>

                    <hr class="border-[#eaddcf]">

                    <!-- Segurança -->
                    <section>
                        <h2 class="text-lg font-['Montserrat'] italic font-medium text-[#3a5528] mb-4">Segurança</h2>

                        <div
                            class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6 flex gap-3 text-sm text-yellow-800 font-light">
                            <AlertCircle class="w-5 h-5 flex-shrink-0" />
                            <p>Deixe os campos de senha em branco se não desejar alterá-la.</p>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-light text-[#8c9e78] mb-1">Nova Senha</label>
                                <div class="relative">
                                    <input v-model="formData.password" :type="showPassword ? 'text' : 'password'"
                                        class="w-full bg-[#faf9f0] border border-[#eaddcf] rounded-xl px-4 py-3 pr-10 text-[#3a5528] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors"
                                        placeholder="••••••••" />
                                    <button type="button" @click="showPassword = !showPassword" tabindex="-1"
                                        class="absolute right-3 top-1/2 -translate-y-1/2 text-[#8c9e78] hover:text-[#3a5528] transition-colors focus:outline-none">
                                        <Eye v-if="!showPassword" :size="20" stroke-width="1.5" />
                                        <EyeOff v-else :size="20" stroke-width="1.5" />
                                    </button>
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-light text-[#8c9e78] mb-1">Confirmar Nova Senha</label>
                                <div class="relative">
                                    <input v-model="formData.confirmPassword"
                                        :type="showConfirmPassword ? 'text' : 'password'"
                                        class="w-full bg-[#faf9f0] border border-[#eaddcf] rounded-xl px-4 py-3 pr-10 text-[#3a5528] focus:outline-none focus:border-[#0f2301] focus:ring-1 focus:ring-[#0f2301] transition-colors"
                                        placeholder="••••••••" />
                                    <button type="button" @click="showConfirmPassword = !showConfirmPassword"
                                        tabindex="-1"
                                        class="absolute right-3 top-1/2 -translate-y-1/2 text-[#8c9e78] hover:text-[#3a5528] transition-colors focus:outline-none">
                                        <Eye v-if="!showConfirmPassword" :size="20" stroke-width="1.5" />
                                        <EyeOff v-else :size="20" stroke-width="1.5" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- ─── Painel de verificação de e-mail (inline) ─────────────── -->
                    <Transition enter-active-class="transition-all duration-400 ease-out"
                        enter-from-class="opacity-0 -translate-y-4 scale-98"
                        enter-to-class="opacity-100 translate-y-0 scale-100"
                        leave-active-class="transition-all duration-300 ease-in"
                        leave-from-class="opacity-100 translate-y-0 scale-100"
                        leave-to-class="opacity-0 -translate-y-4 scale-98">
                        <section v-if="emailVerificationPanel"
                            class="bg-[#0f2301]/5 border border-[#0f2301]/20 rounded-2xl p-6 space-y-5">

                            <div class="flex items-start gap-4">
                                <div
                                    class="w-11 h-11 rounded-full bg-[#0f2301]/10 flex items-center justify-center flex-shrink-0">
                                    <MailCheck :size="22" class="text-[#0f2301]" />
                                </div>
                                <div>
                                    <h3
                                        class="font-['Montserrat'] font-medium text-[#0f2301] text-sm tracking-wide uppercase italic mb-1">
                                        Verificação de E-mail
                                    </h3>
                                    <p class="text-sm font-light text-[#3a5528] leading-relaxed">
                                        Enviamos um código de 6 dígitos para
                                        <strong class="font-medium">{{ pendingEmail }}</strong>.
                                        Insira o código abaixo para confirmar a alteração.
                                    </p>
                                </div>
                            </div>

                            <!-- Input OTP -->
                            <div>
                                <label class="block text-sm font-light text-[#8c9e78] mb-2">Código de
                                    Verificação</label>
                                <input v-model="verifyCode" type="text"
                                    class="w-full bg-white border rounded-xl px-4 py-3 text-center tracking-[0.5em] text-xl font-mono focus:outline-none focus:ring-1 transition-colors"
                                    :class="verifyError ? 'border-red-400 text-red-700 focus:ring-red-300' : 'border-[#eaddcf] text-[#0f2301] focus:border-[#0f2301] focus:ring-[#0f2301]'"
                                    placeholder="000000" maxlength="6"
                                    @input="verifyCode = verifyCode.replace(/\D/g, '')"
                                    @keyup.enter="handleVerifyEmailChange" />
                            </div>

                            <!-- Expiração e reenvio -->
                            <div class="flex items-center justify-between text-xs font-light text-[#8c9e78]"
                                style="font-family: 'Montserrat', sans-serif;">
                                <span>
                                    Expira em
                                    <span :class="timerSeconds < 60 ? 'text-red-500 font-medium' : 'text-[#3a5528]'">
                                        {{ formatTimer }}
                                    </span>
                                </span>
                                <button type="button" @click="handleResendEmailChange"
                                    :disabled="resendCooldown > 0 || resending"
                                    class="text-[#0f2301] underline underline-offset-2 hover:text-[#3a5528] disabled:opacity-40 disabled:cursor-not-allowed transition-opacity">
                                    <span v-if="resending">
                                        <LoaderCircle :size="12" class="inline animate-spin" /> Enviando...
                                    </span>
                                    <span v-else-if="resendCooldown > 0">Reenviar em {{ resendCooldown }}s</span>
                                    <span v-else>Reenviar código</span>
                                </button>
                            </div>

                            <!-- Erro -->
                            <Transition enter-active-class="transition-all duration-200"
                                enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0"
                                leave-active-class="transition-all duration-200"
                                leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
                                <p v-if="verifyError"
                                    class="text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl px-4 py-3 font-light">
                                    {{ verifyError }}
                                </p>
                            </Transition>

                            <!-- Ações -->
                            <div class="flex gap-3">
                                <button type="button" @click="cancelEmailVerification"
                                    class="flex-1 border border-[#eaddcf] text-[#8c9e78] py-3 rounded-xl font-light text-sm hover:bg-[#faf9f0] transition-colors">
                                    Cancelar
                                </button>
                                <button type="button" @click="handleVerifyEmailChange"
                                    :disabled="verifyLoading || verifyCode.length < 6"
                                    class="flex-1 flex items-center justify-center gap-2 bg-[#0f2301] text-[#fffdf2] py-3 rounded-xl font-light text-sm hover:bg-[#3a5528] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                                    <LoaderCircle v-if="verifyLoading" class="w-4 h-4 animate-spin" />
                                    <ShieldCheck v-else class="w-4 h-4" />
                                    {{ verifyLoading ? 'Verificando...' : 'Confirmar' }}
                                </button>
                            </div>
                        </section>
                    </Transition>

                </div>

                <!-- Footer Actions -->
                <div class="px-8 sm:px-10 py-5 bg-[#faf9f0] border-t border-[#eaddcf] flex justify-end">
                    <button @click="handleSave" :disabled="saving || loading || emailVerificationPanel"
                        class="flex items-center gap-2 bg-[#0f2301] text-[#fffdf2] px-8 py-3 rounded-xl font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
                        <Loader2 v-if="saving" class="w-5 h-5 animate-spin" />
                        <Save v-else class="w-5 h-5" />
                        {{ saving ? 'Salvando...' : 'Salvar Alterações' }}
                    </button>
                </div>

            </div>
        </div>
    </div>
</template>
