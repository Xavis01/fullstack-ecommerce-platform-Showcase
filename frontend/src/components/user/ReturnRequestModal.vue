<script setup>
import { computed } from 'vue'
import { ArrowLeftRight, MessageCircle, FileText, Clock } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    orderId: [Number, String]
})

const emit = defineEmits(['close'])

const whatsappUrl = computed(() => {
    const msg = encodeURIComponent(`Olá! Gostaria de solicitar troca ou devolução do meu pedido #${props.orderId}.`)
    return `https://wa.me/5527996657004?text=${msg}`
})
</script>

<template>
    <!-- Blur backdrop -->
    <transition name="modal-backdrop">
        <div v-if="isOpen" class="modal-blur-layer" />
    </transition>

    <!-- Container -->
    <transition name="modal-backdrop">
        <div v-if="isOpen" class="fixed inset-0 z-[110] flex items-center justify-center px-4 py-6 font-montserrat">

            <!-- Dark overlay -->
            <div class="absolute inset-0 bg-black/50" @click="emit('close')" />

            <!-- Modal content -->
            <transition name="modal">
                <div v-if="isOpen"
                    class="relative z-10 w-full max-w-md bg-[#fffdf2] rounded-2xl shadow-2xl border border-[#eaddcf] overflow-hidden">

                    <!-- Top bar -->
                    <div class="h-1 w-full bg-gradient-to-r from-[#3a5528] to-[#0f2301]"></div>

                    <div class="p-6 sm:p-7">

                        <!-- Header -->
                        <div class="flex items-center justify-between mb-5">
                            <h2 class="text-lg font-light italic text-[#0f2301] tracking-wide flex items-center gap-2">
                                <ArrowLeftRight class="w-4.5 h-4.5 text-[#3a5528]" />
                                Troca / Devolução
                            </h2>
                            <button @click="emit('close')"
                                class="text-[#8c9e78] hover:text-[#3a5528] transition-colors p-1.5 hover:bg-[#0f2301]/10 rounded-full">
                                <span class="text-2xl leading-none">&times;</span>
                            </button>
                        </div>

                        <!-- Message -->
                        <div class="bg-[#3a5528]/5 border border-[#3a5528]/15 rounded-xl p-4 mb-5">
                            <p class="text-sm text-[#3a5528] font-light leading-relaxed">
                                Para solicitar a troca ou devolução do pedido
                                <span class="font-semibold">#{{ orderId }}</span>,
                                entre em contato com nossa equipe pelo WhatsApp. Vamos te orientar em todas as etapas!
                                😊
                            </p>
                        </div>

                        <!-- Response time notice -->
                        <div class="flex items-center gap-2 mb-6 px-1">
                            <Clock class="w-3.5 h-3.5 text-[#8c9e78] flex-shrink-0" />
                            <p class="text-xs text-[#8c9e78] font-light italic">
                                Realizamos todo o atendimento pelo WhatsApp. Responderemos em até 24 horas.
                            </p>
                        </div>

                        <!-- Divider -->
                        <div class="border-t border-[#eaddcf] mb-5"></div>

                        <!-- Buttons -->
                        <div class="flex flex-col gap-3">
                            <!-- WhatsApp button -->
                            <a :href="whatsappUrl" target="_blank" rel="noopener noreferrer"
                                class="flex items-center justify-center gap-2.5 w-full bg-[#25D366] text-white py-3.5 rounded-xl font-medium tracking-wide hover:bg-[#1da851] transition-all shadow-md hover:shadow-lg text-sm">
                                <MessageCircle class="w-5 h-5" />
                                Falar com o SAC pelo WhatsApp
                            </a>

                            <!-- Policy link -->
                            <router-link to="/politica-de-troca" target="_blank" @click="emit('close')"
                                class="flex items-center justify-center gap-2 w-full bg-transparent border border-[#eaddcf] text-[#8c9e78] py-3 rounded-xl text-sm font-light italic tracking-wide hover:border-[#3a5528] hover:text-[#3a5528] transition-all">
                                <FileText class="w-4 h-4" />
                                Ver Política de Troca e Devolução
                            </router-link>
                        </div>

                    </div>
                </div>
            </transition>
        </div>
    </transition>
</template>

<style scoped>
.modal-blur-layer {
    position: fixed;
    inset: 0;
    z-index: 109;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
}

.modal-backdrop-enter-active,
.modal-backdrop-leave-active {
    transition: opacity 0.3s ease;
}

.modal-backdrop-enter-from,
.modal-backdrop-leave-to {
    opacity: 0;
}

.modal-enter-active,
.modal-leave-active {
    transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
}
</style>
