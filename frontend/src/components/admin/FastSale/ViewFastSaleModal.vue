<template>
    <transition name="modal-fade">
        <div v-if="isOpen"
            class="fixed inset-0 z-50 flex items-start justify-center bg-black/50 backdrop-blur-sm pt-32 pb-8 overflow-y-auto"
            @click="close">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl p-6 relative font-montserrat mb-auto"
                @click.stop>

                <button @click="close" class="absolute top-4 right-4 text-[#3a5528] hover:text-[#9a382d]">
                    <X class="w-6 h-6" />
                </button>

                <h2 class="text-2xl font-light italic text-[#3a5528] mb-6">Detalhes da Venda #{{ sale?.id }}</h2>

                <div v-if="sale" class="space-y-6">
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <label class="block text-[#3a5528]/70 font-bold">Cliente</label>
                            <p class="text-[#3a5528]">{{ sale.client_name || 'Não informado' }}</p>
                        </div>
                        <div>
                            <label class="block text-[#3a5528]/70 font-bold">Data da Venda</label>
                            <p class="text-[#3a5528]">{{ formatDate(sale.created_at) }}</p>
                        </div>
                        <div>
                            <label class="block text-[#3a5528]/70 font-bold">Método de Pagamento</label>
                            <p class="text-[#3a5528]">{{ formatPayMethod(sale.pay_method) }}</p>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-[#0f2301]/70 mb-1">Vendedor</h3>
                            <p class="text-lg text-[#3a5528] font-light">{{ sale.created_by_name || sale.created_by }}
                            </p>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-lg font-light italic text-[#3a5528] mb-2 border-b border-[#0f2301]/10 pb-2">
                            Itens</h3>
                        <table class="w-full text-sm text-left">
                            <thead>
                                <tr class="bg-[#e4e3db] text-[#3a5528]">
                                    <th class="p-3 rounded-tl-lg">Imagem</th>
                                    <th class="p-3">Produto</th>
                                    <th class="p-3">Tamanho</th>
                                    <th class="p-3">Qtd</th>
                                    <th class="p-3">Preço Unit.</th>
                                    <th class="p-3 rounded-tr-lg">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in sale.items" :key="index"
                                    class="border-b border-[#0f2301]/10">
                                    <td class="p-3">
                                        <img v-if="item.product_image" :src="getImageUrl(item.product_image)"
                                            class="w-12 h-12 object-cover rounded" />
                                        <div v-else
                                            class="w-12 h-12 bg-[#0f2301] rounded flex items-center justify-center">
                                            <span class="text-xs text-[#3a5528]">N/A</span>
                                        </div>
                                    </td>
                                    <td class="p-3">{{ item.product_name }}</td>
                                    <td class="p-3">{{ item.size }}</td>
                                    <td class="p-3">{{ item.quantity }}</td>
                                    <td class="p-3">R$ {{ item.price.toFixed(2) }}</td>
                                    <td class="p-3 font-semibold">R$ {{ (item.price * item.quantity).toFixed(2) }}</td>
                                </tr>
                            </tbody>
                            <tfoot>
                                <tr class="font-bold text-[#3a5528] bg-[#e4e3db]">
                                    <td colspan="5" class="p-3 text-right">Total:</td>
                                    <td class="p-3">R$ {{ sale.total_price.toFixed(2) }}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                    <div class="flex justify-end pt-4">
                        <button @click="close"
                            class="px-6 py-2 bg-[#0f2301] text-white rounded-lg hover:bg-[#0f2301]/90 transition-colors">
                            Fechar
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </transition>
</template>

<script setup>
import { X } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    sale: Object
})

const emit = defineEmits(['close'])

const close = () => {
    emit('close')
}

const formatPayMethod = (method) => {
    const map = {
        'pix': 'Pix',
        'dinheiro': 'Dinheiro',
        'cartao': 'Cartão',
        'cota': 'Cota'
    }
    return map[method] || method
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    // Adjust -3 hours for display
    date.setHours(date.getHours() - 3)
    return date.toLocaleString('pt-BR')
}

const cdnBaseUrl = import.meta.env.VITE_CDN_BASE_URL || ''

const getImageUrl = (imagePath) => {
    if (!imagePath) return ''
    if (imagePath.startsWith('http')) return imagePath
    const cleanPath = imagePath.replace(/^(\/?uploads\/)+/, '')
    return `${cdnBaseUrl}/uploads/${cleanPath}`
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
</style>
