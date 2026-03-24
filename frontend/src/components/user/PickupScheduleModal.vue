<script setup>
import { computed } from 'vue'
import { MapPin, Clock, MessageCircle, CalendarCheck } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    orderId: [Number, String]
})

const emit = defineEmits(['close'])

const whatsappUrl = computed(() => {
    const msg = encodeURIComponent(`Salve fam! Gostaria de agendar a retirada do meu pedido #${props.orderId}.`)
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
        <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center px-4 py-6 font-montserrat">

            <!-- Dark overlay -->
            <div class="absolute inset-0 bg-black/50" @click="emit('close')" />

            <!-- Modal content -->
            <transition name="modal">
                <div v-if="isOpen"
                    class="relative z-10 w-full max-w-md bg-[#fffdf2] rounded-2xl shadow-2xl border border-[#eaddcf] overflow-hidden">

                    <!-- Top bar -->
                    <div class="h-1.5 w-full bg-gradient-to-r from-[#3a5528] to-[#0f2301]"></div>

                    <div class="p-6 sm:p-8">

                        <!-- Header -->
                        <div class="flex items-center justify-between mb-6">
                            <h2 class="text-xl font-light italic text-[#0f2301] tracking-wide flex items-center gap-2">
                                <CalendarCheck class="w-5 h-5 text-[#3a5528]" />
                                Agendar Retirada
                            </h2>
                            <button @click="emit('close')"
                                class="text-[#8c9e78] hover:text-[#3a5528] transition-colors p-1.5 hover:bg-[#0f2301]/10 rounded-full">
                                <span class="text-2xl leading-none">&times;</span>
                            </button>
                        </div>

                        <!-- Address card -->
                        <div class="bg-white border border-[#eaddcf] rounded-xl p-4 mb-5 shadow-sm">
                            <div class="flex items-start gap-3">
                                <div
                                    class="w-9 h-9 bg-[#3a5528]/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <MapPin class="w-4 h-4 text-[#3a5528]" />
                                </div>
                                <div>
                                    <p class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-1">Endereço
                                        de Retirada</p>
                                    <p class="text-sm font-medium text-[#0f2301] leading-relaxed">
                                        Av. Eng. Charles Bitran, 435<br>
                                        Jardim Camburi<br>
                                        Vitória - ES, 29092-270
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- Friendly message -->
                        <div class="bg-[#3a5528]/5 border border-[#3a5528]/15 rounded-xl p-4 mb-5">
                            <p class="text-sm text-[#3a5528] font-light leading-relaxed">
                                Para agendar a retirada do seu pedido
                                <span class="font-semibold">#{{ orderId }}</span>
                                no QG da Rocca, entre em contato conosco pelo WhatsApp. Vamos combinar o melhor
                                horário pra você! 🤙
                            </p>
                        </div>

                        <!-- 24h warning -->
                        <div class="flex items-center gap-2 mb-6 px-1">
                            <Clock class="w-3.5 h-3.5 text-[#8c9e78] flex-shrink-0" />
                            <p class="text-xs text-[#8c9e78] font-light italic">
                                Responderemos em até 24 horas.
                            </p>
                        </div>

                        <!-- Divider -->
                        <div class="border-t border-[#eaddcf] mb-5"></div>

                        <!-- WhatsApp button -->
                        <a :href="whatsappUrl" target="_blank" rel="noopener noreferrer"
                            class="flex items-center justify-center gap-2.5 w-full bg-[#25D366] text-white py-3.5 rounded-xl font-medium tracking-wide hover:bg-[#1da851] transition-all shadow-md hover:shadow-lg text-sm">
                            <MessageCircle class="w-5 h-5" />
                            Agendar pelo WhatsApp
                        </a>

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
    z-index: 99;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
}

/* Backdrop transitions */
.modal-backdrop-enter-active,
.modal-backdrop-leave-active {
    transition: opacity 0.3s ease;
}

.modal-backdrop-enter-from,
.modal-backdrop-leave-to {
    opacity: 0;
}

/* Modal panel transitions */
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
