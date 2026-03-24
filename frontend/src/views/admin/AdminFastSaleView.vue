<script setup>
import { ref, onMounted, computed } from 'vue'
import { Trash2, Pencil, Eye, Loader2, Settings, CreditCard, Banknote, QrCode, Search, Handshake, BarChart, EyeClosed } from 'lucide-vue-next'
import api from '@/api'
import { useToast } from 'vue-toastification'
import CreateFastSaleModal from '@/components/admin/FastSale/CreateFastSaleModal.vue'
import EditFastSaleModal from '@/components/admin/FastSale/EditFastSaleModal.vue'
import ViewFastSaleModal from '@/components/admin/FastSale/ViewFastSaleModal.vue'
import ConfirmDeleteModal from '@/components/admin/FastSale/ConfirmDeleteModal.vue'
import FastPriceConfigModal from '@/components/admin/FastSale/FastPriceConfigModal.vue'
import AdminFastSaleStatsModal from '@/components/admin/FastSale/AdminFastSaleStatsModal.vue'

const toast = useToast()
const sales = ref([])
const loading = ref(true)
const searchTerm = ref('')

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const showConfigModal = ref(false)
const showStatsModal = ref(false)
const isPriceVisible = ref(false)

const togglePriceVisibility = () => {
    isPriceVisible.value = !isPriceVisible.value
}

const selectedSale = ref(null)
const selectedSaleId = ref(null)

const fetchSales = async () => {
    loading.value = true
    try {
        const res = await api.get('/fast-sales')
        sales.value = res.data
    } catch (error) {
        console.error(error)
        toast.error('Erro ao buscar vendas rápidas')
    } finally {
        loading.value = false
    }
}

const filteredSales = computed(() => {
    if (!searchTerm.value) return sales.value
    const term = searchTerm.value.toLowerCase()
    return sales.value.filter(s =>
        s.client_name?.toLowerCase().includes(term) ||
        String(s.id).includes(term)
    )
})

const formatPayMethod = (method) => {
    const map = { pix: 'Pix', dinheiro: 'Dinheiro', cartao: 'Cartão', cota: 'Cota' }
    return map[method] || method
}

const getPaymentIcon = (method) => {
    switch (method) {
        case 'pix': return QrCode
        case 'dinheiro': return Banknote
        case 'cartao': return CreditCard
        case 'cota': return Handshake
        default: return Banknote
    }
}

const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    }).format(new Date(dateString))
}

// Modal actions
const openCreateModal = () => showCreateModal.value = true
const closeCreateModal = () => showCreateModal.value = false
const handleSaleCreated = () => { fetchSales(); closeCreateModal() }

const openConfigModal = () => showConfigModal.value = true
const closeConfigModal = () => showConfigModal.value = false

const openStatsModal = () => showStatsModal.value = true
const closeStatsModal = () => showStatsModal.value = false

const openEditModal = (sale) => { selectedSale.value = sale; showEditModal.value = true }
const closeEditModal = () => { showEditModal.value = false; selectedSale.value = null }
const handleSaleUpdated = () => { fetchSales(); closeEditModal() }

const openViewModal = (sale) => { selectedSale.value = sale; showViewModal.value = true }
const closeViewModal = () => { showViewModal.value = false; selectedSale.value = null }

const openDeleteModal = (id) => { selectedSaleId.value = id; showDeleteModal.value = true }
const closeDeleteModal = () => { showDeleteModal.value = false; selectedSaleId.value = null }
const handleSaleDeleted = () => { fetchSales(); closeDeleteModal() }

