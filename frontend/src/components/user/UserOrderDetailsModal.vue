<script setup>
import { defineProps, defineEmits, ref } from 'vue'
import { PackageSearch, QrCode, CreditCard, Loader2, XCircle, Truck, MapPin, User2, Home, ArrowLeftRight } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/api'
import ConfirmCancelOrderModal from './ConfirmCancelOrderModal.vue'
import ReturnRequestModal from './ReturnRequestModal.vue'

const props = defineProps({
    isOpen: Boolean,
    order: Object
})

const emit = defineEmits(['close', 'cancelled'])
const router = useRouter()
const toast = useToast()

const loadingPix = ref(false)
const cancelling = ref(false)
const showCancelConfirmModal = ref(false)
const showReturnModal = ref(false)

const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

const formatPaymentMethod = (method) => {
    const map = { 'pix': 'PIX', 'credit_card': 'Cartão de Crédito', 'dinheiro': 'Dinheiro' }
    return map[method] || method || 'N/A'
}

const formatPaymentStatus = (paid) => paid ? 'Aprovado' : 'Aguardando Pagamento'

const formatCPF = (cpf) => {
    if (!cpf) return null
    const d = cpf.replace(/\D/g, '')
    return d.length === 11 ? d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4') : cpf
}

const formatPhone = (phone) => {
    if (!phone) return null
    const d = phone.replace(/\D/g, '')
    if (d.length === 11) return d.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
    if (d.length === 10) return d.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3')
    return phone
}

const recoverPix = async () => {
    loadingPix.value = true
    try {
        const response = await api.get(`/user/orders/${props.order.order_id}/pix`)
        const pixData = {
            point_of_interaction: {
                transaction_data: {
                    qr_code: response.data.qr_code,
                    qr_code_base64: response.data.qr_code_base64
                }
            }
        }
        sessionStorage.setItem('pendingPix', JSON.stringify(pixData))
        emit('close')
        router.push('/checkout/pix')
    } catch (error) {
        console.error(error)
        toast.error('Erro ao recuperar o código PIX. Tente novamente mais tarde.')
    } finally {
        loadingPix.value = false
    }
}

const cancelOrder = () => { showCancelConfirmModal.value = true }

