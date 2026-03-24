<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { Search, Loader2, Pencil, Trash2, Eye, Power, PowerOff } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import CouponFormModal from '@/components/admin/CouponFormModal.vue'
import ConfirmDeleteCouponModal from '@/components/admin/ConfirmDeleteCouponModal.vue'
import ConfirmToggleCouponModal from '@/components/admin/ConfirmToggleCouponModal.vue'
import CouponDetailsModal from '@/components/admin/CouponDetailsModal.vue'

const toast = useToast()
const coupons = ref([])
const loading = ref(false)
const searchTerm = ref('')

const showFormModal = ref(false)
const showDeleteModal = ref(false)
const showToggleModal = ref(false)
const showDetailsModal = ref(false)

const editingCoupon = ref(null)
const couponToDelete = ref(null)
const couponToToggle = ref(null)
const couponToView = ref(null)
const saving = ref(false)
const loadingDetails = ref(false)

const fetchCoupons = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/coupons/list')
        if (response.data.error) {
            toast.error(response.data.error)
        } else {
            coupons.value = response.data
        }
    } catch (error) {
        console.error('Error fetching coupons:', error)
        toast.error('Erro ao carregar cupons')
    } finally {
        loading.value = false
    }
}

const filteredCoupons = computed(() => {
    if (!searchTerm.value) return coupons.value
    const term = searchTerm.value.toLowerCase()
    return coupons.value.filter(c => c.nome?.toLowerCase().includes(term))
})

const openCreate = () => {
    editingCoupon.value = null
    showFormModal.value = true
}

const openEdit = async (coupon) => {
    editingCoupon.value = { ...coupon }
    showFormModal.value = true
    loadingDetails.value = true
    try {
        const response = await api.get(`/admin/coupons/get/${coupon.id}`)
        editingCoupon.value = response.data
    } catch (err) {
        toast.error('Erro ao buscar dados do cupom')
        showFormModal.value = false
    } finally {
        loadingDetails.value = false
    }
}

const openView = async (coupon) => {
    couponToView.value = { ...coupon }
    showDetailsModal.value = true
    loadingDetails.value = true
    try {
        const response = await api.get(`/admin/coupons/get/${coupon.id}`)
        couponToView.value = response.data
    } catch (err) {
        toast.error('Erro ao buscar detalhes')
        showDetailsModal.value = false
    } finally {
        loadingDetails.value = false
    }
}

const openDelete = (coupon) => {
    couponToDelete.value = coupon
    showDeleteModal.value = true
}

const openToggle = (coupon) => {
    couponToToggle.value = coupon
    showToggleModal.value = true
}

const handleToggleSaved = () => {
    fetchCoupons()
    showToggleModal.value = false
    couponToToggle.value = null
}

const handleFormSaved = async (payload) => {
    saving.value = true
    try {
        if (editingCoupon.value) {
            await api.put(`/admin/coupons/update/${editingCoupon.value.id}`, payload)
            toast.success('Cupom atualizado!')
        } else {
            await api.post('/admin/coupons/create', payload)
            toast.success('Cupom criado!')
        }
        fetchCoupons()
        showFormModal.value = false
        editingCoupon.value = null
    } catch (error) {
        toast.error(error.response?.data?.error || 'Erro ao salvar cupom')
    } finally {
        saving.value = false
    }
}

const handleDeleted = () => {
    fetchCoupons()
    showDeleteModal.value = false
    couponToDelete.value = null
}

const formatValor = (coupon) => {
    if (coupon.porcentagem) {
        return `${coupon.valor}%`
    }
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(coupon.valor)
}

onMounted(() => {
    fetchCoupons()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Cupons de Desconto
            </h1>
            <p class="text-[#8c9e78] font-light">Gerencie os cupons da loja</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <!-- Search Bar -->
            <div class="relative group w-96">
                <input v-model="searchTerm" type="text" placeholder="Pesquisar por nome..."
                    class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
                <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
            </div>

            <!-- Create Button -->
            <button @click="openCreate"
                class="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                <span class="text-base leading-none">+</span> Novo Cupom
            </button>
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
                                Nome</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Desconto / Valor</th>
                            <th
                                class="py-4 px-6 text-center font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Ativo</th>
                            <th
                                class="py-4 px-6 text-center font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Usado</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#eaddcf]">
                        <tr v-for="coupon in filteredCoupons" :key="coupon.id" class="coupon-row">
                            <td class="py-4 px-6 text-[#3a5528] font-medium">{{ coupon.nome }}</td>
                            <td class="py-4 px-6 text-[#6b8555] font-light">{{ formatValor(coupon) }}</td>
                            <td class="py-4 px-6 text-center">
                                <button @click="openToggle(coupon)" class="p-2 rounded-full transition-colors"
                                    :class="coupon.is_active ? 'text-[#0f2301] hover:bg-[#0f2301]/10' : 'text-[#9a382d] hover:bg-[#9a382d]/10'"
                                    :title="coupon.is_active ? 'Desativar Cupom' : 'Ativar Cupom'">
                                    <Power v-if="coupon.is_active" :size="20" />
                                    <PowerOff v-else :size="20" />
                                </button>
                            </td>
                            <td class="py-4 px-6 text-center text-[#6b8555] font-light">
                                {{ coupon.vezes_usado }}x
                            </td>
                            <!-- Ações -->
                            <td class="py-4 px-6">
                                <div class="flex items-center gap-3">
                                    <button @click="openView(coupon)"
                                        class="text-[#3a5528] hover:text-[#2c3e20] hover:scale-110 transition-all p-1"
                                        title="Detalhes">
                                        <Eye :size="17" />
                                    </button>
                                    <button @click="openEdit(coupon)"
                                        class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                                        title="Editar">
                                        <Pencil :size="17" />
                                    </button>
                                    <button @click="openDelete(coupon)"
                                        class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1"
                                        title="Excluir">
                                        <Trash2 :size="17" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="filteredCoupons.length === 0">
                            <td colspan="5" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhum cupom encontrado.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <!-- Modals -->
        <CouponFormModal :is-open="showFormModal" :edit-data="editingCoupon" :saving="saving"
            :loading-details="loadingDetails" @close="showFormModal = false" @save="handleFormSaved" />

        <ConfirmDeleteCouponModal :is-open="showDeleteModal" :coupon="couponToDelete" @close="showDeleteModal = false"
            @deleted="handleDeleted" />

        <ConfirmToggleCouponModal :is-open="showToggleModal" :coupon="couponToToggle" @close="showToggleModal = false"
            @toggled="handleToggleSaved" />

        <CouponDetailsModal :is-open="showDetailsModal" :coupon="couponToView" :loading-details="loadingDetails"
            @close="showDetailsModal = false" />
    </div>
</template>

<style scoped>
.coupon-row {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

.coupon-row:hover {
    background-color: #f0efe9;
}
</style>
