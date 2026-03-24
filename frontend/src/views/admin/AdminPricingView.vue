<template>
    <div class="min-h-screen font-montserrat bg-[#fffdf2] pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Precificação
            </h1>
            <p class="text-[#8c9e78] font-light">Gerencie os custos e preços de venda dos produtos</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <!-- Esquerda vazia ou futura busca -->
            <div></div>

            <!-- Botão Adicionar -->
            <button
                class="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm"
                @click="addRow">
                <span class="text-base leading-none">+</span> Adicionar Produto
            </button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-20">
            <LoaderCircle class="animate-spin text-[#3a5528] w-10 h-10" />
        </div>

        <div v-else class="px-10">
            <div
                class="bg-white/50 backdrop-blur-sm rounded-lg overflow-hidden shadow-sm border border-[#eaddcf] overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-[#e4e3db] border-b border-[#eaddcf]">
                        <tr>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Produto</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Custo Produto</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Preço Venda</th>
                            <th class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs"
                                title="Subsídio de Frete">Sub. Frete</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Ads</th>

                            <!-- Calculated Columns -->
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528]/70 tracking-wider text-xs">
                                Mkt (10%)</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528]/70 tracking-wider text-xs">
                                Fin (10.7%)</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-bold text-[#3a5528] tracking-wider text-xs">
                                Custo Total</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-bold text-[#3a5528] tracking-wider text-xs">
                                Lucro</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Margem %</th>
                            <th
                                class="py-4 px-4 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Markup</th>
                            <th
                                class="py-4 px-4 text-center font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-xs">
                                Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#eaddcf]">
                        <tr v-for="(row, index) in rows" :key="index" class="pricing-row">
                            <!-- Inputs -->
                            <td class="p-3">
                                <input v-model="row.name" @blur="updateItem(row)" placeholder="Nome..."
                                    class="w-32 bg-transparent border-b border-[#0f2301]/30 focus:border-[#0f2301] outline-none text-[#3a5528] placeholder-[#8c9e78] text-xs py-1 transition-colors" />
                            </td>
                            <td class="p-3">
                                <div class="relative flex items-center gap-2">
                                    <div class="relative w-20">
                                        <span class="absolute left-0 top-1 text-[#0f2301]/50 text-xs">R$</span>
                                        <input type="number" step="0.01" v-model.number="row.cost"
                                            @blur="updateItem(row)"
                                            class="w-full pl-5 bg-transparent border-b border-[#0f2301]/30 focus:border-[#0f2301] outline-none text-[#3a5528] font-medium text-xs py-1 transition-colors" />
                                    </div>
                                    <button @click="openCalculator(row)" title="Calculadora de Custo"
                                        class="text-[#fffdf2] hover:scale-110 transition-transform bg-[#0f2301]/10 p-1 rounded-md">
                                        <Calculator class="w-3 h-3" />
                                    </button>
                                </div>
                            </td>
                            <td class="p-3">
                                <div class="relative">
                                    <span class="absolute left-0 top-1 text-[#0f2301]/50 text-xs">R$</span>
                                    <input type="number" step="0.01" v-model.number="row.price" @blur="updateItem(row)"
                                        class="w-20 pl-5 bg-transparent border-b border-[#0f2301]/30 focus:border-[#0f2301] outline-none text-[#3a5528] font-bold text-xs py-1 transition-colors" />
                                </div>
                            </td>
                            <td class="p-3">
                                <div class="relative">
                                    <span class="absolute left-0 top-1 text-[#0f2301]/50 text-xs">R$</span>
                                    <input type="number" step="0.01" v-model.number="row.subsidy_frete"
                                        @blur="updateItem(row)"
                                        class="w-16 pl-5 bg-transparent border-b border-[#0f2301]/30 focus:border-[#0f2301] outline-none text-[#3a5528] text-xs py-1 transition-colors" />
                                </div>
                            </td>
                            <td class="p-3">
                                <div class="relative">
                                    <span class="absolute left-0 top-1 text-[#0f2301]/50 text-xs">R$</span>
                                    <input type="number" step="0.01" v-model.number="row.ads" @blur="updateItem(row)"
                                        class="w-16 pl-5 bg-transparent border-b border-[#0f2301]/30 focus:border-[#0f2301] outline-none text-[#3a5528] text-xs py-1 transition-colors" />
                                </div>
                            </td>

                            <!-- Results -->
                            <td class="p-3 text-[#3a5528]/80 text-xs">
                                R$ {{ calculateMarketing(row).toFixed(2) }}
                            </td>
                            <td class="p-3 text-[#3a5528]/80 text-xs">
                                R$ {{ calculateFinancial(row).toFixed(2) }}
                            </td>
                            <td class="p-3 text-[#3a5528] font-bold text-xs">
                                R$ {{ calculateTotalCost(row).toFixed(2) }}
                            </td>
                            <td class="p-3 text-[#3a5528] font-bold text-xs"
                                :class="calculateProfit(row) < 0 ? 'text-[#9a382d]' : ''">
                                R$ {{ calculateProfit(row).toFixed(2) }}
                            </td>
                            <td class="p-3 text-[#3a5528] text-xs">
                                {{ calculateMargin(row).toFixed(1) }}%
                            </td>
                            <td class="p-3 text-[#3a5528] text-xs">
                                {{ calculateMarkup(row).toFixed(2) }}
                            </td>

                            <td class="p-3 text-center">
                                <button @click="removeRow(index, row.id)"
                                    class="text-[#9a382d] hover:scale-110 transition-transform p-1.5 hover:bg-red-50 rounded-lg"
                                    title="Remover">
                                    <Trash2 class="w-4 h-4" />
                                </button>
                            </td>
                        </tr>
                        <tr v-if="rows.length === 0">
                            <td colspan="12" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhum item de precificação encontrado.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Summary Cards -->
            <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 opacity-80">
                <div class="bg-[#0f2301]/30 p-5 rounded-lg border border-[#0f2301]/10 backdrop-blur-sm">
                    <h3 class="font-montserrat italic text-[#3a5528] mb-3 font-medium text-sm">Resumo das Taxas</h3>
                    <ul class="text-xs text-[#3a5528] space-y-2 font-light">
                        <li class="flex justify-between border-b border-[#0f2301]/10 pb-1"><span>Marketing:</span>
                            <span>10%</span>
                        </li>
                        <li class="flex justify-between border-b border-[#0f2301]/10 pb-1"><span>Financeiro:</span>
                            <span>10.7%</span>
                        </li>
                        <li class="flex justify-between pt-1"><span>Imposto:</span> <span>0%</span></li>
                    </ul>
                </div>
            </div>
        </div>

        <ConfirmDeletePricingModal :isOpen="showDeleteModal" :itemId="selectedIdToDelete"
            @close="showDeleteModal = false" @deleted="handleDeleted" />

        <ProductCostCalculatorModal :isOpen="showCalculatorModal" @close="showCalculatorModal = false"
            @confirm="handleCalculatorConfirm" />

    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Trash2, Save, Calculator, LoaderCircle } from 'lucide-vue-next'
import api from '@/api'
import { useToast } from 'vue-toastification'
import ConfirmDeletePricingModal from '@/components/admin/Pricing/ConfirmDeletePricingModal.vue'
import ProductCostCalculatorModal from '@/components/admin/Pricing/ProductCostCalculatorModal.vue'

const toast = useToast()
const rows = ref([])
const loading = ref(false)

const showDeleteModal = ref(false)
const selectedIdToDelete = ref(null)

const showCalculatorModal = ref(false)
const selectedRowForCalculation = ref(null)

// Fetch items
async function fetchItems() {
    loading.value = true
    try {
        const res = await api.get('/admin/pricing/list')
        rows.value = res.data
    } catch (err) {
        console.error(err)
        toast.error('Erro ao carregar itens de precificação')
    } finally {
        loading.value = false
    }
}

// Add new item
async function addRow() {
    try {
        const newItem = {
            name: '',
            cost: 0,
            price: 0,
            subsidy_frete: 10, // Default requested by user
            ads: 0
        }
        const res = await api.post('/admin/pricing/create', newItem)
        newItem.id = res.data.id
        rows.value.unshift(newItem) // Add to top
        toast.success('Novo item adicionado')
    } catch (err) {
        console.error(err)
        toast.error('Erro ao criar item')
    }
}

// Update item (auto-save or manual) - Implementing debounce or save on blur is better, 
// but for simplicity and robustness, let's use a "Save" button or save on change (blur).
// Let's do save on blur for inputs.
async function updateItem(row) {
    if (!row.id) return
    try {
        await api.put(`/admin/pricing/update/${row.id}`, {
            name: row.name,
            cost: row.cost,
            price: row.price,
            subsidy_frete: row.subsidy_frete,
            ads: row.ads
        })
        // Optional: toast.success('Salvo') - too noisy for every field
    } catch (err) {
        console.error(err)
        toast.error('Erro ao salvar alteração')
    }
}

// Delete item
async function removeRow(index, id) {
    if (!id) {
        rows.value.splice(index, 1) // Just remove from UI if not saved (shouldn't happen with current logic)
        return
    }

    selectedIdToDelete.value = id
    showDeleteModal.value = true
}

function handleDeleted() {
    // Remove locally after success
    const idx = rows.value.findIndex(r => r.id === selectedIdToDelete.value)
    if (idx !== -1) rows.value.splice(idx, 1)

    showDeleteModal.value = false
    selectedIdToDelete.value = null
}

// Calculator Logic
function openCalculator(row) {
    selectedRowForCalculation.value = row
    showCalculatorModal.value = true
}

function handleCalculatorConfirm(totalCost) {
    if (selectedRowForCalculation.value) {
        selectedRowForCalculation.value.cost = totalCost
        updateItem(selectedRowForCalculation.value) // Auto-save
        toast.success(`Custo atualizado para R$ ${totalCost.toFixed(2)}`)
    }
    showCalculatorModal.value = false
    selectedRowForCalculation.value = null
}

// Logic based on PlanilhaPrecificacao.xlsx
// Taxas fixas
const TAX_MARKETING = 0.10
const TAX_FINANCIAL = 0.107

function calculateMarketing(row) {
    return (row.price || 0) * TAX_MARKETING
}

function calculateFinancial(row) {
    return (row.price || 0) * TAX_FINANCIAL
}

function calculateTotalCost(row) {
    // Total Cost = Product Cost + Subsidy + Ads + Marketing + Financial + (Other zero fields like Tax)
    const mkt = calculateMarketing(row)
    const fin = calculateFinancial(row)
    return (row.cost || 0) + (row.subsidy_frete || 0) + (row.ads || 0) + mkt + fin
}

function calculateProfit(row) {
    const totalCost = calculateTotalCost(row)
    return (row.price || 0) - totalCost
}

function calculateMargin(row) {
    if (!row.price) return 0
    const profit = calculateProfit(row)
    return (profit * 100) / row.price
}

function calculateMarkup(row) {
    if (!row.cost || row.cost === 0) return 0
    return (row.price || 0) / row.cost
}

onMounted(() => {
    fetchItems()
})

</script>

<style scoped>
.pricing-row {
    background-color: transparent;
    transition: background-color 0.2s ease;
}

.pricing-row:hover {
    background-color: #f0efe9;
}

/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

/* Firefox */
input[type=number] {
    -moz-appearance: textfield;
    appearance: textfield;
}
</style>