const executeCancel = async () => {
    cancelling.value = true
    try {
        const response = await api.delete(`/user/orders/${props.order.order_id}/cancel`)
        toast.success(response.data.message || 'Pedido cancelado com sucesso!')
        showCancelConfirmModal.value = false
        emit('cancelled')
        emit('close')
    } catch (error) {
        console.error(error)
        toast.error(error.response?.data?.error || 'Erro ao cancelar o pedido. Tente novamente.')
        showCancelConfirmModal.value = false
    } finally {
        cancelling.value = false
    }
}
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
                <div v-if="isOpen && order"
                    class="relative z-10 w-full max-w-4xl bg-[#fffdf2] rounded-2xl shadow-2xl border border-[#eaddcf] flex flex-col max-h-full overflow-hidden">

                    <!-- Header (fixed) -->
                    <div
                        class="shrink-0 px-6 py-5 border-b border-[#eaddcf] flex justify-between items-center bg-white/50">
                        <div>
                            <h2
                                class="text-xl font-['Montserrat'] italic font-medium text-[#3a5528] flex items-center gap-2">
                                <PackageSearch :size="20" /> Detalhes do Pedido
                            </h2>
                            <p v-if="order.date" class="text-sm text-[#8c9e78] font-light mt-0.5">{{ order.date }}</p>
                        </div>
                        <button @click="$emit('close')"
                            class="text-[#8c9e78] hover:text-[#3a5528] transition-colors p-2 hover:bg-[#0f2301]/10 rounded-full">
                            <span class="text-2xl leading-none">&times;</span>
                        </button>
                    </div>

                    <!-- Body (scrollable) -->
                    <div class="flex-1 overflow-y-auto custom-scrollbar">
                        <div class="p-6 flex flex-col md:flex-row gap-6">

                            <!-- ─── LEFT COLUMN ─── -->
                            <div class="flex-1 flex flex-col gap-5">

                                <!-- Products -->
                                <div>
                                    <h3 class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-3">
                                        Itens Comprados
                                    </h3>
                                    <div class="space-y-2.5">
                                        <div v-for="(item, idx) in order.items" :key="idx"
                                            class="flex items-center gap-3 bg-white border border-[#eaddcf] p-3.5 rounded-xl">
                                            <div
                                                class="w-14 h-14 bg-[#faf9f0] rounded-lg border border-[#eaddcf]/50 overflow-hidden flex-shrink-0 flex items-center justify-center">
                                                <img v-if="item.image_url" :src="item.image_url"
                                                    class="object-cover w-full h-full opacity-80" />
                                                <PackageSearch v-else class="w-5 h-5 text-[#d4c4b7]" />
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

                                <!-- Shipping + Address side-by-side -->
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                                    <!-- Envio -->
                                    <div class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm">
                                        <h3
                                            class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2.5 flex items-center gap-1.5">
                                            <Truck :size="11" /> Envio
                                        </h3>
                                        <div v-if="!order.shipping?.service_name">
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
                                                        v-if="order.shipping.service_name?.toUpperCase().includes('RETIRADA')"
                                                        :size="11" />
                                                    <Truck v-else :size="11" />
                                                    {{ order.shipping.service_name }}
                                                </span>
                                                <span v-if="order.shipping.price > 0"
                                                    class="text-[#3a5528] font-semibold text-sm whitespace-nowrap">
                                                    {{ formatCurrency(order.shipping.price) }}
                                                </span>
                                            </div>
                                            <p v-if="order.shipping.delivery_time"
                                                class="text-[#8c9e78] text-xs font-light">
                                                Prazo: {{ order.shipping.delivery_time }} dia{{
                                                    order.shipping.delivery_time !== 1 ? 's' : '' }} útei{{
                                                    order.shipping.delivery_time !== 1 ? 's' : 'l' }}
                                            </p>
                                        </div>
                                    </div>

                                    <!-- Endereço -->
                                    <div v-if="order.shipping?.address || order.shipping?.cep"
                                        class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm">
                                        <h3
                                            class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2.5 flex items-center gap-1.5">
                                            <MapPin :size="11" /> Endereço
                                        </h3>
                                        <div class="space-y-0.5 text-[#0f2301]">
                                            <p v-if="order.shipping.address" class="font-medium text-sm">
                                                {{ order.shipping.address }}
                                                <span v-if="order.shipping.number">, {{ order.shipping.number }}</span>
                                                <span v-if="order.shipping.complement"> — {{ order.shipping.complement
                                                }}</span>
                                            </p>
                                            <p v-if="order.shipping.neighborhood" class="text-[#8c9e78] text-xs">{{
                                                order.shipping.neighborhood }}</p>
                                            <p v-if="order.shipping.city" class="text-[#8c9e78] text-xs">
                                                {{ order.shipping.city }}<span v-if="order.shipping.state"> / {{
                                                    order.shipping.state }}</span>
                                            </p>
                                            <p v-if="order.shipping.cep" class="text-[#8c9e78] text-xs">CEP: {{
                                                order.shipping.cep }}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- ─── RIGHT COLUMN ─── -->
                            <div class="w-full md:w-72 flex flex-col gap-4 shrink-0">

                                <!-- Dados do cliente (CPF / Telefone) -->
                                <div v-if="order.customer_cpf || order.customer_phone"
                                    class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm">
                                    <h3
                                        class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2.5 flex items-center gap-1.5">
                                        <User2 :size="11" /> Seus Dados
                                    </h3>
                                    <div class="grid grid-cols-2 gap-2">
                                        <div v-if="order.customer_cpf">
                                            <p class="text-[10px] font-bold uppercase tracking-wider text-[#b0a898]">CPF
                                            </p>
                                            <p class="text-[#0f2301] text-xs mt-0.5">{{ formatCPF(order.customer_cpf) }}
                                            </p>
                                        </div>
                                        <div v-if="order.customer_phone">
                                            <p class="text-[10px] font-bold uppercase tracking-wider text-[#b0a898]">
                                                Telefone</p>
                                            <p class="text-[#0f2301] text-xs mt-0.5">{{
                                                formatPhone(order.customer_phone) }}</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Status + Pagamento + Total -->
                                <div
                                    class="bg-white p-4 rounded-xl border border-[#eaddcf] shadow-sm flex flex-col gap-3">
                                    <div>
                                        <h3 class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-2">
                                            Status</h3>
                                        <p class="text-[#3a5528] font-medium text-sm mb-2">{{
                                            formatPaymentStatus(order.is_paid) }}</p>
                                        <div
                                            class="flex items-center gap-1.5 bg-[#0f2301]/8 w-fit px-2 py-1 rounded text-[#3a5528]">
                                            <QrCode v-if="order.payment_method === 'pix'" class="w-3.5 h-3.5" />
                                            <CreditCard v-else class="w-3.5 h-3.5" />
                                            <span class="text-[10px] font-bold uppercase tracking-wider">{{
                                                formatPaymentMethod(order.payment_method) }}</span>
                                        </div>
                                    </div>

                                    <div class="pt-3 border-t border-[#eaddcf]">
                                        <h3 class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-1.5">
                                            Total</h3>
                                        <div class="flex flex-col gap-1">
                                            <div class="flex justify-between text-[#8c9e78] text-xs">
                                                <span class="italic">Subtotal</span>
                                                <span>{{ formatCurrency(order.total + order.discount_amount) }}</span>
                                            </div>
                                            <div v-if="order.coupon_code"
                                                class="flex justify-between text-[#8c9e78] text-xs">
                                                <span class="italic">Cupom ({{ order.coupon_code }})</span>
                                                <span>- {{ formatCurrency(order.discount_amount) }}</span>
                                            </div>
                                            <div v-if="order.shipping?.price > 0"
                                                class="flex justify-between text-[#8c9e78] text-xs">
                                                <span class="italic">Frete</span>
                                                <span>{{ formatCurrency(order.shipping.price) }}</span>
                                            </div>
                                        </div>
                                        <p
                                            class="text-[#3a5528] font-semibold text-xl mt-2 pt-2 border-t border-[#eaddcf]">
                                            {{ formatCurrency(order.total) }}
                                        </p>
                                    </div>
                                </div>

                                <!-- Ações pendentes -->
                                <div v-if="order.payment_status === 'pending'"
                                    class="bg-[#faf9f0] border border-[#eaddcf] p-4 rounded-xl flex flex-col gap-3">
                                    <p class="text-[#8c9e78] text-xs font-light text-center">Seu pedido ainda não foi
                                        pago.</p>
                                    <button v-if="order.payment_method === 'pix'" @click="recoverPix"
                                        :disabled="loadingPix || cancelling"
                                        class="w-full flex items-center justify-center gap-2 bg-[#3a5528] text-[#fffdf2] py-2.5 rounded-xl text-sm font-light italic tracking-wide hover:bg-[#0f2301] transition-colors disabled:opacity-50">
                                        <Loader2 v-if="loadingPix" class="w-4 h-4 animate-spin" />
                                        <QrCode v-else class="w-4 h-4" />
                                        {{ loadingPix ? 'Gerando...' : 'Pagar via PIX' }}
                                    </button>
                                    <button @click="cancelOrder" :disabled="loadingPix || cancelling"
                                        class="w-full flex items-center justify-center gap-2 bg-transparent border border-red-200 text-red-600 py-2.5 rounded-xl text-sm font-light italic tracking-wide hover:bg-red-50 transition-colors disabled:opacity-50">
                                        <Loader2 v-if="cancelling" class="w-4 h-4 animate-spin" />
                                        <XCircle v-else class="w-4 h-4" />
                                        {{ cancelling ? 'Cancelando...' : 'Cancelar Pedido' }}
                                    </button>
                                </div>

                                <!-- Troca / Devolução (somente pedidos pagos) -->
                                <div v-if="order.is_paid" class="pt-1">
                                    <button @click="showReturnModal = true"
                                        class="w-full flex items-center justify-center gap-1.5 text-[#8c9e78] hover:text-[#3a5528] text-xs font-light italic py-2 rounded-lg hover:bg-[#0f2301]/5 transition-all">
                                        <ArrowLeftRight class="w-3.5 h-3.5" />
                                        Troca / Devolução
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
    </transition>

    <ConfirmCancelOrderModal :isOpen="showCancelConfirmModal" :order="order" :loading="cancelling"
        @close="showCancelConfirmModal = false" @cancel="executeCancel" />

    <ReturnRequestModal :isOpen="showReturnModal" :orderId="order?.order_id" @close="showReturnModal = false" />
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
