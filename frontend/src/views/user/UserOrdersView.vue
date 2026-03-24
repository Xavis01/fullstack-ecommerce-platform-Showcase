<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import { Loader2, PackageSearch, CalendarCheck } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import UserOrderDetailsModal from '@/components/user/UserOrderDetailsModal.vue'
import PickupScheduleModal from '@/components/user/PickupScheduleModal.vue'

const toast = useToast()
const userStore = useUserStore()
const router = useRouter()
const orders = ref([])
const loading = ref(true)

const showDetailsModal = ref(false)
const selectedOrder = ref(null)

const showPickupModal = ref(false)
const pickupOrderId = ref(null)

const openPickupModal = (orderId) => {
    pickupOrderId.value = orderId
    showPickupModal.value = true
}

const fetchOrders = async () => {
    try {
        const response = await api.get('/user/orders')
        orders.value = response.data
    } catch (error) {
        console.error('Error fetching orders:', error)
        toast.error('Erro ao carregar seus pedidos')
    } finally {
        loading.value = false
    }
}

const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

const openDetails = (order) => {
    selectedOrder.value = order.order_id
    showDetailsModal.value = true
}

onMounted(() => {
    if (!localStorage.getItem('token')) {
        router.push('/')
        return
    }
    fetchOrders()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pt-4 pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-8 max-w-5xl mx-auto">
            <h1
                class="text-3xl font-['Montserrat'] font-light text-[#3a5528] italic mb-2 tracking-wide flex items-center gap-3">
                <PackageSearch :size="32" class="text-[#0f2301]" />
                Meus Pedidos
            </h1>
            <p class="text-[#8c9e78] font-light">Acompanhe o status e o histórico das suas compras.</p>
        </div>

        <!-- Content -->
        <div class="px-4 sm:px-10 max-w-5xl mx-auto">
            <div v-if="loading" class="flex justify-center py-20">
                <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
            </div>

            <!-- Empty State -->
            <div v-else-if="orders.length === 0"
                class="text-center py-20 bg-white/50 border border-[#eaddcf] rounded-2xl shadow-sm backdrop-blur-sm">
                <PackageSearch class="w-16 h-16 text-[#eaddcf] mx-auto mb-4" />
                <h3 class="text-xl font-['Montserrat'] italic text-[#3a5528] mb-2">Você ainda não tem pedidos</h3>
                <p class="text-[#8c9e78] font-light mb-6">Que tal dar uma olhada nas nossas novidades?</p>
                <router-link to="/produtos"
                    class="inline-block bg-[#0f2301] text-[#fffdf2] px-8 py-3 rounded-xl font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                    Ver Produtos
                </router-link>
            </div>

            <!-- Orders List -->
            <div v-else class="space-y-6">
                <!-- Order Card -->
                <div v-for="order in orders" :key="order.order_id"
                    class="bg-white/70 backdrop-blur-sm border border-[#eaddcf] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                    <div class="absolute top-0 left-0 w-2 h-full bg-[#0f2301]"></div>

                    <div class="flex flex-col md:flex-row justify-between md:items-center gap-6">

                        <!-- Order Info -->
                        <div class="flex-1 pl-4">
                            <div class="flex items-center gap-3 mb-2">
                                <span class="text-lg font-['Montserrat'] italic font-medium text-[#3a5528]">
                                    Pedido #{{ order.order_id }}
                                </span>
                                <span v-if="order.is_paid"
                                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                                    Pagamento Aprovado
                                </span>
                                <span v-else
                                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-200">
                                    Aguardando Pagamento
                                </span>
                            </div>
                            <p class="text-[#8c9e78] text-sm font-light mb-3">Realizado em {{ order.date }}</p>

                            <div class="flex flex-wrap gap-2">
                                <div v-for="(item, idx) in order.items.slice(0, 3)" :key="idx"
                                    class="bg-[#fffdf2] border border-[#eaddcf] px-3 py-1.5 rounded-lg text-xs text-[#3a5528] font-medium flex items-center gap-2">
                                    <span class="text-[#8c9e78]">{{ item.quantity }}x</span> {{ item.product_name }}
                                </div>
                                <div v-if="order.items.length > 3"
                                    class="bg-[#fffdf2] border border-[#eaddcf] px-3 py-1.5 rounded-lg text-xs text-[#8c9e78] font-light">
                                    + {{ order.items.length - 3 }} itens
                                </div>
                            </div>
                        </div>

                        <!-- Action & Price -->
                        <div
                            class="flex md:flex-col items-center justify-between md:items-end gap-4 border-t md:border-t-0 md:border-l border-[#eaddcf] pt-4 md:pt-0 md:pl-6 pl-4">
                            <div class="text-left md:text-right">
                                <p class="text-xs font-bold uppercase tracking-wider text-[#8c9e78] mb-1">Total</p>
                                <p class="text-xl font-medium text-[#3a5528]">{{ formatCurrency(order.total) }}</p>
                            </div>
                            <div class="flex flex-col gap-2">
                                <button v-if="order.shipping?.service_name?.toUpperCase().includes('RETIRADA')"
                                    @click="openPickupModal(order.order_id)"
                                    class="flex items-center justify-center gap-1.5 bg-[#3a5528] text-[#fffdf2] px-4 py-2 rounded-xl text-sm font-light italic tracking-wide hover:bg-[#0f2301] transition-all shadow-sm cursor-pointer">
                                    <CalendarCheck class="w-3.5 h-3.5" />
                                    Agendar Retirada
                                </button>
                                <button @click="openDetails(order)"
                                    class="bg-transparent border border-[#0f2301] text-[#0f2301] px-5 py-2 rounded-xl text-sm font-light italic tracking-wide hover:bg-black/5 transition-all">
                                    Ver Detalhes
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>

        </div>

        <!-- Separated User Order Details Modal -->
        <UserOrderDetailsModal :isOpen="showDetailsModal" :order="orders.find(o => o.order_id === selectedOrder)"
            @close="showDetailsModal = false" @cancelled="fetchOrders" />

        <!-- Pickup Schedule Modal -->
        <PickupScheduleModal :isOpen="showPickupModal" :orderId="pickupOrderId" @close="showPickupModal = false" />

    </div>
</template>
