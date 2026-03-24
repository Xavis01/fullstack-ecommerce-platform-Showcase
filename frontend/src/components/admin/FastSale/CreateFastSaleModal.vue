<template>
    <transition name="modal-fade">
        <div v-if="isOpen"
            class="fixed inset-0 z-50 flex items-start justify-center bg-black/50 backdrop-blur-sm pt-32 pb-8 overflow-y-auto"
            @click="close">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl p-6 relative font-montserrat mb-auto"
                @click.stop>

                <button @click="close" class="absolute top-4 right-4 text-[#3a5528] hover:text-[#9a382d]">
                    <X class="w-6 h-6" />
                </button>

                <h2 class="text-2xl font-light italic text-[#3a5528] mb-6">Nova Venda Rápida</h2>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <!-- Nome do Cliente -->
                    <div>
                        <label class="block text-sm font-medium text-[#3a5528] mb-1">Nome do Cliente (Opcional)</label>
                        <div class="relative">
                            <User class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#3a5528]" />
                            <input v-model="form.client_name" type="text"
                                class="w-full border border-[#0f2301]/30 rounded-lg pl-10 pr-4 py-3 h-11 focus:ring-2 focus:ring-[#0f2301] outline-none text-[#3a5528] font-montserrat italic" />
                        </div>
                    </div>

                    <!-- Método de Pagamento -->
                    <div>
                        <label class="block text-sm font-medium text-[#3a5528] mb-1">Método de Pagamento</label>
                        <RoccaSelect v-model="form.pay_method" :options="paymentMethods" />
                    </div>

                    <!-- Data -->
                    <div>
                        <label class="block text-sm font-medium text-[#3a5528] mb-1">Data</label>
                        <RoccaDatePicker v-model="form.date" />
                    </div>
                </div>

                <!-- Adicionar Produtos -->
                <div class="bg-[#e4e3db] p-4 rounded-lg border border-[#0f2301]/10 mb-6">
                    <h3 class="text-lg font-light italic text-[#3a5528] mb-4">Adicionar Produtos</h3>

                    <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
                        <!-- Produto -->
                        <div class="md:col-span-4">
                            <label class="block text-sm font-medium text-[#3a5528] mb-1">Produto</label>
                            <RoccaSelect v-model="selectedProductId" :options="productOptions"
                                placeholder="Selecione um produto" show-images searchable @change="onProductSelect" />
                        </div>

                        <!-- Variante -->
                        <div class="md:col-span-3">
                            <label class="block text-sm font-medium text-[#3a5528] mb-1">Tamanho</label>
                            <RoccaSelect v-model="selectedVariantId" :options="variantOptions" placeholder="Selecione"
                                :disabled="!selectedProduct" />
                        </div>

                        <!-- Quantidade -->
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-[#3a5528] mb-1">Qtd</label>
                            <div class="h-11 flex items-center ml-4">
                                <QuantityControl v-model="quantity" :min="1" :max="selectedVariant?.stock || 1"
                                    :disabled="!selectedVariant" />
                            </div>
                        </div>

                        <!-- Botão Adicionar -->
                        <div class="md:col-span-3">
                            <button @click="addItem" :disabled="!isValidItem"
                                class="w-full bg-[#0f2301] text-white py-2 rounded-lg hover:bg-[#0f2301]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                                Adicionar Item
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Lista de Itens -->
                <Transition name="expand">
                    <div v-if="form.items.length > 0" class="mb-6 overflow-hidden">
                        <table class="w-full text-sm text-left">
                            <thead class="bg-[#e4e3db] text-[#3a5528]">
                                <tr>
                                    <th class="p-3 rounded-tl-lg">Imagem</th>
                                    <th class="p-3">Produto</th>
                                    <th class="p-3">Tamanho</th>
                                    <th class="p-3">Qtd</th>
                                    <th class="p-3">Preço Unit.</th>
                                    <th class="p-3">Subtotal</th>
                                    <th class="p-3 rounded-tr-lg">Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in form.items" :key="index"
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
                                    <td class="p-3">
                                        <button @click="removeItem(index)"
                                            class="text-[#9a382d] hover:text-[#9a382d]/80">
                                            <Trash2 class="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                            <tfoot class="font-bold text-[#3a5528] bg-[#e4e3db]">
                                <tr>
                                    <td colspan="5" class="p-3 text-right">Total:</td>
                                    <td class="p-3">R$ {{ totalSale.toFixed(2) }}</td>
                                    <td></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </Transition>

                <div class="flex justify-end gap-3">
                    <button @click="close"
                        class="px-6 py-2 border border-[#0f2301]/30 rounded-lg text-[#3a5528] hover:bg-[#0f2301]/50 transition-colors">
                        Cancelar
                    </button>
                    <button @click="submit" :disabled="form.items.length === 0 || loading"
                        class="px-6 py-2 bg-[#0f2301] text-white rounded-lg hover:bg-[#0f2301]/90 transition-colors disabled:opacity-50 flex items-center gap-2">
                        <LoaderCircle v-if="loading" class="w-4 h-4 animate-spin" />
                        Finalizar Venda
                    </button>
                </div>

            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { X, Trash2, LoaderCircle, Plus, QrCode, Banknote, CreditCard, User, Handshake } from 'lucide-vue-next'
import api from '@/api'
import { useToast } from 'vue-toastification'
import RoccaDatePicker from '@/components/common/RoccaDatePicker.vue'
import RoccaSelect from '@/components/common/RoccaSelect.vue'
import QuantityControl from '@/components/common/QuantityControl.vue'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close', 'created'])
const toast = useToast()

const loading = ref(false)
const products = ref([])
const form = ref({
    client_name: '',
    pay_method: 'pix',
    date: new Date().toISOString(),
    items: [],
    total_price: 0
})

const selectedProductId = ref(null)
const selectedVariantId = ref(null)
const quantity = ref(1)

const paymentMethods = [
    { value: 'pix', label: 'Pix', icon: QrCode },
    { value: 'dinheiro', label: 'Dinheiro', icon: Banknote },
    { value: 'cartao', label: 'Cartão', icon: CreditCard },
    { value: 'cota', label: 'Cota', icon: Handshake }
]

const fetchProducts = async () => {
    try {
        const res = await api.get('/admin/products/list?status=ativo')
        products.value = res.data
    } catch (error) {
        console.error("Erro ao buscar produtos", error)
        toast.error("Erro ao carregar produtos")
    }
}

const selectedProduct = computed(() => {
    return products.value.find(p => p.id === selectedProductId.value) || null
})

const selectedVariant = computed(() => {
    if (!selectedProduct.value) return null
    return selectedProduct.value.variants?.find(v => v.id === selectedVariantId.value) || null
})

const productOptions = computed(() => {
    return products.value.map(p => ({
        value: p.id,
        label: p.name,
        image: p.image_url
    }))
})

const availableVariants = computed(() => {
    if (!selectedProduct.value) return []
    return selectedProduct.value.variants || []
})

const variantOptions = computed(() => {
    return availableVariants.value.map(v => ({
        value: v.id,
        label: `${v.size} (Estoque: ${v.stock})`,
        disabled: v.stock <= 0
    }))
})

const cdnBaseUrl = import.meta.env.VITE_CDN_BASE_URL || ''

const getImageUrl = (imagePath) => {
    if (!imagePath) return ''
    if (imagePath.startsWith('http')) return imagePath
    const cleanPath = imagePath.replace(/^(\/?uploads\/)+/, '')
    return `${cdnBaseUrl}/uploads/${cleanPath}`
}

const onProductSelect = () => {
    selectedVariantId.value = null
    quantity.value = 1
}

const isValidItem = computed(() => {
    return selectedProduct.value && selectedVariant.value && quantity.value > 0 && quantity.value <= selectedVariant.value.stock
})

const addItem = () => {
    if (!isValidItem.value) return

    const variant = selectedVariant.value
    const product = selectedProduct.value

    // Verifica se já existe o item na lista (mesma variante)
    const existingIndex = form.value.items.findIndex(i => i.product_variant_id === variant.id)

    if (existingIndex >= 0) {
        // Se somar ultrapassar estoque, avisa
        if (form.value.items[existingIndex].quantity + quantity.value > variant.stock) {
            toast.warning("Quantidade total excede o estoque disponível")
            return
        }
        form.value.items[existingIndex].quantity += quantity.value
    } else {
        form.value.items.push({
            product_id: product.id,
            product_name: product.name,
            product_image: product.image_url,
            product_variant_id: variant.id,
            size: variant.size,
            price: product.fast_price || product.price,
            quantity: quantity.value
        })
    }

    // Resetar seleção
    selectedProductId.value = null
    selectedVariantId.value = null
    quantity.value = 1
}

const removeItem = (index) => {
    form.value.items.splice(index, 1)
}

const totalSale = computed(() => {
    return form.value.items.reduce((acc, item) => acc + (item.price * item.quantity), 0)
})

const submit = async () => {
    loading.value = true
    try {
        form.value.total_price = totalSale.value
        await api.post('/fast-sales', form.value)
        toast.success("Venda realizada com sucesso!")
        emit('created')
        resetForm()
    } catch (error) {
        console.error(error)
        toast.error(error.response?.data?.error || "Erro ao criar venda")
    } finally {
        loading.value = false
    }
}

const resetForm = () => {
    form.value = {
        client_name: '',
        pay_method: 'pix',
        date: new Date().toISOString(),
        items: [],
        total_price: 0
    }
    selectedProductId.value = null
    selectedVariantId.value = null
    quantity.value = 1
}

const close = () => {
    emit('close')
    resetForm()
}

watch(() => props.isOpen, (newVal) => {
    if (newVal) {
        fetchProducts()
        resetForm()
    }
})

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

/* Smooth expansion animation */
.expand-enter-active,
.expand-leave-active {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    max-height: 600px;
}

.expand-enter-from,
.expand-leave-to {
    max-height: 0;
    opacity: 0;
    transform: scaleY(0.95);
}

.expand-enter-to,
.expand-leave-from {
    max-height: 600px;
    opacity: 1;
    transform: scaleY(1);
}
</style>
