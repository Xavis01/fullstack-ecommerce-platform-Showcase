<template>
    <div class="min-h-[80vh] bg-[#fffdf2] font-montserrat flex items-start justify-center px-4 pt-24 md:pt-32 pb-12">
        <div class="max-w-md w-full">

            <!-- Card principal -->
            <div
                class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-[#eaddcf] overflow-hidden relative">

                <!-- Barra top -->
                <div class="h-1.5 w-full bg-gradient-to-r from-[#3a5528] to-[#0f2301]"></div>

                <div class="p-8 text-center">

                    <!-- Ícone animado -->
                    <div class="relative mx-auto w-20 h-20 mb-6">
                        <div class="absolute inset-0 bg-[#3a5528]/10 rounded-full animate-ping"></div>
                        <div
                            class="relative w-20 h-20 bg-gradient-to-br from-[#3a5528] to-[#0f2301] rounded-full flex items-center justify-center shadow-lg">
                            <CheckCircle2 class="w-10 h-10 text-[#fffdf2]" />
                        </div>
                    </div>

                    <!-- Título -->
                    <h1 class="text-2xl font-light text-[#0f2301] italic mb-2 tracking-wide">
                        Pagamento Aprovado!
                    </h1>
                    <p class="text-[#8c9e78] font-light text-sm leading-relaxed">
                        Seu pedido foi confirmado e já estamos<br>preparando para
                        <span v-if="isPickupOrder">a retirada.</span>
                        <span v-else>envio.</span>
                    </p>

                    <!-- Divider -->
                    <div class="my-6 border-t border-[#eaddcf]"></div>

                    <!-- Botões -->
                    <div class="space-y-3">
                        <router-link to="/produtos"
                            class="flex items-center justify-center gap-2 w-full bg-[#0f2301] text-[#fffdf2] py-3 rounded-xl font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                            <ShoppingBag class="w-4 h-4" />
                            Continuar Comprando
                        </router-link>

                        <!-- Botão Agendar Retirada: só aparece se foi Retirada -->
                        <button v-if="isPickupOrder" @click="showPickupModal = true"
                            class="flex items-center justify-center gap-2 w-full bg-[#3a5528] text-[#fffdf2] py-3 rounded-xl font-light italic tracking-wide hover:bg-[#0f2301] transition-all shadow-sm cursor-pointer">
                            <CalendarCheck class="w-4 h-4" />
                            Agendar Retirada
                        </button>

                        <router-link to="/meus-pedidos"
                            class="flex items-center justify-center gap-2 w-full bg-transparent border border-[#3a5528] text-[#3a5528] py-3 rounded-xl font-light italic tracking-wide hover:bg-[#3a5528]/10 transition-all">
                            <Package class="w-4 h-4" />
                            Meus Pedidos
                        </router-link>
                        <router-link to="/"
                            class="flex items-center justify-center gap-2 w-full bg-transparent text-[#8c9e78] py-2.5 rounded-xl font-light text-sm hover:text-[#3a5528] transition-all">
                            <Home class="w-4 h-4" />
                            Página Principal
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Pickup Schedule Modal -->
    <PickupScheduleModal :isOpen="showPickupModal" :orderId="orderId" @close="showPickupModal = false" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { CheckCircle2, ShoppingBag, Package, Home, CalendarCheck } from 'lucide-vue-next'
import PickupScheduleModal from '@/components/user/PickupScheduleModal.vue'

const isPickupOrder = ref(false)
const showPickupModal = ref(false)
const orderId = ref(null)

onMounted(() => {
    isPickupOrder.value = sessionStorage.getItem('is_pickup') === '1'
    orderId.value = sessionStorage.getItem('lastOrderId')
    sessionStorage.removeItem('is_pickup')
    sessionStorage.removeItem('lastOrderId')
})
</script>
