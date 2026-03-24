<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { Search, Loader2, FileText, Trash2 } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import OrderDetailsModal from '@/components/admin/OrderDetailsModal.vue'
import ConfirmHardDeleteModal from '@/components/admin/Products/trash/ConfirmHardDeleteModal.vue'

const toast = useToast()
const orders = ref([])
const loading = ref(false)
const searchTerm = ref('')

const showDetailsModal = ref(false)
const showDeleteModal = ref(false)
const selectedOrder = ref(null)
const orderToDelete = ref(null)

const fetchOrders = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/orders/list')
        orders.value = response.data
    } catch (error) {
        console.error('Error fetching orders:', error)
        toast.error('Erro ao carregar pedidos')
    } finally {
        loading.value = false
    }
}

const filteredOrders = computed(() => {
    if (!searchTerm.value) return orders.value
    const term = searchTerm.value.toLowerCase()
    return orders.value.filter(o =>
        o.customer_name?.toLowerCase().includes(term) ||
        o.customer_email?.toLowerCase().includes(term) ||
        o.order_id.toString().toLowerCase().includes(term)
    )
})

const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

const openDetails = (order) => {
    selectedOrder.value = order.order_id
    showDetailsModal.value = true
}

const openDelete = (order) => {
    if (order.paid) {
        toast.warning('Não é possível excluir pedidos já pagos.')
        return
    }
    orderToDelete.value = order
    showDeleteModal.value = true
}

const handleDelete = async () => {
    if (!orderToDelete.value) return
    try {
        await api.delete(`/admin/orders/delete/${orderToDelete.value.order_id}`)
        toast.success(`Pedido #${orderToDelete.value.order_id} excluído com sucesso!`)
        await fetchOrders()
    } catch (error) {
        console.error('Error deleting order:', error)
        toast.error(error.response?.data?.error || 'Erro ao excluir pedido')
    } finally {
        showDeleteModal.value = false
        orderToDelete.value = null
    }
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
                Pedidos
            </h1>
            <p class="text-[#8c9e78] font-light">Visualize e gerencie as compras realizadas na loja</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <!-- Search Bar -->
            <div class="relative group w-96">
                <input v-model="searchTerm" type="text" placeholder="Pesquisar por cliente ou ID..."
                    class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
                <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
            </div>
        </div>

        <!-- Table -->
        <div class="px-10">
            <div v-if="loading" class="flex justify-center py-20">
                <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
            </div>

            <div v-else
                class="bg-white/50 backdrop-blur-sm rounded-lg overflow-hidden shadow-sm border border-[#eaddcf]">
                <table class="w-full text-left">
                    <thead class="bg-[#e4e3db] border-b border-[#eaddcf]">
                        <tr>
                            <th
                                class="py-4 px-6 font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Pedido</th>
                            <th
                                class="py-4 px-6 font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Data</th>
                            <th
                                class="py-4 px-6 font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Cliente</th>
                            <th
                                class="py-4 px-6 font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Total</th>
                            <th
                                class="py-4 px-6 font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm text-center">
                                Status</th>
                            <th
                                class="py-4 px-6 font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm text-right">
                                Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#eaddcf]">
                        <tr v-for="order in filteredOrders" :key="order.order_id" class="order-row">
                            <td class="py-4 px-6 text-[#3a5528] font-semibold text-sm">
                                #{{ order.order_id }}
                            </td>
                            <td class="py-4 px-6 text-[#3a5528] font-light text-sm">
                                {{ order.date }}
                            </td>
                            <td class="py-4 px-6 text-[#3a5528] font-medium text-sm">
                                {{ order.customer_name }}
                                <br />
                                <span class="text-xs text-[#8c9e78] font-light">{{ order.customer_email }}</span>
                            </td>
                            <td class="py-4 px-6 text-[#3a5528] font-medium text-sm">
                                {{ formatCurrency(order.total) }}
                            </td>
                            <td class="py-4 px-6 text-center">
                                <span v-if="order.paid"
                                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200 shadow-sm">
                                    Pago
                                </span>
                                <span v-else
                                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-200 shadow-sm">
                                    Pendente
                                </span>
                            </td>
                            <td class="py-4 px-6 text-right">
                                <div class="flex items-center justify-end gap-3">
                                    <button @click="openDetails(order)"
                                        class="text-[#3a5528] hover:text-[#2c3e20] hover:scale-110 transition-all p-1"
                                        title="Ver Detalhes">
                                        <FileText :size="17" />
                                    </button>
                                    <button @click="openDelete(order)" :disabled="order.paid"
                                        class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:scale-100"
                                        title="Cancelar/Excluir">
                                        <Trash2 :size="17" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="filteredOrders.length === 0">
                            <td colspan="6" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhum pedido encontrado.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <OrderDetailsModal :is-open="showDetailsModal" :order-id="selectedOrder" @close="showDetailsModal = false" />
        <ConfirmHardDeleteModal :is-open="showDeleteModal" title="Excluir Pedido Pendente"
            :message="`Tem certeza que deseja excluir o pedido #${orderToDelete?.order_id}?`"
            @close="showDeleteModal = false" @confirm="handleDelete" />
    </div>
</template>

<style scoped>
.order-row {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

.order-row:hover {
    background-color: #f0efe9;
}
</style>