onMounted(() => fetchSales())
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Venda Rápida
            </h1>
            <p class="text-[#8c9e78] font-light">Registre e gerencie as vendas rápidas da loja</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <!-- Search -->
            <div class="relative group w-96">
                <input v-model="searchTerm" type="text" placeholder="Pesquisar por cliente ou ID..."
                    class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
                <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
            </div>

            <!-- Buttons -->
            <div class="flex gap-2 items-center">
                <!-- Visibilidade de Preço -->
                <button @click="togglePriceVisibility"
                    class="group flex items-center justify-center p-2.5 rounded-xl border border-[#0f2301]/10 bg-white/40 backdrop-blur-md text-[#3a5528] hover:bg-white hover:border-[#0f2301]/30 hover:shadow-lg transition-all duration-300 active:scale-90"
                    :title="isPriceVisible ? 'Ocultar Preços' : 'Mostrar Preços'">
                    <component :is="isPriceVisible ? Eye : EyeClosed" :size="20"
                        class="transition-transform duration-500 group-hover:scale-110" />
                </button>

                <div class="w-px h-6 bg-[#0f2301]/20 mx-1"></div>

                <button @click="openStatsModal"
                    class="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#0f2301]/40 text-[#3a5528] text-sm font-light italic tracking-wide hover:bg-[#0f2301]/50 transition-all">
                    <BarChart3 :size="16" />
                    Estatísticas
                </button>

                <button @click="openConfigModal"
                    class="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#0f2301]/40 text-[#3a5528] text-sm font-light italic tracking-wide hover:bg-[#0f2301]/50 transition-all">
                    <Settings :size="16" />
                    Configurar Preços
                </button>

                <div class="w-px h-6 bg-[#0f2301]/20 mx-1"></div>

                <button @click="openCreateModal"
                    class="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                    <span class="text-base leading-none">+</span> Nova Venda
                </button>
            </div>
        </div>

        <!-- Table -->
        <div class="px-10">
            <div v-if="loading" class="flex justify-center py-20">
                <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
            </div>

            <div v-else
                class="bg-white/50 backdrop-blur-sm rounded-lg overflow-hidden shadow-sm border border-[#eaddcf]">
                <table class="w-full">
                    <thead class="bg-[#e4e3db] border-b border-[#eaddcf]">
                        <tr>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                ID</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Cliente</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Total</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Pagamento</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Data</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#eaddcf]">
                        <tr v-for="sale in filteredSales" :key="sale.id" class="sale-row">
                            <td class="py-4 px-6 text-[#3a5528] font-light text-sm">#{{ sale.id }}</td>
                            <td class="py-4 px-6 text-[#3a5528] font-medium">{{ sale.client_name || '—' }}</td>
                            <td class="py-4 px-6 text-[#6b8555] font-light">
                                <template v-if="isPriceVisible">
                                    R$ {{ Number(sale.total_price).toFixed(2) }}
                                </template>
                                <template v-else>
                                    R$ ••••
                                </template>
                            </td>
                            <td class="py-4 px-6 text-[#6b8555] font-light">
                                <div class="flex items-center gap-2">
                                    <component :is="getPaymentIcon(sale.pay_method)" :size="15"
                                        class="text-[#0f2301]" />
                                    {{ formatPayMethod(sale.pay_method) }}
                                </div>
                            </td>
                            <td class="py-4 px-6 text-[#6b8555] font-light text-sm">{{ formatDate(sale.date) }}</td>
                            <!-- Ações -->
                            <td class="py-4 px-6">
                                <div class="flex items-center gap-1">
                                    <button @click="openViewModal(sale)" title="Ver Detalhes"
                                        class="text-[#3a5528] hover:text-[#2c3e20] hover:scale-110 transition-all p-1">
                                        <Eye :size="17" />
                                    </button>
                                    <button @click="openEditModal(sale)" title="Editar"
                                        class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1">
                                        <Pencil :size="17" />
                                    </button>
                                    <button @click="openDeleteModal(sale.id)" title="Deletar"
                                        class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1">
                                        <Trash2 :size="17" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="filteredSales.length === 0">
                            <td colspan="6" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhuma venda encontrada.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <CreateFastSaleModal :isOpen="showCreateModal" @close="closeCreateModal" @created="handleSaleCreated" />
        <FastPriceConfigModal :isOpen="showConfigModal" @close="closeConfigModal" />
        <EditFastSaleModal :isOpen="showEditModal" :sale="selectedSale" @close="closeEditModal"
            @updated="handleSaleUpdated" />
        <ViewFastSaleModal :isOpen="showViewModal" :sale="selectedSale" @close="closeViewModal" />
        <ConfirmDeleteModal :isOpen="showDeleteModal" :saleId="selectedSaleId" @close="closeDeleteModal"
            @deleted="handleSaleDeleted" />
        <AdminFastSaleStatsModal :isOpen="showStatsModal" :sales="sales" :isPriceVisible="isPriceVisible"
            @close="closeStatsModal" @togglePriceVisibility="togglePriceVisibility" />
    </div>
</template>

<style scoped>
.sale-row {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

.sale-row:hover {
    background-color: #f0efe9;
}
</style>
