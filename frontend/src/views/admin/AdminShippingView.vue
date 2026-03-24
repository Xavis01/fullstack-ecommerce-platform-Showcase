<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { Search, Loader2, Truck, ExternalLink, Package, MapPin, Clock, ChevronDown, ShoppingCart, CheckCircle2, AlertCircle, Wallet } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'

const toast = useToast()
const orders = ref([])
const loading = ref(false)
const searchTerm = ref('')
const addingToCart = ref({})  // { [orderId]: true/false }

const fetchOrders = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/orders/list')
        // Filter only orders that have shipping (excluding pickup)
        orders.value = response.data.filter(o => o.shipping_service_name && o.shipping_service_name !== 'Retirada')
    } catch (error) {
        console.error('Error fetching orders:', error)
        toast.error('Erro ao carregar pedidos')
    } finally {
        loading.value = false
    }
}

// Fetch full details for each shipping order
const shippingDetails = ref({})
const loadingDetails = ref({})

const fetchOrderDetail = async (orderId) => {
    if (shippingDetails.value[orderId]) return // Already loaded
    loadingDetails.value[orderId] = true
    try {
        const res = await api.get(`/admin/orders/detail/${orderId}`)
        shippingDetails.value[orderId] = res.data
    } catch (err) {
        console.error(err)
    } finally {
        loadingDetails.value[orderId] = false
    }
}

const expandedOrder = ref(null)

const toggleOrder = async (orderId) => {
    if (expandedOrder.value === orderId) {
        expandedOrder.value = null
    } else {
        expandedOrder.value = orderId
        await fetchOrderDetail(orderId)
    }
}

const addToMelhorEnvioCart = async (order) => {
    addingToCart.value[order.order_id] = true
    try {
        const res = await api.post(`/admin/shipping/add-to-cart/${order.order_id}`)
        const data = res.data
        toast.success(`Pedido #${order.order_id} adicionado ao carrinho da Melhor Envio!`)
        // Abre o painel da ME no carrinho
        window.open(data.redirect_url || 'https://melhorenvio.com.br/envios/carrinho', '_blank')
    } catch (err) {
        const msg = err.response?.data?.message || 'Erro ao adicionar ao carrinho da Melhor Envio'
        toast.error(msg)
        console.error(err)
    } finally {
        addingToCart.value[order.order_id] = false
    }
}

const filteredOrders = computed(() => {
    if (!searchTerm.value) return orders.value
    const term = searchTerm.value.toLowerCase()
    return orders.value.filter(o =>
        o.customer_name?.toLowerCase().includes(term) ||
        o.customer_email?.toLowerCase().includes(term) ||
        o.order_id.toString().includes(term)
    )
})

const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0)
}

// Valor da compra = total - frete
const getPurchaseValue = (order) => {
    return (order.total || 0) - (order.shipping_price || 0)
}

const getStatusColor = (paid) => {
    return paid
        ? 'bg-green-100 text-green-800 border-green-200'
        : 'bg-yellow-100 text-yellow-800 border-yellow-200'
}

const openMelhorEnvio = () => {
    window.open('https://melhorenvio.com.br/painel', '_blank')
}

