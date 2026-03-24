<template>
    <transition name="modal-fade">
        <div v-if="isOpen"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto"
            @click="close">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl p-8 relative font-montserrat border border-[#0f2301]/10"
                @click.stop>

                <button @click="close"
                    class="absolute top-6 right-6 text-[#3a5528] hover:text-[#9a382d] transition-colors">
                    <X class="w-6 h-6" />
                </button>

                <div class="flex justify-between items-start mb-8 pr-12">
                    <div>
                        <h2 class="text-2xl font-light italic text-[#3a5528] mb-2 tracking-wide">Estatísticas de Venda
                        </h2>
                        <p class="text-[#8c9e78] font-light">Filtre por período e método de pagamento para ver o
                            desempenho</p>
                    </div>

                    <button @click="$emit('togglePriceVisibility')"
                        class="group flex items-center gap-2 px-4 py-2 rounded-xl border border-[#0f2301]/10 bg-[#0f2301]/5 text-[#3a5528] hover:bg-white hover:border-[#0f2301]/30 hover:shadow-lg transition-all duration-300 active:scale-95"
                        :title="isPriceVisible ? 'Ocultar Preços' : 'Mostrar Preços'">
                        <component :is="isPriceVisible ? Eye : EyeClosed" :size="20"
                            class="transition-transform duration-500 group-hover:scale-110" />
                        <span
                            class="text-[10px] uppercase tracking-widest font-medium opacity-60 group-hover:opacity-100 transition-opacity">
                            {{ isPriceVisible ? 'Visível' : 'Oculto' }}
                        </span>
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <!-- Data Início -->
                    <div>
                        <label class="block text-sm font-medium text-[#3a5528] mb-2 italic">Data Início</label>
                        <RoccaDatePicker v-model="filters.startDate" placeholder="Início" />
                    </div>

                    <!-- Data Fim -->
                    <div>
                        <label class="block text-sm font-medium text-[#3a5528] mb-2 italic">Data Fim</label>
                        <RoccaDatePicker v-model="filters.endDate" placeholder="Fim" />
                    </div>

                    <!-- Métodos de Pagamento (MultiSelect) -->
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-[#3a5528] mb-2 italic">Métodos de Pagamento</label>
                        <MultiSelect v-model="filters.payMethods" :items="paymentMethodOptions"
                            placeholder="Selecione os métodos" />
                    </div>
                </div>

                <!-- Resultado -->
                <div
                    class="bg-[#e4e3db]/50 rounded-2xl p-8 border border-[#0f2301]/10 flex flex-col items-center justify-center text-center">
                    <span class="text-[#8c9e78] text-sm font-medium uppercase tracking-[0.2em] mb-2">Total
                        Vendido Bruto</span>
                    <div class="flex items-baseline gap-1">
                        <span class="text-[#3a5528] text-2xl font-light italic">R$</span>
                        <span v-if="isPriceVisible" class="text-[#0f2301] text-5xl font-light tracking-tight">{{
                            formattedTotal }}</span>
                        <span v-else class="text-[#0f2301] text-5xl font-light tracking-tight">••••</span>
                    </div>
                    <div class="mt-4 flex items-center gap-2 text-[#8c9e78] text-sm italic font-light">
                        <TrendingUp v-if="stats.count > 0" class="w-4 h-4" />
                        <span>Baseado em {{ stats.count }} {{ stats.count === 1 ? 'venda' : 'vendas' }} no
                            período</span>
                    </div>
                </div>

                <div class="mt-8 flex justify-end">
                    <button @click="close"
                        class="px-8 py-3 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#3a5528] transition-all shadow-md italic tracking-wide font-light">
                        Fechar Relatório
                    </button>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X, TrendingUp, Eye, EyeClosed } from 'lucide-vue-next'
import RoccaDatePicker from '@/components/common/RoccaDatePicker.vue'
import MultiSelect from '@/components/admin/Products/MultiSelect.vue'

const props = defineProps({
    isOpen: Boolean,
    sales: {
        type: Array,
        default: () => []
    },
    isPriceVisible: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['close', 'togglePriceVisibility'])

const paymentMethodOptions = [
    { id: 'pix', name: 'PIX' },
    { id: 'cartao', name: 'CARTÃO' },
    { id: 'dinheiro', name: 'DINHEIRO' },
    { id: 'cota', name: 'COTA' }
]

const filters = ref({
    startDate: '',
    endDate: '',
    payMethods: ['pix', 'cartao', 'dinheiro']
})

// Initialize dates when modal opens (start of month to today)
const initDates = () => {
    const now = new Date()
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
    filters.value.startDate = firstDay.toISOString()
    filters.value.endDate = now.toISOString()
    filters.value.payMethods = ['pix', 'cartao', 'dinheiro']
}

watch(() => props.isOpen, (val) => {
    if (val) {
        initDates()
    }
})

const stats = computed(() => {
    if (!props.sales.length) return { total: 0, count: 0 }

    const start = filters.value.startDate ? new Date(filters.value.startDate) : null
    const end = filters.value.endDate ? new Date(filters.value.endDate) : null

    // Set start to beginning of day and end to end of day for proper filtering
    if (start) start.setHours(0, 0, 0, 0)
    if (end) end.setHours(23, 59, 59, 999)

    const filtered = props.sales.filter(sale => {
        const saleDate = new Date(sale.date)

        // Date range filter
        const matchesDate = (!start || saleDate >= start) && (!end || saleDate <= end)

        // Payment method filter
        const matchesPayMethod = filters.value.payMethods.includes(sale.pay_method)

        return matchesDate && matchesPayMethod
    })

    const total = filtered.reduce((acc, sale) => acc + Number(sale.total_price), 0)

    return {
        total,
        count: filtered.length
    }
})

const formattedTotal = computed(() => {
    return stats.value.total.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })
})

const close = () => {
    emit('close')
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

/* Custom transitions matching other modals */
.modal-fade-enter-active>div {
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}

.modal-fade-leave-active>div {
    transition: transform 0.25s cubic-bezier(0.7, 0, 0.84, 0), opacity 0.25s ease;
}

.modal-fade-enter-from>div {
    transform: scale(0.95);
    opacity: 0;
}

.modal-fade-leave-to>div {
    transform: scale(0.95);
    opacity: 0;
}
</style>
