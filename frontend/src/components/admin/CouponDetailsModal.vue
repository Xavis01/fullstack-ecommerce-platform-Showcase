<script setup>
import { computed } from 'vue'
import { Loader2 } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    coupon: Object,
    loadingDetails: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const formatValor = computed(() => {
    if (!props.coupon) return ''
    if (props.coupon.porcentagem) {
        return `${props.coupon.valor}%`
    }
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(props.coupon.valor)
})

const formatDate = (dateString) => {
    if (!dateString) return 'Sem validade restrita'
    return new Date(dateString).toLocaleDateString('pt-BR', { timeZone: 'UTC' })
}

const formatCurrency = (val) => {
    if (!val && val !== 0) return 'Sem limite'
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}
</script>

<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="emit('close')"
            class="fixed inset-0 z-[110] flex items-center justify-center pt-24 sm:pt-8 px-4 pb-8 backdrop-blur-sm bg-black/60 font-montserrat">
            <div @click.stop
                class="bg-white w-full max-w-2xl rounded-2xl shadow-2xl p-6 relative space-y-4 border border-[#3a5528]/10 max-h-[85vh] overflow-y-auto">

                <!-- Loading Overlay -->
                <div v-if="loadingDetails"
                    class="absolute inset-0 bg-white/50 backdrop-blur-[2px] z-10 rounded-2xl flex flex-col items-center justify-center">
                    <Loader2 class="animate-spin text-[#3a5528] mb-2" :size="32" />
                    <span class="text-[#3a5528] text-sm font-light italic">Carregando detalhes...</span>
                </div>

                <!-- Botão fechar -->
                <button @click="emit('close')"
                    class="absolute top-5 right-5 text-[#53713d]/50 hover:text-[#53713d] text-2xl transition-colors">
                    <i class="fas fa-times"></i>
                </button>

                <h3 class="text-xl font-light italic text-[#53713d] tracking-wide pr-8 border-b border-[#eaddcf] pb-3">
                    Detalhes do Cupom: <span class="font-semibold">{{ coupon?.nome }}</span>
                </h3>

                <div v-if="coupon" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-[#53713d] text-sm">
                    <!-- Informações Básicas -->
                    <div class="space-y-2.5">
                        <h4 class="font-semibold italic border-b border-[#eaddcf]/50 pb-1.5">Informações Básicas</h4>

                        <div><strong class="font-normal italic">Desconto:</strong> {{ formatValor }}</div>
                        <div><strong class="font-normal italic">Frete Grátis:</strong> {{ coupon.frete_gratis ? 'Sim' :
                            'Não' }}</div>
                        <div><strong class="font-normal italic">Status:</strong> {{ coupon.is_active ? 'Ativo' :
                            'Inativo' }}</div>
                        <div v-if="coupon.descricao"><strong class="font-normal italic">Descrição:</strong> {{
                            coupon.descricao }}</div>
                        <div><strong class="font-normal italic">Usos:</strong> {{ coupon.vezes_usado }} vezes</div>
                    </div>

                    <!-- Regras de Uso -->
                    <div class="space-y-2.5">
                        <h4 class="font-semibold italic border-b border-[#eaddcf]/50 pb-1.5">Regras de Uso</h4>

                        <div><strong class="font-normal italic">Início:</strong> {{ formatDate(coupon.data_inicio) }}
                        </div>
                        <div><strong class="font-normal italic">Fim:</strong> {{ formatDate(coupon.data_fim) }}</div>
                        <div><strong class="font-normal italic">Gasto Mínimo:</strong> {{
                            formatCurrency(coupon.gasto_minimo) }}</div>
                        <div><strong class="font-normal italic">Gasto Máximo:</strong> {{
                            formatCurrency(coupon.gasto_maximo) }}</div>
                        <div><strong class="font-normal italic">Uso Individual:</strong> {{ coupon.uso_individual ? 'Sim (não comba) ' : 'Não(pode combar)' }}</div>
                        <div><strong class="font-normal italic">Exclui Itens c/ Desconto:</strong> {{
                            coupon.excluir_item_com_desconto ? 'Sim' : 'Não' }}</div>
                        <div><strong class="font-normal italic">Limite Total de Usos:</strong> {{ coupon.limite_uso ||
                            'Sem limite' }}</div>
                        <div><strong class="font-normal italic">Limite p/ Conta:</strong> {{ coupon.limite_por_conta ||
                            'Sem limite' }}</div>
                    </div>

                    <!-- Associações (Full Width) -->
                    <div class="space-y-4 col-span-1 md:col-span-2">
                        <h4 class="font-semibold italic border-b border-[#eaddcf]/50 pb-2">Vínculos de Entidades</h4>

                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <!-- Produtos -->
                            <div class="bg-[#f5ecd2]/30 p-3 rounded-lg border border-[#eaddcf]">
                                <strong class="block mb-2 font-normal italic">Produtos Ativos: {{ coupon.produtos ?
                                    'Sim' : 'Não' }}</strong>
                                <span class="text-xs">{{ coupon.excluir_produtos ? 'Exceções (proibido usar em):' :
                                    'Regra restrita aos selecionados:' }}</span>
                                <ul class="list-disc pl-5 mt-1 text-sm opacity-80 max-h-24 overflow-y-auto">
                                    <li v-for="p in coupon.product_coupons" :key="p.product_id">{{ p.product_name }}
                                    </li>
                                    <li v-if="!coupon.product_coupons?.length" class="list-none italic opacity-50">
                                        Nenhum selecionado</li>
                                </ul>
                            </div>

                            <!-- Categorias -->
                            <div class="bg-[#f5ecd2]/30 p-3 rounded-lg border border-[#eaddcf]">
                                <strong class="block mb-2 font-normal italic">Categorias Ativas: {{ coupon.categorias ?
                                    'Sim' : 'Não' }}</strong>
                                <span class="text-xs">{{ coupon.excluir_categorias ? 'Exceções (proibido usar em):' :
                                    'Regra restrita aos selecionados:' }}</span>
                                <ul class="list-disc pl-5 mt-1 text-sm opacity-80 max-h-24 overflow-y-auto">
                                    <li v-for="c in coupon.category_coupons" :key="c.category_id">{{ c.category_name }}
                                    </li>
                                    <li v-if="!coupon.category_coupons?.length" class="list-none italic opacity-50">
                                        Nenhuma selecionada</li>
                                </ul>
                            </div>

                            <!-- Coleções -->
                            <div class="bg-[#f5ecd2]/30 p-3 rounded-lg border border-[#eaddcf]">
                                <strong class="block mb-2 font-normal italic">Coleções Ativas: {{ coupon.colecoes ?
                                    'Sim' : 'Não' }}</strong>
                                <span class="text-xs">{{ coupon.excluir_colecoes ? 'Exceções (proibido usar em):' :
                                    'Regra restrita aos selecionados:' }}</span>
                                <ul class="list-disc pl-5 mt-1 text-sm opacity-80 max-h-24 overflow-y-auto">
                                    <li v-for="c in coupon.collection_coupons" :key="c.collection_id">{{
                                        c.collection_name }}</li>
                                    <li v-if="!coupon.collection_coupons?.length" class="list-none italic opacity-50">
                                        Nenhuma selecionada</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex justify-end pt-4">
                    <button @click="emit('close')"
                        class="px-6 py-2.5 bg-[#3a5528] text-[#f5ecd2] rounded-lg hover:bg-[#53713d] transition-all italic tracking-wide">
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    </transition>
</template>

<style scoped>
.modal-fade-enter-active {
    transition: opacity 0.3s ease, backdrop-filter 0.3s ease;
}

.modal-fade-leave-active {
    transition: opacity 0.25s ease, backdrop-filter 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.modal-fade-enter-active>div {
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}

.modal-fade-leave-active>div {
    transition: transform 0.25s cubic-bezier(0.7, 0, 0.84, 0), opacity 0.25s ease;
}

.modal-fade-enter-from>div {
    transform: translateY(-20px);
    opacity: 0;
}

.modal-fade-leave-to>div {
    transform: translateY(-10px);
    opacity: 0;
}
</style>