onMounted(() => {
    fetchOrders()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Frete & Envios
            </h1>
            <p class="text-[#8c9e78] font-light">Gerencie os envios dos pedidos pagos</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div class="relative group w-96">
                <input v-model="searchTerm" type="text" placeholder="Pesquisar por cliente ou ID..."
                    class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
                <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
            </div>
            <button @click="openMelhorEnvio"
                class="flex items-center gap-2 bg-[#0f2301] text-[#fffdf2] px-5 py-2.5 rounded-lg font-light text-sm hover:bg-[#3a5528] transition-all shadow-sm">
                <ExternalLink class="w-4 h-4" />
                Abrir Melhor Envio
            </button>
        </div>

        <!-- Content -->
        <div class="px-10">
            <div v-if="loading" class="flex justify-center py-20">
                <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
            </div>

            <div v-else-if="filteredOrders.length === 0" class="text-center py-20">
                <Package class="w-16 h-16 mx-auto text-[#8c9e78]/30 mb-4" />
                <p class="text-[#8c9e78] font-light italic">Nenhum pedido com frete encontrado.</p>
            </div>

            <div v-else class="space-y-4">
                <div v-for="order in filteredOrders" :key="order.order_id"
                    class="bg-white/50 backdrop-blur-sm rounded-xl overflow-hidden shadow-sm border border-[#eaddcf] transition-all">

                    <!-- Order Header Row -->
                    <div class="flex items-center justify-between p-5 hover:bg-[#faf9f0] transition-colors">

                        <!-- Left: toggle + name -->
                        <div @click="toggleOrder(order.order_id)"
                            class="flex items-center gap-6 cursor-pointer flex-1 min-w-0">
                            <ChevronDown :size="18"
                                class="text-[#3a5528] transition-transform duration-300 flex-shrink-0"
                                :class="expandedOrder === order.order_id ? 'rotate-180' : ''" />
                            <div class="flex-shrink-0">
                                <span class="text-[#3a5528] font-semibold">#{{ order.order_id }}</span>
                                <p class="text-xs text-[#8c9e78] font-light">{{ order.date }}</p>
                            </div>
                            <div class="min-w-0">
                                <p class="text-sm font-medium text-[#3a5528] truncate">{{ order.customer_name }}</p>
                                <p class="text-xs text-[#8c9e78] font-light truncate">{{ order.customer_email }}</p>
                            </div>
                        </div>

                        <!-- Right: valores + status + botão -->
                        <div class="flex items-center gap-4 flex-shrink-0">
                            <!-- Valores separados -->
                            <div class="text-right">
                                <div class="flex items-center gap-3 justify-end">
                                    <div class="text-right">
                                        <p class="text-xs text-[#8c9e78] font-light">Compra</p>
                                        <p class="font-medium text-[#3a5528] text-sm">{{
                                            formatCurrency(getPurchaseValue(order)) }}</p>
                                    </div>
                                    <div class="h-8 w-px bg-[#eaddcf]"></div>
                                    <div class="text-right">
                                        <p
                                            class="text-xs text-[#8c9e78] font-light flex items-center gap-1 justify-end">
                                            <Truck class="w-3 h-3" /> Frete
                                        </p>
                                        <p class="font-medium text-[#0f2301] text-sm">{{
                                            formatCurrency(order.shipping_price) }}</p>
                                    </div>
                                </div>
                                <p class="text-xs text-[#8c9e78] font-light mt-0.5">{{ order.shipping_service_name }}
                                </p>
                            </div>

                            <!-- Status badge -->
                            <span
                                :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border shadow-sm', getStatusColor(order.paid)]">
                                {{ order.paid ? 'Pago' : 'Pendente' }}
                            </span>

                            <!-- Botão adicionar ao carrinho ME -->
                            <button v-if="order.paid" @click.stop="addToMelhorEnvioCart(order)"
                                :disabled="addingToCart[order.order_id]"
                                class="flex items-center gap-1.5 bg-[#3a5528] text-[#fffdf2] px-3 py-2 rounded-lg text-xs font-light hover:bg-[#0f2301] transition-all shadow-sm disabled:opacity-50 whitespace-nowrap"
                                title="Adicionar ao carrinho da Melhor Envio e abrir painel">
                                <Loader2 v-if="addingToCart[order.order_id]" class="w-3.5 h-3.5 animate-spin" />
                                <ShoppingCart v-else class="w-3.5 h-3.5" />
                                <span>{{ addingToCart[order.order_id] ? 'Adicionando...' : 'Enviar ME' }}</span>
                            </button>
                        </div>
                    </div>

                    <!-- Expanded Details -->
                    <Transition enter-active-class="transition-all duration-350 ease-out"
                        enter-from-class="max-h-0 opacity-0" enter-to-class="max-h-[600px] opacity-100"
                        leave-active-class="transition-all duration-250 ease-in"
                        leave-from-class="max-h-[600px] opacity-100" leave-to-class="max-h-0 opacity-0">
                        <div v-if="expandedOrder === order.order_id" class="overflow-hidden">
                            <div class="border-t border-[#eaddcf] p-5 bg-[#faf9f0]/50">

                                <div v-if="loadingDetails[order.order_id]" class="flex justify-center py-8">
                                    <Loader2 class="animate-spin text-[#3a5528]" :size="24" />
                                </div>

                                <div v-else-if="shippingDetails[order.order_id]"
                                    class="grid grid-cols-1 md:grid-cols-3 gap-6">

                                    <!-- Resumo Financeiro -->
                                    <div>
                                        <h4 class="text-sm font-medium text-[#3a5528] mb-3 flex items-center gap-2">
                                            <Wallet class="w-4 h-4" /> Resumo Financeiro
                                        </h4>
                                        <div class="space-y-2 text-sm">
                                            <div class="flex justify-between">
                                                <span class="text-[#8c9e78] font-light">Valor da Compra:</span>
                                                <span class="font-medium text-[#3a5528]">{{
                                                    formatCurrency(getPurchaseValue(order)) }}</span>
                                            </div>
                                            <div class="flex justify-between">
                                                <span class="text-[#8c9e78] font-light">Valor do Frete:</span>
                                                <span class="font-medium text-[#0f2301]">{{
                                                    formatCurrency(order.shipping_price) }}</span>
                                            </div>
                                            <div class="flex justify-between border-t border-[#eaddcf] pt-2 mt-1">
                                                <span class="text-[#3a5528] font-medium">Total Pago:</span>
                                                <span class="font-semibold text-[#0f2301]">{{
                                                    formatCurrency(order.total) }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Shipping Info -->
                                    <div>
                                        <h4 class="text-sm font-medium text-[#3a5528] mb-3 flex items-center gap-2">
                                            <Truck class="w-4 h-4" /> Informações do Envio
                                        </h4>
                                        <div class="space-y-2 text-sm">
                                            <div class="flex justify-between">
                                                <span class="text-[#8c9e78] font-light">Serviço:</span>
                                                <span class="font-medium text-[#3a5528]">{{
                                                    shippingDetails[order.order_id].shipping.service_name || 'N/A'
                                                    }}</span>
                                            </div>
                                            <div class="flex justify-between">
                                                <span class="text-[#8c9e78] font-light">Prazo:</span>
                                                <span class="font-medium text-[#3a5528] flex items-center gap-1">
                                                    <Clock class="w-3 h-3" /> {{
                                                        shippingDetails[order.order_id].shipping.delivery_time || '—' }}
                                                    dias úteis
                                                </span>
                                            </div>
                                            <div class="flex justify-between">
                                                <span class="text-[#8c9e78] font-light">ID Serviço:</span>
                                                <span class="font-medium text-[#3a5528]">{{
                                                    shippingDetails[order.order_id].shipping.service_id || '—' }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Address -->
                                    <div>
                                        <h4 class="text-sm font-medium text-[#3a5528] mb-3 flex items-center gap-2">
                                            <MapPin class="w-4 h-4" /> Endereço de Entrega
                                        </h4>
                                        <div class="text-sm space-y-1">
                                            <p class="text-[#3a5528]"
                                                v-if="shippingDetails[order.order_id].shipping.address">
                                                {{ shippingDetails[order.order_id].shipping.address }}, {{
                                                    shippingDetails[order.order_id].shipping.number }}
                                                <span v-if="shippingDetails[order.order_id].shipping.complement"> - {{
                                                    shippingDetails[order.order_id].shipping.complement }}</span>
                                            </p>
                                            <p class="text-[#8c9e78] font-light"
                                                v-if="shippingDetails[order.order_id].shipping.neighborhood">
                                                {{ shippingDetails[order.order_id].shipping.neighborhood }}
                                            </p>
                                            <p class="text-[#8c9e78] font-light"
                                                v-if="shippingDetails[order.order_id].shipping.city">
                                                {{ shippingDetails[order.order_id].shipping.city }} - {{
                                                    shippingDetails[order.order_id].shipping.state }}
                                            </p>
                                            <p class="text-[#8c9e78] font-light"
                                                v-if="shippingDetails[order.order_id].shipping.cep">
                                                CEP: {{ shippingDetails[order.order_id].shipping.cep }}
                                            </p>
                                            <p v-if="!shippingDetails[order.order_id].shipping.address"
                                                class="text-[#8c9e78] font-light italic">
                                                Endereço não informado
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Transition>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
