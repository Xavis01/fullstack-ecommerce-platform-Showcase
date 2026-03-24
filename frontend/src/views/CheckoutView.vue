<template>
    <div class="min-h-screen bg-[#fffdf2] font-montserrat mt-2 py-8 px-4 sm:px-6 lg:px-8">
        <div class="max-w-5xl mx-auto">
            <h1
                class="text-3xl font-['Montserrat'] font-light text-[#3a5528] italic mb-8 border-b border-[#eaddcf] pb-4">
                Finalizar Compra</h1>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

                <!-- Left: Order Summary + Address + Shipping -->
                <div class="space-y-6">
                    <!-- Resumo do Carrinho -->
                    <div>
                        <h2 class="text-xl font-medium italic text-[#3a5528] mb-4">Resumo do Pedido</h2>

                        <div v-for="item in cartStore.items" :key="item.variant_id"
                            class="bg-white p-4 rounded-xl shadow-sm border border-[#eaddcf] flex items-center gap-4 transition-all hover:bg-[#faf9f0] mb-3">

                            <div
                                class="w-16 h-16 bg-[#0f2301]/50 rounded-lg overflow-hidden flex-shrink-0 border border-[#0f2301]/20">
                                <img v-if="item.image_url" :src="item.image_url" :alt="item.name"
                                    class="w-full h-full object-cover" />
                            </div>

                            <div class="flex-1 min-w-0 flex flex-col justify-between py-1">
                                <div>
                                    <h3 class="font-medium text-[#3a5528] truncate">{{ item.name }}</h3>
                                    <p class="text-sm font-light text-[#8c9e78]">Qtd: <span class="font-medium">{{
                                        item.quantity }}</span> x <span class="font-medium">{{ item.size }}</span>
                                    </p>
                                </div>
                            </div>

                            <div class="font-medium text-[#6b8555]">
                                R$ {{ (item.price * item.quantity).toFixed(2) }}
                            </div>
                        </div>
                    </div>

                    <!-- Endereço de Entrega -->
                    <div class="bg-white/50 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-[#eaddcf]">
                        <h2 class="text-lg font-medium italic text-[#3a5528] mb-4 flex items-center gap-2">
                            <MapPin class="w-5 h-5" /> Endereço de Entrega
                        </h2>

                        <!-- CEP -->
                        <div class="mb-4">
                            <label class="block text-xs font-medium text-[#3a5528] mb-1">CEP *</label>
                            <div class="flex gap-2">
                                <input v-model="addressForm.cep" type="text" placeholder="00000-000"
                                    class="flex-1 bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm"
                                    @input="formatAddressCep" maxlength="9" />
                                <button @click="lookupCep"
                                    :disabled="loadingCep || addressForm.cep.replace(/\D/g, '').length < 8"
                                    class="bg-[#0f2301] text-[#fffdf2] px-4 py-2 rounded-lg font-light text-sm hover:bg-[#3a5528] transition-all disabled:opacity-50 flex items-center gap-2 whitespace-nowrap">
                                    <LoaderCircle v-if="loadingCep" class="w-4 h-4 animate-spin" />
                                    <span v-else>Buscar</span>
                                </button>
                            </div>
                        </div>

                        <!-- CPF -->
                        <div class="mb-4">
                            <label class="block text-xs font-medium text-[#3a5528] mb-1">CPF *</label>
                            <input v-model="addressForm.cpf" type="text" placeholder="000.000.000-00"
                                class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm"
                                @input="formatCpf" maxlength="14" />
                        </div>

                        <!-- Telefone -->
                        <div class="mb-4">
                            <label class="block text-xs font-medium text-[#3a5528] mb-1">Telefone *</label>
                            <input v-model="addressForm.phone" type="text" placeholder="(27) 99999-9999"
                                class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm"
                                @input="formatPhone" maxlength="15" />
                        </div>

                        <!-- Street + Number: oculto se retirada -->
                        <div v-if="!isPickup" class="grid grid-cols-3 gap-3 mb-3">
                            <div class="col-span-2">
                                <label class="block text-xs font-medium text-[#3a5528] mb-1">Rua *</label>
                                <input v-model="addressForm.address" type="text" placeholder="Rua/Logradouro"
                                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm" />
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-[#3a5528] mb-1">Número *</label>
                                <input v-model="addressForm.number" type="text" placeholder="Nº"
                                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm" />
                            </div>
                        </div>

                        <!-- Complement + Neighborhood: oculto se retirada -->
                        <div v-if="!isPickup" class="grid grid-cols-2 gap-3 mb-3">
                            <div>
                                <label class="block text-xs font-medium text-[#3a5528] mb-1">Complemento</label>
                                <input v-model="addressForm.complement" type="text" placeholder="Apto, Bloco..."
                                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm" />
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-[#3a5528] mb-1">Bairro *</label>
                                <input v-model="addressForm.neighborhood" type="text" placeholder="Bairro"
                                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm" />
                            </div>
                        </div>

                        <!-- City + State: oculto se retirada -->
                        <div v-if="!isPickup" class="grid grid-cols-3 gap-3">
                            <div class="col-span-2">
                                <label class="block text-xs font-medium text-[#3a5528] mb-1">Cidade *</label>
                                <input v-model="addressForm.city" type="text" placeholder="Cidade"
                                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm" />
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-[#3a5528] mb-1">UF *</label>
                                <input v-model="addressForm.state" type="text" placeholder="SP" maxlength="2"
                                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm uppercase" />
                            </div>
                        </div>

                        <!-- Info card quando retirada selecionada -->
                        <div v-if="isPickup"
                            class="mt-2 flex items-center gap-3 bg-[#3a5528]/5 border border-[#3a5528]/20 rounded-xl p-4">
                            <MapPin class="w-5 h-5 text-[#3a5528] flex-shrink-0" />
                            <div>
                                <p class="text-sm font-medium text-[#0f2301]">Retirada</p>
                                <p class="text-xs text-[#8c9e78] font-light">Jardim Camburi — Vitória, ES<br>O endereço
                                    exato será combinado após o pedido.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Opções de Frete -->
                    <div class="bg-white/50 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-[#eaddcf]">
                        <h2 class="text-lg font-medium italic text-[#3a5528] mb-4 flex items-center gap-2">
                            <Truck class="w-5 h-5" /> Opção de Envio
                        </h2>

                        <!-- Se já tem opções do carrinho -->
                        <div v-if="cartStore.shippingOptions.length > 0" class="space-y-2">
                            <button v-for="opt in cartStore.shippingOptions" :key="opt.id"
                                @click="cartStore.selectShipping(opt)"
                                class="w-full flex items-center justify-between py-3 px-4 border rounded-lg transition-all text-left"
                                :class="cartStore.selectedShipping?.id === opt.id
                                    ? 'border-[#0f2301] bg-[#0f2301]/5 shadow-sm'
                                    : 'border-[#eaddcf] hover:border-[#3a5528]/40 bg-[#faf9f0]'">
                                <div class="flex items-center gap-3">
                                    <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                                        :class="cartStore.selectedShipping?.id === opt.id ? 'border-[#0f2301]' : 'border-[#eaddcf]'">
                                        <div v-if="cartStore.selectedShipping?.id === opt.id"
                                            class="w-2.5 h-2.5 rounded-full bg-[#0f2301]"></div>
                                    </div>
                                    <div>
                                        <p class="text-sm font-medium text-[#0f2301]">{{ opt.name }}</p>
                                        <p class="text-xs text-[#8c9e78] font-light">{{ opt.delivery_time }} dias úteis
                                        </p>
                                    </div>
                                </div>
                                <span class="font-medium text-[#0f2301] text-sm">
                                    <span v-if="cartStore.isFreeShipping">R$ 0,00</span>
                                    <span v-else>R$ {{ opt.price.toFixed(2) }}</span>
                                </span>
                            </button>

                            <!-- Opção de Retirada -->
                            <button @click="cartStore.selectShipping(pickupOption)"
                                class="w-full flex items-center justify-between py-3 px-4 border rounded-lg transition-all text-left"
                                :class="cartStore.selectedShipping?.id === 'pickup'
                                    ? 'border-[#0f2301] bg-[#0f2301]/5 shadow-sm'
                                    : 'border-[#eaddcf] hover:border-[#3a5528]/40 bg-[#faf9f0]'">
                                <div class="flex items-center gap-3">
                                    <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                                        :class="cartStore.selectedShipping?.id === 'pickup' ? 'border-[#0f2301]' : 'border-[#eaddcf]'">
                                        <div v-if="cartStore.selectedShipping?.id === 'pickup'"
                                            class="w-2.5 h-2.5 rounded-full bg-[#0f2301]"></div>
                                    </div>
                                    <div>
                                        <p class="text-sm font-medium text-[#0f2301]">Retirada</p>
                                        <p class="text-xs text-[#8c9e78] font-light">Jardim Camburi — Vitória, ES</p>
                                    </div>
                                </div>
                                <span class="font-medium text-[#3a5528] text-sm">Grátis</span>
                            </button>
                        </div>

                        <!-- Se precisa calcular -->
                        <div v-else class="space-y-2">
                            <div v-if="cartStore.loadingShipping" class="flex justify-center py-2">
                                <LoaderCircle class="w-5 h-5 animate-spin text-[#3a5528]" />
                            </div>
                            <p v-else-if="!addressForm.cep || addressForm.cep.replace(/\D/g, '').length < 8"
                                class="text-sm text-[#8c9e78] font-light italic">
                                Preencha o CEP acima e clique em <strong>Buscar</strong> para ver as opções de envio.
                            </p>
                            <p v-else-if="cartStore.shippingError" class="text-xs text-[#9a382d] font-light">{{
                                cartStore.shippingError }}</p>
                            <p v-else class="text-sm text-[#8c9e78] font-light italic">
                                Clique em <strong>Buscar</strong> no campo CEP acima para ver as opções.
                            </p>

                            <!-- Opção de Retirada sempre disponível, mesmo sem calcular frete -->
                            <button @click="cartStore.selectShipping(pickupOption)"
                                class="w-full flex items-center justify-between py-3 px-4 border rounded-lg transition-all text-left"
                                :class="cartStore.selectedShipping?.id === 'pickup'
                                    ? 'border-[#0f2301] bg-[#0f2301]/5 shadow-sm'
                                    : 'border-[#eaddcf] hover:border-[#3a5528]/40 bg-[#faf9f0]'">
                                <div class="flex items-center gap-3">
                                    <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                                        :class="cartStore.selectedShipping?.id === 'pickup' ? 'border-[#0f2301]' : 'border-[#eaddcf]'">
                                        <div v-if="cartStore.selectedShipping?.id === 'pickup'"
                                            class="w-2.5 h-2.5 rounded-full bg-[#0f2301]"></div>
                                    </div>
                                    <div>
                                        <p class="text-sm font-medium text-[#0f2301]">Retirada</p>
                                        <p class="text-xs text-[#8c9e78] font-light">Jardim Camburi — Vitória, ES</p>
                                    </div>
                                </div>
                                <span class="font-medium text-[#3a5528] text-sm">Grátis</span>
                            </button>
                        </div>
                    </div>

                    <!-- Totals -->
                    <div
                        class="bg-white/50 backdrop-blur-sm p-4 rounded-xl shadow-sm border border-[#eaddcf] flex flex-col gap-2">
                        <div class="flex justify-between items-center text-[#8c9e78]">
                            <span class="font-light italic">Subtotal:</span>
                            <span class="font-medium">R$ {{ cartStore.total.toFixed(2) }}</span>
                        </div>
                        <div v-if="cartStore.appliedCoupon"
                            class="flex flex-col sm:flex-row justify-between text-[#0f2301] items-start sm:items-center gap-2">
                            <span
                                class="font-light italic flex items-center gap-1 group relative cursor-help w-full sm:w-auto"
                                :title="cartStore.appliedCouponData?.descricao || 'Cupom de Desconto'">
                                <Tag class="w-4 h-4 flex-shrink-0" /> <span class="truncate pr-2">Cupom ({{
                                    cartStore.appliedCoupon }})</span>
                            </span>
                            <div class="flex flex-col justify-end text-left sm:text-right w-full sm:w-auto">
                                <span v-if="cartStore.isFreeShipping" class="font-medium whitespace-nowrap">Frete Grátis
                                </span>
                                <span v-else class="font-medium whitespace-nowrap">- R$ {{
                                    cartStore.discountAmount.toFixed(2) }}</span>
                                <span v-if="!cartStore.isFreeShipping && cartStore.appliedCouponData?.porcentagem"
                                    class="text-xs font-light">({{ cartStore.appliedCouponData.valor }}%)</span>
                            </div>
                        </div>
                        <div v-if="cartStore.selectedShipping" class="flex justify-between items-center text-[#8c9e78]">
                            <span class="font-light italic flex items-center gap-1">
                                <Truck class="w-3.5 h-3.5" /> Frete ({{ cartStore.selectedShipping.name }})
                            </span>
                            <span class="font-medium">
                                <span v-if="cartStore.isFreeShipping">Grátis</span>
                                <span v-else>R$ {{ cartStore.shippingPrice.toFixed(2) }}</span>
                            </span>
                        </div>
                        <div class="border-t border-[#eaddcf] pt-2 mt-1 flex justify-between items-center">
                            <span class="text-lg font-medium italic text-[#3a5528]">Total a pagar:</span>
                            <span class="text-2xl font-medium text-[#0f2301]">R$ {{ cartStore.finalTotal.toFixed(2)
                            }}</span>
                        </div>
                    </div>
                </div>

                <!-- Right: Payment -->
                <div>
                    <h2 class="text-xl font-medium italic text-[#3a5528] mb-4">Pagamento</h2>

                    <!-- Validation warning -->
                    <div v-if="!canPay"
                        class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-4 text-sm text-yellow-800 font-light italic">
                        <p v-if="!cartStore.selectedShipping" class="flex items-center gap-2">
                            <TriangleAlert class="w-4 h-4 flex-shrink-0" /> Selecione uma opção de envio para continuar.
                        </p>
                        <p v-else-if="!isPickup && (!addressForm.address || !addressForm.number || !addressForm.neighborhood || !addressForm.city || !addressForm.state)"
                            class="flex items-center gap-2">
                            <TriangleAlert class="w-4 h-4 flex-shrink-0" /> Preencha todos os campos obrigatórios do
                            endereço.
                        </p>
                    </div>

                    <div class="bg-white/50 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-[#eaddcf] relative min-h-[400px]"
                        :class="{ 'opacity-50 pointer-events-none': !canPay }">
                        <div v-if="loadingBrick"
                            class="absolute inset-0 flex flex-col items-center justify-center bg-white/80 z-10 rounded-xl">
                            <LoaderCircle class="w-10 h-10 animate-spin text-[#3a5528] mb-4" />
                            <span class="text-[#8c9e78] font-light italic">Carregando formulário seguro...</span>
                        </div>

                        <div id="paymentBrick_container"></div>

                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { useToast } from 'vue-toastification'
import { LoaderCircle, Tag, MapPin, Truck, TriangleAlert } from 'lucide-vue-next'
import api from '@/api'

const cartStore = useCartStore()
const userStore = useUserStore()
const router = useRouter()
const toast = useToast()

const loadingBrick = ref(true)
const loadingCep = ref(false)
const isFinalizingOrder = ref(false)
let cardPaymentBrickController = null

// Address form
const addressForm = ref({
    cep: cartStore.shippingCep ? cartStore.shippingCep.replace(/(\d{5})(\d{3})/, '$1-$2') : '',
    cpf: '',
    phone: '',
    address: '',
    number: '',
    complement: '',
    neighborhood: '',
    city: '',
    state: '',
})

// Carrega telefone do usuário (se já tiver salvo)
const loadUserPhone = async () => {
    try {
        const res = await api.get('/me')
        if (res.data.phone) {
            addressForm.value.phone = res.data.phone
        }
    } catch (e) {
        // silently ignore
    }
}
loadUserPhone()

// Opção especial de retirada
const pickupOption = {
    id: 'pickup',
    name: 'Retirada',
    price: 0,
    delivery_time: null,
    company_name: 'Jardim Camburi — Vitória, ES',
    is_pickup: true
}

const isPickup = computed(() => cartStore.selectedShipping?.id === 'pickup')

const canPay = computed(() => {
    if (isPickup.value) return true  // pickup não precisa de endereço
    return cartStore.selectedShipping &&
        addressForm.value.address &&
        addressForm.value.number &&
        addressForm.value.neighborhood &&
        addressForm.value.city &&
        addressForm.value.state
})

const formatCpf = () => {
    let v = addressForm.value.cpf.replace(/\D/g, '')
    if (v.length > 3) v = v.slice(0, 3) + '.' + v.slice(3)
    if (v.length > 7) v = v.slice(0, 7) + '.' + v.slice(7)
    if (v.length > 11) v = v.slice(0, 11) + '-' + v.slice(11, 13)
    addressForm.value.cpf = v
}

const formatPhone = () => {
    let v = addressForm.value.phone.replace(/\D/g, '')
    if (v.length > 0) v = '(' + v
    if (v.length > 3) v = v.slice(0, 3) + ') ' + v.slice(3)
    if (v.length > 10) v = v.slice(0, 10) + '-' + v.slice(10, 14)
    addressForm.value.phone = v
}

const formatAddressCep = () => {
    let v = addressForm.value.cep.replace(/\D/g, '')
    if (v.length > 5) v = v.slice(0, 5) + '-' + v.slice(5, 8)
    addressForm.value.cep = v
}

const lookupCep = async () => {
    const cleanCep = addressForm.value.cep.replace(/\D/g, '')
    if (cleanCep.length < 8) return

    loadingCep.value = true
    try {
        let success = false
        // Try BrasilAPI first
        try {
            const res = await fetch(`https://brasilapi.com.br/api/cep/v1/${cleanCep}`)
            if (res.ok) {
                const data = await res.json()
                addressForm.value.address = data.street || ''
                addressForm.value.neighborhood = data.neighborhood || ''
                addressForm.value.city = data.city || ''
                addressForm.value.state = data.state || ''
                success = true
            }
        } catch (e) {
            console.warn("BrasilAPI falhou, tentando ViaCEP...")
        }

        if (!success) {
            // Fallback to ViaCEP
            const res = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`)
            const data = await res.json()
            if (!data.erro) {
                addressForm.value.address = data.logradouro || ''
                addressForm.value.neighborhood = data.bairro || ''
                addressForm.value.city = data.localidade || ''
                addressForm.value.state = data.uf || ''
            } else {
                toast.error('CEP não encontrado.')
            }
        }
    } catch (err) {
        toast.error('Erro ao buscar CEP.')
    } finally {
        loadingCep.value = false
    }

    // Also calculate shipping if not already done
    if (cartStore.shippingOptions.length === 0) {
        await cartStore.calculateShipping(cleanCep)
    }
}

const handleCalcShipping = async () => {
    const cleanCep = addressForm.value.cep.replace(/\D/g, '')
    await cartStore.calculateShipping(cleanCep)
}

// If shipping was already calculated from cart, auto-fill CEP and lookup address
onMounted(async () => {
    if (cartStore.items.length === 0) {
        router.push('/cart')
        return
    }

    // Auto-fill from stored CEP
    if (cartStore.shippingCep && !addressForm.value.address) {
        addressForm.value.cep = cartStore.shippingCep.replace(/(\d{5})(\d{3})/, '$1-$2')
        await lookupCep()
    }

    await initPaymentBrick()
})

// Voltar pro carrinho se o usuário remover o último item estando na página de checkout
watch(() => cartStore.items.length, (newLength) => {
    if (newLength === 0 && !isFinalizingOrder.value) {
        router.push('/cart')
    }
})

// Re-init brick when total changes (shipping selected)
watch(() => cartStore.finalTotal, async (newVal, oldVal) => {
    if (newVal !== oldVal && cardPaymentBrickController) {
        cardPaymentBrickController.unmount()
        cardPaymentBrickController = null
        loadingBrick.value = true
        await initPaymentBrick()
    }
})

async function initPaymentBrick() {
    try {
        const { loadMercadoPago } = await import('@mercadopago/sdk-js')
        await loadMercadoPago()

        const mp = new window.MercadoPago(import.meta.env.VITE_MP_PUBLIC_KEY, {
            locale: 'pt-BR'
        })

        const bricksBuilder = mp.bricks()

        const renderPaymentBrick = async (bricksBuilder) => {
            const settings = {
                initialization: {
                    amount: cartStore.finalTotal,
                    preferenceId: null,
                },
                customization: {
                    paymentMethods: {
                        creditCard: "all",
                        debitCard: "all",
                        bankTransfer: "all"
                    },
                    visual: {
                        style: {
                            theme: "default",
                            customVariables: {
                                formBackgroundColor: "#ffffff",
                                baseColor: "#0f2301",
                                baseColorFirstVariant: "#4a6336",
                                baseColorSecondVariant: "#3b502b",
                                primaryColor: "#0f2301",
                                outlinePrimaryColor: "#0f2301",
                                buttonTextColor: "#fffdf2",
                            }
                        }
                    }
                },
                callbacks: {
                    onReady: () => {
                        loadingBrick.value = false
                    },
                    onSubmit: async ({ selectedPaymentMethod, formData }) => {
                        console.log("🔥 BRICK ONSUBMIT TRIGERRED! 🔥")
                        console.log("Selected Method:", selectedPaymentMethod)

                        return new Promise((resolve, reject) => {
                            if (cartStore.appliedCoupon) {
                                formData.coupon_code = cartStore.appliedCoupon
                            }

                            // Add shipping data
                            if (cartStore.selectedShipping) {
                                formData.shipping_service_id = cartStore.selectedShipping.id
                                formData.shipping_cep = cartStore.shippingCep
                                formData.shipping_address = {
                                    address: addressForm.value.address,
                                    number: addressForm.value.number,
                                    complement: addressForm.value.complement,
                                    neighborhood: addressForm.value.neighborhood,
                                    city: addressForm.value.city,
                                    state: addressForm.value.state,
                                }
                            }

                            // CPF e telefone do cliente
                            if (addressForm.value.cpf) {
                                formData.customer_cpf = addressForm.value.cpf.replace(/\D/g, '')
                            }
                            if (addressForm.value.phone) {
                                formData.customer_phone = addressForm.value.phone
                            }

                            api.post('/cart/checkout', formData)
                                .then((response) => {
                                    resolve()
                                    const paymentData = response.data
                                    // Captura ANTES de limpar (clearShipping zera selectedShipping)
                                    const wasPickup = cartStore.selectedShipping?.id === 'pickup'
                                    isFinalizingOrder.value = true
                                    cartStore.clearCart2()
                                    cartStore.clearCoupon()
                                    cartStore.clearShipping()

                                    if (paymentData.status === 'approved' || paymentData.status === 'paid') {
                                        sessionStorage.setItem('is_pickup', wasPickup ? '1' : '0')
                                        sessionStorage.setItem('lastOrderId', paymentData.order_id)
                                        router.push('/checkout/sucesso')
                                    } else if (paymentData.status === 'pending' || paymentData.payment_data?.payment_method_id === 'pix') {
                                        sessionStorage.setItem('pendingPix', JSON.stringify(paymentData.payment_data))
                                        sessionStorage.setItem('lastOrderId', paymentData.order_id)
                                        sessionStorage.setItem('is_pickup', wasPickup ? '1' : '0')
                                        router.push('/checkout/pix')
                                    } else if (paymentData.status === 'rejected') {
                                        toast.error('Pagamento recusado. Tente outro cartão.')
                                    }
                                })
                                .catch((error) => {
                                    reject()
                                    console.error("Erro na API:", error)
                                    toast.error(error.response?.data?.message || 'Erro ao processar o pagamento')
                                })
                        })
                    },
                    onError: (error) => {
                        console.error(error)
                        toast.error("Erro ao carregar módulo de pagamento.")
                    },
                },
            }
            cardPaymentBrickController = await bricksBuilder.create(
                "payment",
                "paymentBrick_container",
                settings
            )
        }

        await renderPaymentBrick(bricksBuilder)

    } catch (error) {
        console.error("Erro initializing MP", error)
        loadingBrick.value = false
    }
}

onBeforeUnmount(() => {
    if (cardPaymentBrickController) {
        cardPaymentBrickController.unmount()
    }
})
</script>
