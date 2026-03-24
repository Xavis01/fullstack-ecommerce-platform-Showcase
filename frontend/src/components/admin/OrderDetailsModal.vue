<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { X, Loader2, PackageOpen, QrCode, CreditCard, MapPin, Truck, User2, Home, CheckCircle2 } from 'lucide-vue-next'
import api from '@/api'
import { useToast } from 'vue-toastification'

const props = defineProps({
    isOpen: Boolean,
    orderId: [Number, String, null]
})

const emit = defineEmits(['close'])
const toast = useToast()

const loading = ref(false)
const orderData = ref(null)

const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0)
}

const formatPaymentMethod = (method) => {
    if (!method) return 'N/A'
    const methods = {
        'pix': 'PIX',
        'credit_card': 'Cartão de Crédito',
        'ticket': 'Boleto'
    }
    return methods[method] || method
}

const formatCPF = (cpf) => {
    if (!cpf) return 'N/A'
    const d = cpf.replace(/\D/g, '')
    return d.length === 11 ? d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4') : cpf
}

const formatPhone = (phone) => {
    if (!phone) return 'N/A'
    const d = phone.replace(/\D/g, '')
    if (d.length === 11) return d.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
    if (d.length === 10) return d.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3')
    return phone
}

const fetchOrderDetails = async () => {
    if (!props.orderId) return
    loading.value = true
    orderData.value = null
    try {
        const response = await api.get(`/admin/orders/detail/${props.orderId}`)
        orderData.value = response.data
    } catch (error) {
        console.error('Error fetching order details:', error)
        toast.error('Erro ao carregar detalhes do pedido.')
        emit('close')
    } finally {
        loading.value = false
    }
}

watch(() => props.isOpen, (newVal) => {
    if (newVal && props.orderId) fetchOrderDetails()
    else orderData.value = null
})
</script>

