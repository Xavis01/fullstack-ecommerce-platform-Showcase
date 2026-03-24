<template>
    <div>
        <!-- Backdrop -->
        <Transition enter-active-class="transition-all duration-500 ease-out" enter-from-class="opacity-0"
            enter-to-class="opacity-100" leave-active-class="transition-all duration-300 ease-in"
            leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="visible" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[200]" @click="handleClose"></div>
        </Transition>

        <!-- Modal Container -->
        <Transition enter-active-class="transition-all duration-500 ease-out" enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100" leave-active-class="transition-all duration-300 ease-in"
            leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
            <div v-if="visible"
                class="fixed inset-0 z-[200] flex items-center justify-center pb-16 pointer-events-none">
                <div class="perspective-container pointer-events-auto">
                    <div class="flip-card" :class="{ 'is-flipped': isRegistering }">

                        <!-- ─── FRENTE: LOGIN + FORGOT PASSWORD ─── -->
                        <div class="flip-card-face flip-card-front">
                            <div class="modal-card">
                                <div class="flex justify-between items-center mb-8">
                                    <h2 class="modal-title">
                                        <span v-if="loginStep === 'login'">ENTRAR</span>
                                        <span v-else-if="loginStep === 'forgot-email'">RECUPERAR SENHA</span>
                                        <span v-else>NOVA SENHA</span>
                                    </h2>
                                    <button @click="handleClose"
                                        class="text-[#3a5528] hover:opacity-60 transition-all hover:rotate-90 duration-300">
                                        <X :size="24" :stroke-width="1.5" />
                                    </button>
                                </div>

                                <Transition name="step-fade" mode="out-in">
                                    <!-- LOGIN NORMAL -->
                                    <form v-if="loginStep === 'login'" key="login" @submit.prevent="handleLogin"
                                        class="space-y-5">
                                        <div class="input-group">
                                            <label class="input-label">Email</label>
                                            <input v-model="loginForm.email" type="email" class="custom-input"
                                                :class="{ 'input-error': loginError }" placeholder="seu@email.com"
                                                required autocomplete="email" />
                                        </div>

                                        <div class="input-group">
                                            <label class="input-label">Senha</label>
                                            <div class="relative">
                                                <input v-model="loginForm.password"
                                                    :type="showLoginPassword ? 'text' : 'password'"
                                                    class="custom-input pr-10" :class="{ 'input-error': loginError }"
                                                    placeholder="••••••••" required autocomplete="current-password" />
                                                <button type="button" @click="showLoginPassword = !showLoginPassword"
                                                    tabindex="-1"
                                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-[#3a5528] hover:text-[#0f2301] transition-colors focus:outline-none">
                                                    <Eye v-if="!showLoginPassword" :size="20" stroke-width="1.5" />
                                                    <EyeOff v-else :size="20" stroke-width="1.5" />
                                                </button>
                                            </div>
                                            <!-- Esqueceu a senha -->
                                            <div class="text-right mt-1">
                                                <button type="button" @click="loginStep = 'forgot-email'"
                                                    class="text-xs font-light italic text-[#8c9e78] hover:text-[#0f2301] transition-colors underline underline-offset-2"
                                                    style="font-family: 'Montserrat', sans-serif;">
                                                    Esqueceu a senha?
                                                </button>
                                            </div>
                                        </div>

                                        <Transition enter-active-class="transition-all duration-200"
                                            enter-from-class="opacity-0 -translate-y-2"
                                            enter-to-class="opacity-100 translate-y-0"
                                            leave-active-class="transition-all duration-200"
                                            leave-from-class="opacity-100 translate-y-0"
                                            leave-to-class="opacity-0 -translate-y-2">
                                            <p v-if="loginError" class="error-message">{{ loginError }}</p>
                                        </Transition>

                                        <button type="submit" class="submit-btn" :disabled="loginLoading">
                                            <span v-if="!loginLoading"
                                                class="flex items-center justify-center gap-2">ENTRAR</span>
                                            <LoaderCircle v-else class="animate-spin mx-auto" :size="20" />
                                        </button>

                                        <div class="text-center mt-6">
                                            <p class="toggle-text">
                                                Ainda não tem conta?
                                                <button type="button" @click="flipToRegister"
                                                    class="toggle-link">CADASTRAR</button>
                                            </p>
                                        </div>
                                    </form>

                                    <!-- STEP: INFORME SEU E-MAIL -->
                                    <div v-else-if="loginStep === 'forgot-email'" key="forgot-email" class="space-y-5">
                                        <p class="text-sm font-light text-[#3a5528] leading-relaxed"
                                            style="font-family:'Montserrat',sans-serif;">
                                            Informe o e-mail da sua conta e enviaremos um código para redefinir sua
                                            senha.
                                        </p>

                                        <div class="input-group">
                                            <label class="input-label">E-mail cadastrado</label>
                                            <input v-model="forgotEmail" type="email" class="custom-input"
                                                :class="{ 'input-error': forgotError }" placeholder="seu@email.com"
                                                autocomplete="email" />
                                        </div>

                                        <Transition enter-active-class="transition-all duration-200"
                                            enter-from-class="opacity-0 -translate-y-2"
                                            enter-to-class="opacity-100 translate-y-0"
                                            leave-active-class="transition-all duration-200"
                                            leave-from-class="opacity-100 translate-y-0"
                                            leave-to-class="opacity-0 -translate-y-2">
                                            <p v-if="forgotError" class="error-message">{{ forgotError }}</p>
                                        </Transition>

                                        <button type="button" @click="handleForgotSend" class="submit-btn"
                                            :disabled="forgotLoading || !forgotEmail">
                                            <span v-if="!forgotLoading" class="flex items-center justify-center gap-2">
                                                <Mail :size="16" /> Enviar Código
                                            </span>
                                            <LoaderCircle v-else class="animate-spin mx-auto" :size="20" />
                                        </button>

                                        <div class="text-center">
                                            <button type="button" @click="loginStep = 'login'"
                                                class="text-xs font-light italic text-[#8c9e78] hover:text-[#3a5528] transition-colors"
                                                style="font-family: 'Montserrat', sans-serif;">
                                                ← Voltar ao login
                                            </button>
                                        </div>
                                    </div>

                                    <!-- STEP: CÓDIGO + NOVA SENHA -->
                                    <div v-else key="forgot-verify" class="space-y-5">
                                        <div class="flex flex-col items-center gap-2 py-1">
                                            <div
                                                class="w-12 h-12 rounded-full bg-[#0f2301]/10 flex items-center justify-center">
                                                <KeyRound :size="22" class="text-[#0f2301]" />
                                            </div>
                                            <p class="text-center text-sm font-light text-[#3a5528] leading-relaxed"
                                                style="font-family:'Montserrat',sans-serif;">
                                                Código enviado para<br><strong class="font-medium">{{ forgotEmail
                                                }}</strong>
                                            </p>
                                        </div>

                                        <div class="input-group">
                                            <label class="input-label">Código de Verificação</label>
                                            <input v-model="forgotCode" type="text"
                                                class="custom-input text-center tracking-[0.4em] text-xl"
                                                :class="{ 'input-error': forgotError }" placeholder="000000"
                                                maxlength="6" @input="forgotCode = forgotCode.replace(/\D/g, '')" />
                                        </div>

                                        <div class="input-group">
                                            <label class="input-label">Nova Senha</label>
                                            <div class="relative">
                                                <input v-model="forgotNewPassword"
                                                    :type="showForgotPassword ? 'text' : 'password'"
                                                    class="custom-input pr-10" :class="{ 'input-error': forgotError }"
                                                    placeholder="••••••••" minlength="6" />
                                                <button type="button" @click="showForgotPassword = !showForgotPassword"
                                                    tabindex="-1"
                                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-[#3a5528] hover:text-[#0f2301] transition-colors focus:outline-none">
                                                    <Eye v-if="!showForgotPassword" :size="20" stroke-width="1.5" />
                                                    <EyeOff v-else :size="20" stroke-width="1.5" />
                                                </button>
                                            </div>
                                            <p class="input-hint">Mínimo 6 caracteres</p>
                                        </div>

                                        <!-- timer + reenvio -->
                                        <div class="flex items-center justify-between text-xs font-light"
                                            style="font-family:'Montserrat',sans-serif;">
                                            <span class="text-[#8c9e78]">
                                                Expira em <span
                                                    :class="forgotTimerSeconds < 60 ? 'text-red-500 font-medium' : 'text-[#3a5528]'">{{
                                                        forgotFormatTimer }}</span>
                                            </span>
                                            <button type="button" @click="handleForgotResend"
                                                :disabled="forgotResendCooldown > 0 || forgotResending"
                                                class="text-[#0f2301] underline underline-offset-2 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity">
                                                <span v-if="forgotResending">
                                                    <LoaderCircle :size="12" class="inline animate-spin" /> Enviando...
                                                </span>
                                                <span v-else-if="forgotResendCooldown > 0">Reenviar em {{
                                                    forgotResendCooldown }}s</span>
                                                <span v-else>Reenviar código</span>
                                            </button>
                                        </div>

                                        <Transition enter-active-class="transition-all duration-200"
                                            enter-from-class="opacity-0 -translate-y-2"
                                            enter-to-class="opacity-100 translate-y-0"
                                            leave-active-class="transition-all duration-200"
                                            leave-from-class="opacity-100 translate-y-0"
                                            leave-to-class="opacity-0 -translate-y-2">
                                            <p v-if="forgotError" class="error-message">{{ forgotError }}</p>
                                        </Transition>

                                        <button type="button" @click="handleResetPassword" class="submit-btn"
                                            :disabled="forgotLoading || forgotCode.length < 6 || forgotNewPassword.length < 6">
                                            <span v-if="!forgotLoading" class="flex items-center justify-center gap-2">
                                                <ShieldCheck :size="16" /> Redefinir Senha
                                            </span>
                                            <LoaderCircle v-else class="animate-spin mx-auto" :size="20" />
                                        </button>

                                        <div class="text-center">
                                            <button type="button" @click="loginStep = 'forgot-email'"
                                                class="text-xs font-light italic text-[#8c9e78] hover:text-[#3a5528] transition-colors"
                                                style="font-family: 'Montserrat', sans-serif;">
                                                ← Corrigir e-mail
                                            </button>
                                        </div>
                                    </div>
                                </Transition>
                            </div>
                        </div>

                        <!-- ─── VERSO: CADASTRO (multi-step) ─── -->
                        <div class="flip-card-face flip-card-back">
                            <div class="modal-card">
                                <div class="flex justify-between items-center mb-8">
                                    <!-- Título muda por step -->
                                    <h2 class="modal-title">
                                        <span v-if="registerStep === 'form'">CADASTRO</span>
                                        <span v-else-if="registerStep === 'verify'">VERIFICAÇÃO</span>
                                        <span v-else>CADASTRADO!</span>
                                    </h2>
                                    <button @click="handleClose"
                                        class="text-[#3a5528] hover:opacity-60 transition-all hover:rotate-90 duration-300">
                                        <X :size="24" :stroke-width="1.5" />
                                    </button>
                                </div>

                                <!-- STEP 1: Formulário de dados -->
                                <Transition name="step-fade" mode="out-in">
                                    <form v-if="registerStep === 'form'" key="form" @submit.prevent="handleRegister"
                                        class="space-y-5">
                                        <div class="input-group">
                                            <label class="input-label">Nome Completo</label>
                                            <input v-model="registerForm.name" type="text" class="custom-input"
                                                @input="registerForm.name = registerForm.name.replace(/[^a-zA-ZÀ-ÖØ-öø-ÿ\s\'-]/g, '')"
                                                :class="{ 'input-error': registerError }"
                                                placeholder="Seu nome completo" required autocomplete="name" />
                                        </div>

                                        <div class="input-group">
                                            <label class="input-label">Email</label>
                                            <input v-model="registerForm.email" type="email" class="custom-input"
                                                :class="{ 'input-error': registerError }" placeholder="seu@email.com"
                                                required autocomplete="email" />
                                        </div>

                                        <div class="input-group">
                                            <label class="input-label">Senha</label>
                                            <div class="relative">
                                                <input v-model="registerForm.password"
                                                    :type="showRegisterPassword ? 'text' : 'password'"
                                                    class="custom-input pr-10" :class="{ 'input-error': registerError }"
                                                    placeholder="••••••••" required autocomplete="new-password"
                                                    minlength="6" />
                                                <button type="button"
                                                    @click="showRegisterPassword = !showRegisterPassword" tabindex="-1"
                                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-[#3a5528] hover:text-[#0f2301] transition-colors focus:outline-none">
                                                    <Eye v-if="!showRegisterPassword" :size="20" stroke-width="1.5" />
                                                    <EyeOff v-else :size="20" stroke-width="1.5" />
                                                </button>
                                            </div>
                                            <p class="input-hint">Mínimo 6 caracteres</p>
                                        </div>

                                        <Transition enter-active-class="transition-all duration-200"
                                            enter-from-class="opacity-0 -translate-y-2"
                                            enter-to-class="opacity-100 translate-y-0"
                                            leave-active-class="transition-all duration-200"
                                            leave-from-class="opacity-100 translate-y-0"
                                            leave-to-class="opacity-0 -translate-y-2">
                                            <p v-if="registerError" class="error-message">{{ registerError }}</p>
                                        </Transition>

                                        <button type="submit" class="submit-btn" :disabled="registerLoading">
                                            <span v-if="!registerLoading"
                                                class="flex items-center justify-center gap-2">
                                                <Mail :size="16" />
                                                Continuar
                                            </span>
                                            <LoaderCircle v-else class="animate-spin mx-auto" :size="20" />
                                        </button>

                                        <div class="text-center mt-6">
                                            <p class="toggle-text">
                                                Já tem conta?
                                                <button type="button" @click="flipToLogin"
                                                    class="toggle-link">ENTRAR</button>
                                            </p>
                                        </div>
                                    </form>

                                    <!-- STEP 2: Verificação OTP -->
                                    <div v-else-if="registerStep === 'verify'" key="verify" class="space-y-5">
                                        <!-- Ícone de e-mail enviado -->
                                        <div class="flex flex-col items-center gap-3 py-2">
                                            <div
                                                class="w-14 h-14 rounded-full bg-[#0f2301]/10 flex items-center justify-center">
                                                <MailCheck :size="28" class="text-[#0f2301]" />
                                            </div>
                                            <p class="text-center text-sm font-light text-[#3a5528] leading-relaxed">
                                                Enviamos um código de 6 dígitos para<br>
                                                <strong class="font-medium">{{ registerForm.email }}</strong>
                                            </p>
                                        </div>

                                        <!-- Input OTP -->
                                        <div class="input-group">
                                            <label class="input-label">Código de Verificação</label>
                                            <input v-model="verifyCode" type="text"
                                                class="custom-input text-center tracking-[0.4em] text-xl"
                                                :class="{ 'input-error': verifyError }" placeholder="000000"
                                                maxlength="6" @input="verifyCode = verifyCode.replace(/\D/g, '')"
                                                @keyup.enter="handleVerifyRegister" />
                                        </div>

                                        <!-- Expiração e reenvio -->
                                        <div class="flex items-center justify-between text-xs font-light"
                                            style="font-family: 'Montserrat', sans-serif;">
                                            <span class="text-[#8c9e78]">
                                                Expira em <span
                                                    :class="timerSeconds < 60 ? 'text-red-500 font-medium' : 'text-[#3a5528]'">{{
                                                        formatTimer }}</span>
                                            </span>
                                            <button type="button" @click="handleResendCode"
                                                :disabled="resendCooldown > 0 || resending"
                                                class="text-[#0f2301] underline underline-offset-2 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity">
                                                <span v-if="resending">
                                                    <LoaderCircle :size="12" class="inline animate-spin" /> Enviando...
                                                </span>
                                                <span v-else-if="resendCooldown > 0">Reenviar em {{ resendCooldown
                                                }}s</span>
                                                <span v-else>Reenviar código</span>
                                            </button>
                                        </div>

                                        <Transition enter-active-class="transition-all duration-200"
                                            enter-from-class="opacity-0 -translate-y-2"
                                            enter-to-class="opacity-100 translate-y-0"
                                            leave-active-class="transition-all duration-200"
                                            leave-from-class="opacity-100 translate-y-0"
                                            leave-to-class="opacity-0 -translate-y-2">
                                            <p v-if="verifyError" class="error-message">{{ verifyError }}</p>
                                        </Transition>

                                        <button type="button" @click="handleVerifyRegister" class="submit-btn"
                                            :disabled="verifyLoading || verifyCode.length < 6">
                                            <span v-if="!verifyLoading" class="flex items-center justify-center gap-2">
                                                <ShieldCheck :size="16" />
                                                CONFIRMAR
                                            </span>
                                            <LoaderCircle v-else class="animate-spin mx-auto" :size="20" />
                                        </button>

                                        <div class="text-center">
                                            <button type="button" @click="registerStep = 'form'"
                                                class="text-xs font-light italic text-[#8c9e78] hover:text-[#3a5528] transition-colors"
                                                style="font-family: 'Montserrat', sans-serif;">
                                                ← Voltar e corrigir e-mail
                                            </button>
                                        </div>
                                    </div>
                                </Transition>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </Transition>
    </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { useToast } from 'vue-toastification'
import { X, LoaderCircle, Eye, EyeOff, Mail, MailCheck, ShieldCheck, KeyRound } from 'lucide-vue-next'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['close'])

const router = useRouter()
const userStore = useUserStore()
const toast = useToast()

// ─── Estado do flip ───────────────────────────────────────────────────────────
const isRegistering = ref(false)
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showForgotPassword = ref(false)

// ─── Steps de LOGIN (inclui forgot password) ──────────────────────────────────
const loginStep = ref('login') // 'login' | 'forgot-email' | 'forgot-verify'
const forgotEmail = ref('')
const forgotCode = ref('')
const forgotNewPassword = ref('')
const forgotError = ref('')
const forgotLoading = ref(false)
const forgotResending = ref(false)
const forgotResendCooldown = ref(0)
const forgotTimerSeconds = ref(900)
let forgotTimerInterval = null
let forgotCooldownInterval = null

const forgotFormatTimer = computed(() => {
    const m = Math.floor(forgotTimerSeconds.value / 60).toString().padStart(2, '0')
    const s = (forgotTimerSeconds.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
})

const startForgotTimer = () => {
    clearInterval(forgotTimerInterval)
    forgotTimerSeconds.value = 900
    forgotTimerInterval = setInterval(() => {
        if (forgotTimerSeconds.value > 0) forgotTimerSeconds.value--
        else clearInterval(forgotTimerInterval)
    }, 1000)
}

const startForgotCooldown = () => {
    forgotResendCooldown.value = 60
    clearInterval(forgotCooldownInterval)
    forgotCooldownInterval = setInterval(() => {
        if (forgotResendCooldown.value > 0) forgotResendCooldown.value--
        else clearInterval(forgotCooldownInterval)
    }, 1000)
}

// ─── Formulários ──────────────────────────────────────────────────────────────
const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ name: '', email: '', password: '' })

// ─── Steps de registro ────────────────────────────────────────────────────────
const registerStep = ref('form') // 'form' | 'verify'
const verifyCode = ref('')
const verifyError = ref('')
const verifyLoading = ref(false)

// ─── Loading / Errors ─────────────────────────────────────────────────────────
const loginLoading = ref(false)
const registerLoading = ref(false)
const loginError = ref('')
const registerError = ref('')

// ─── Timer de expiração (15 min = 900s) ──────────────────────────────────────
const timerSeconds = ref(900)
let timerInterval = null

const formatTimer = computed(() => {
    const m = Math.floor(timerSeconds.value / 60).toString().padStart(2, '0')
    const s = (timerSeconds.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
})

const startTimer = () => {
    clearInterval(timerInterval)
    timerSeconds.value = 900
    timerInterval = setInterval(() => {
        if (timerSeconds.value > 0) {
            timerSeconds.value--
        } else {
            clearInterval(timerInterval)
        }
    }, 1000)
}

const stopTimer = () => {
    clearInterval(timerInterval)
    timerInterval = null
}

onUnmounted(stopTimer)

// ─── Reenvio de código ────────────────────────────────────────────────────────
const resendCooldown = ref(0)
const resending = ref(false)
let cooldownInterval = null

const startCooldown = () => {
    resendCooldown.value = 60
    cooldownInterval = setInterval(() => {
        if (resendCooldown.value > 0) resendCooldown.value--
        else clearInterval(cooldownInterval)
    }, 1000)
}

const handleResendCode = async () => {
    resending.value = true
    try {
        await api.post('/auth/send-verification', {
            email: registerForm.value.email,
            purpose: 'register'
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

// ─── Flip de navegação ────────────────────────────────────────────────────────
const flipToRegister = () => {
    loginError.value = ''
    loginStep.value = 'login'
    isRegistering.value = true
}

const flipToLogin = () => {
    registerError.value = ''
    isRegistering.value = false
    resetRegister()
}

// ─── Forgot password: enviar código ─────────────────────────────────────────
const handleForgotSend = async () => {
    forgotLoading.value = true
    forgotError.value = ''
    try {
        await api.post('/auth/forgot-password', { email: forgotEmail.value })
        loginStep.value = 'forgot-verify'
        forgotCode.value = ''
        forgotNewPassword.value = ''
        forgotError.value = ''
        startForgotTimer()
        startForgotCooldown()
    } catch (err) {
        const errData = err.response?.data
        const detail = errData?.details ? ` (${errData.details})` : ''
        forgotError.value = (errData?.error || 'Erro ao enviar código.') + detail
    } finally {
        forgotLoading.value = false
    }
}

// ─── Forgot password: reenviar código ────────────────────────────────────────
const handleForgotResend = async () => {
    forgotResending.value = true
    try {
        await api.post('/auth/forgot-password', { email: forgotEmail.value })
        startForgotTimer()
        startForgotCooldown()
        forgotError.value = ''
        toast.success('Novo código enviado!')
    } catch (err) {
        toast.error('Erro ao reenviar código.')
    } finally {
        forgotResending.value = false
    }
}

// ─── Forgot password: redefinir senha ────────────────────────────────────────
const handleResetPassword = async () => {
    if (forgotCode.value.length < 6 || forgotNewPassword.value.length < 6) return
    forgotLoading.value = true
    forgotError.value = ''
    try {
        await api.post('/auth/reset-password', {
            email: forgotEmail.value,
            code: forgotCode.value,
            new_password: forgotNewPassword.value
        })
        toast.success('Senha redefinida com sucesso! Faça login com sua nova senha.')
        // Volta ao login e pré-preenche o e-mail
        loginStep.value = 'login'
        loginForm.value.email = forgotEmail.value
        loginForm.value.password = ''
        forgotEmail.value = ''
        forgotCode.value = ''
        forgotNewPassword.value = ''
        clearInterval(forgotTimerInterval)
        clearInterval(forgotCooldownInterval)
    } catch (err) {
        const status = err.response?.status
        if (status === 410) {
            forgotError.value = 'Código expirado. Clique em "Reenviar código".'
        } else {
            forgotError.value = err.response?.data?.error || 'Código incorreto. Tente novamente.'
        }
    } finally {
        forgotLoading.value = false
    }
}

// ─── Login ────────────────────────────────────────────────────────────────────
const handleLogin = async () => {
    loginLoading.value = true
    loginError.value = ''
    try {
        const res = await api.post('/login', {
            email: loginForm.value.email,
            password: loginForm.value.password
        })
        localStorage.setItem('token', res.data.token)
        await userStore.fetchUser()
        toast.success('Logado com sucesso!')
        handleClose()
        loginForm.value = { email: '', password: '' }
    } catch (err) {
        loginError.value = 'Email ou senha inválidos'
    } finally {
        loginLoading.value = false
    }
}

// ─── Registro: Step 1 — envia OTP ────────────────────────────────────────────
const handleRegister = async () => {
    registerLoading.value = true
    registerError.value = ''
    try {
        await api.post('/register', {
            name: registerForm.value.name,
            email: registerForm.value.email,
            password: registerForm.value.password
        })
        registerStep.value = 'verify'
        verifyCode.value = ''
        verifyError.value = ''
        startTimer()
        startCooldown()
    } catch (err) {
        const errData = err.response?.data
        const detail = errData?.details ? ` (${errData.details})` : ''
        registerError.value = (errData?.error || 'Erro ao cadastrar. Tente novamente.') + detail
    } finally {
        registerLoading.value = false
    }
}

// ─── Registro: Step 2 — verifica código ──────────────────────────────────────
const handleVerifyRegister = async () => {
    if (verifyCode.value.length < 6) return
    verifyLoading.value = true
    verifyError.value = ''
    try {
        const res = await api.post('/auth/verify-email', {
            email: registerForm.value.email,
            code: verifyCode.value,
            purpose: 'register'
        })
        // Login automático
        localStorage.setItem('token', res.data.token)
        await userStore.fetchUser()
        toast.success('Bem-vindo(a) à Família Rocca!🇮')
        handleClose()
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

// ─── Fechar e resetar ────────────────────────────────────────────────────────
const resetRegister = () => {
    registerStep.value = 'form'
    verifyCode.value = ''
    verifyError.value = ''
    registerForm.value = { name: '', email: '', password: '' }
    registerError.value = ''
    stopTimer()
    clearInterval(cooldownInterval)
    resendCooldown.value = 0
}

const handleClose = () => {
    emit('close')
    setTimeout(() => {
        isRegistering.value = false
        showLoginPassword.value = false
        showRegisterPassword.value = false
        showForgotPassword.value = false
        loginStep.value = 'login'
        forgotEmail.value = ''
        forgotCode.value = ''
        forgotNewPassword.value = ''
        forgotError.value = ''
        clearInterval(forgotTimerInterval)
        clearInterval(forgotCooldownInterval)
        loginForm.value = { email: '', password: '' }
        loginError.value = ''
        resetRegister()
    }, 300)
}

watch(() => props.visible, (newVal) => {
    if (!newVal) {
        loginError.value = ''
        registerError.value = ''
    }
})
</script>

<style scoped>
.perspective-container {
    perspective: 1000px;
    width: 450px;
    max-width: 90vw;
}

.flip-card {
    position: relative;
    width: 100%;
    transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
}

.flip-card.is-flipped {
    transform: rotateY(180deg);
}

.flip-card-face {
    width: 100%;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
}

.flip-card-front {
    position: relative;
}

.flip-card-back {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    transform: rotateY(180deg);
}

.modal-card {
    background-color: #fffdf2;
    border: 1.5px solid #0f2301;
    border-radius: 4px;
    padding: 2.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.75rem;
    font-weight: 300;
    font-style: italic;
    color: #3a5528;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.input-group {
    position: relative;
}

.input-label {
    display: block;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.75rem;
    font-weight: 300;
    font-style: italic;
    color: #3a5528;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

.custom-input {
    width: 100%;
    padding: 0.875rem 1rem;
    background-color: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(90, 122, 64, 0.3);
    border-radius: 3px;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.95rem;
    font-weight: 300;
    color: #333;
    transition: all 0.3s ease;
    outline: none;
    box-sizing: border-box;
}

.custom-input:focus {
    background-color: rgba(255, 255, 255, 0.9);
    border-color: #0f2301;
    box-shadow: 0 0 0 3px rgba(90, 122, 64, 0.1);
}

.custom-input::placeholder {
    color: rgba(83, 113, 61, 0.4);
    font-style: italic;
}

.custom-input.input-error {
    border-color: #9a382d;
    background-color: rgba(154, 56, 45, 0.05);
}

.input-hint {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.7rem;
    font-weight: 300;
    font-style: italic;
    color: rgba(83, 113, 61, 0.6);
    margin-top: 0.375rem;
}

.error-message {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.8rem;
    font-weight: 300;
    font-style: italic;
    color: #9a382d;
    text-align: center;
    padding: 0.5rem;
    background-color: rgba(154, 56, 45, 0.1);
    border-radius: 3px;
}

.submit-btn {
    width: 100%;
    padding: 0.95rem 1.5rem;
    background-color: #0f2301;
    color: #fffdf2;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.875rem;
    font-weight: 300;
    font-style: italic;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(90, 122, 64, 0.2);
}

.submit-btn:hover:not(:disabled) {
    background-color: #4d6736;
    box-shadow: 0 4px 12px rgba(90, 122, 64, 0.3);
    transform: translateY(-1px);
}

.submit-btn:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(90, 122, 64, 0.2);
}

.submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.toggle-text {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.8rem;
    font-weight: 300;
    font-style: italic;
    color: #3a5528;
}

.toggle-link {
    color: #0f2301;
    font-weight: 400;
    text-decoration: underline;
    text-underline-offset: 2px;
    transition: all 0.2s ease;
    margin-left: 0.25rem;
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    font-family: inherit;
    font-size: inherit;
    font-style: inherit;
}

.toggle-link:hover {
    color: #4d6736;
    opacity: 0.8;
}

/* Step fade transition */
.step-fade-enter-active,
.step-fade-leave-active {
    transition: all 0.25s ease;
}

.step-fade-enter-from {
    opacity: 0;
    transform: translateX(20px);
}

.step-fade-leave-to {
    opacity: 0;
    transform: translateX(-20px);
}

@media (max-width: 500px) {
    .modal-card {
        padding: 2rem 1.5rem;
    }

    .modal-title {
        font-size: 1.5rem;
    }
}
</style>