<template>
    <!-- Blur backdrop -->
    <transition name="modal-backdrop">
        <div v-if="isOpen" class="modal-blur-layer" />
    </transition>

    <!-- Container -->
    <transition name="modal-backdrop">
        <div v-if="isOpen"
            class="fixed inset-0 z-[100] flex items-center justify-center pt-28 pb-6 px-3 md:px-4 font-montserrat">

            <!-- Dark overlay -->
            <div class="absolute inset-0 bg-black/50" @click="$emit('close')" />

            <!-- Modal content -->
            <transition name="modal">
                <div v-if="isOpen"
                    class="relative z-10 w-full max-w-4xl bg-[#fffdf2] rounded-2xl shadow-2xl border border-[#eaddcf] flex flex-col max-h-full overflow-hidden">

                    <!-- Header (fixed) -->
                    <div
                        class="shrink-0 px-6 py-5 border-b border-[#eaddcf] flex justify-between items-start bg-white/50">
                        <div>
                            <h2
                                class="text-xl font-['Montserrat'] italic font-medium text-[#3a5528] flex items-center gap-2">
                                <PackageOpen :size="20" />
                                Detalhes do Pedido
                                <span v-if="orderId" class="text-[#8c9e78]">#{{ orderId }}</span>
                            </h2>
                            <p v-if="orderData" class="text-sm text-[#8c9e78] font-light mt-0.5">{{ orderData.date }}
                            </p>
                        </div>
                        <button @click="$emit('close')"
                            class="text-[#8c9e78] hover:text-[#3a5528] transition-colors p-2 hover:bg-[#0f2301]/10 rounded-full mt-0.5">
                            <X :size="20" />
                        </button>
                    </div>

                    <!-- Body (scrollable) -->
                    <div class="flex-1 overflow-y-auto custom-scrollbar">

                        <!-- Loading -->
                        <div v-if="loading" class="flex justify-center items-center py-20">
                            <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
                        </div>

                        <div v-else-if="orderData" class="p-6 flex flex-col md:flex-row gap-6">

                            <!-- ─── LEFT COLUMN ─── -->
                            <div class="flex-1 flex flex-col gap-5">

                                <!-- Products -->
                                <div>
                                    <h3 class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-3">
                                        Itens Comprados ({{ orderData.items?.length || 0 }})
                                    </h3>
                                    <div class="space-y-2.5">
                                        <div v-for="(item, idx) in orderData.items" :key="idx"
                                            class="flex items-center gap-3 bg-white border border-[#eaddcf] p-3.5 rounded-xl">
                                            <div
                                                class="w-14 h-14 bg-[#faf9f0] rounded-lg border border-[#eaddcf]/50 overflow-hidden flex-shrink-0 flex items-center justify-center">
                                                <img v-if="item.image_url" :src="item.image_url"
                                                    class="object-cover w-full h-full opacity-80" />
                                                <PackageOpen v-else class="w-5 h-5 text-[#d4c4b7]" />
                                            </div>
                                            <div class="flex-1 min-w-0">
                                                <p class="text-[#3a5528] font-medium text-sm truncate">{{
                                                    item.product_name }}</p>
                                                <p class="text-[#8c9e78] text-xs font-light">Tamanho: {{ item.variant }}
                                                </p>
                                            </div>
                                            <div class="text-right flex-shrink-0">
                                                <p class="text-[#3a5528] text-sm">{{ item.quantity }}x</p>
                                                <p class="text-[#0f2301] font-medium text-sm">{{
                                                    formatCurrency(item.subtotal) }}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Shipping + Address side-by-side on left -->
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                                    <!-- Envio -->
                                    <div class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm">
                                        <h3
                                            class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2.5 flex items-center gap-1.5">
                                            <Truck :size="11" /> Envio
                                        </h3>
                                        <div v-if="!orderData.shipping?.service_name">
                                            <span
                                                class="inline-flex items-center gap-1.5 text-xs font-medium bg-[#3a5528]/10 text-[#3a5528] px-2.5 py-1 rounded-full">
                                                <Home :size="12" /> Retirada na loja
                                            </span>
                                        </div>
                                        <div v-else class="flex flex-col gap-1.5">
                                            <div class="flex items-center justify-between gap-2">
                                                <span
                                                    class="inline-flex items-center gap-1 text-xs font-bold uppercase tracking-wider bg-[#0f2301]/10 text-[#3a5528] px-2.5 py-1 rounded-full">
                                                    <Home
                                                        v-if="orderData.shipping.service_name?.toUpperCase().includes('RETIRADA')"
                                                        :size="11" />
                                                    <Truck v-else :size="11" />
                                                    {{ orderData.shipping.service_name }}
                                                </span>
                                                <span v-if="orderData.shipping.price > 0"
                                                    class="text-[#3a5528] font-semibold text-sm whitespace-nowrap">
                                                    {{ formatCurrency(orderData.shipping.price) }}
                                                </span>
                                            </div>
                                            <p v-if="orderData.shipping.delivery_time"
                                                class="text-[#8c9e78] text-xs font-light">
                                                Prazo: {{ orderData.shipping.delivery_time }} dia{{
                                                    orderData.shipping.delivery_time !== 1 ? 's' : '' }} útei{{
                                                    orderData.shipping.delivery_time !== 1 ? 's' : 'l' }}
                                            </p>
                                        </div>
                                    </div>

                                    <!-- Endereço -->
                                    <div v-if="orderData.shipping?.address || orderData.shipping?.cep"
                                        class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm">
                                        <h3
                                            class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2.5 flex items-center gap-1.5">
                                            <MapPin :size="11" /> Endereço
                                        </h3>
                                        <div class="space-y-0.5 text-[#0f2301]">
                                            <p v-if="orderData.shipping.address" class="font-medium text-sm">
                                                {{ orderData.shipping.address }}
                                                <span v-if="orderData.shipping.number">, {{ orderData.shipping.number
                                                    }}</span>
                                                <span v-if="orderData.shipping.complement"> — {{
                                                    orderData.shipping.complement }}</span>
                                            </p>
                                            <p v-if="orderData.shipping.neighborhood" class="text-[#8c9e78] text-xs">{{
                                                orderData.shipping.neighborhood }}</p>
                                            <p v-if="orderData.shipping.city" class="text-[#8c9e78] text-xs">
                                                {{ orderData.shipping.city }}<span v-if="orderData.shipping.state"> / {{
                                                    orderData.shipping.state }}</span>
                                            </p>
                                            <p v-if="orderData.shipping.cep" class="text-[#8c9e78] text-xs">CEP: {{
                                                orderData.shipping.cep }}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- ─── RIGHT COLUMN ─── -->
                            <div class="w-full md:w-72 flex flex-col gap-4 shrink-0">

                                <!-- Cliente -->
                                <div class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm">
                                    <h3
                                        class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2.5 flex items-center gap-1.5">
                                        <User2 :size="11" /> Cliente
                                    </h3>
                                    <p class="text-[#3a5528] font-medium text-sm">{{ orderData.customer?.name }}</p>
                                    <p class="text-[#0f2301] text-xs font-light truncate mt-0.5">{{
                                        orderData.customer?.email }}</p>
                                    <div class="mt-2.5 pt-2.5 border-t border-[#eaddcf] grid grid-cols-2 gap-2">
                                        <div>
                                            <p class="text-[10px] font-bold uppercase tracking-wider text-[#b0a898]">CPF
                                            </p>
                                            <p class="text-[#0f2301] text-xs mt-0.5">{{
                                                formatCPF(orderData.customer?.cpf) }}</p>
                                        </div>
                                        <div>
                                            <p class="text-[10px] font-bold uppercase tracking-wider text-[#b0a898]">
                                                Telefone</p>
                                            <p class="text-[#0f2301] text-xs mt-0.5">{{
                                                formatPhone(orderData.customer?.phone) }}</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pagamento + Total -->
                                <div
                                    class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm flex flex-col gap-3">
                                    <div>
                                        <h3 class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2">
                                            Pagamento</h3>
                                        <div class="flex flex-wrap gap-2 mb-2">
                                            <span v-if="orderData.is_paid"
                                                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                                                ✓ Pago
                                            </span>
                                            <span v-else
                                                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-200">
                                                Pendente
                                            </span>
                                        </div>
                                        <div
                                            class="flex items-center gap-1.5 bg-[#0f2301]/8 w-fit px-2 py-1 rounded text-[#3a5528]">
                                            <QrCode v-if="orderData.payment_method === 'pix'" class="w-3.5 h-3.5" />
                                            <CreditCard v-else class="w-3.5 h-3.5" />
                                            <span class="text-[10px] font-bold uppercase tracking-wider">{{
                                                formatPaymentMethod(orderData.payment_method) }}</span>
                                        </div>
                                    </div>

                                    <div class="pt-3 border-t border-[#eaddcf]">
                                        <h3 class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-1.5">
                                            Total</h3>
                                        <div class="flex flex-col gap-1">
                                            <div class="flex justify-between text-[#8c9e78] text-xs">
                                                <span class="italic">Subtotal</span>
                                                <span>{{ formatCurrency(orderData.total + orderData.discount_amount)
                                                    }}</span>
                                            </div>
                                            <div v-if="orderData.coupon_code"
                                                class="flex justify-between text-[#8c9e78] text-xs">
                                                <span class="italic">Cupom ({{ orderData.coupon_code }})</span>
                                                <span>- {{ formatCurrency(orderData.discount_amount) }}</span>
                                            </div>
                                            <div v-if="orderData.shipping?.price > 0"
                                                class="flex justify-between text-[#8c9e78] text-xs">
                                                <span class="italic">Frete</span>
                                                <span>{{ formatCurrency(orderData.shipping.price) }}</span>
                                            </div>
                                        </div>
                                        <p
                                            class="text-[#3a5528] font-semibold text-xl mt-2 pt-2 border-t border-[#eaddcf]">
                                            {{ formatCurrency(orderData.total) }}
                                        </p>
                                    </div>
                                </div>
                            </div>
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

.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #eaddcf;
    border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #d4c4b7;
}
</style>
