<template>
  <div class="min-h-screen bg-[#fffdf2] mt-2 font-montserrat py-6 sm:py-8 px-4 sm:px-6 lg:px-8">

    <div class="max-w-5xl mx-auto">
      <h1
        class="text-2xl sm:text-3xl font-['Montserrat'] font-light text-[#3a5528] italic mb-6 sm:mb-8 border-b border-[#eaddcf] pb-3 sm:pb-4">
        Seu Carrinho
      </h1>

      <!-- Loading State -->
      <div v-if="cartStore.loading && cartStore.items.length === 0"
        class="flex flex-col items-center justify-center py-16 sm:py-20">
        <LoaderCircle class="w-8 h-8 sm:w-10 sm:h-10 animate-spin text-[#3a5528] mb-3 sm:mb-4" />
        <p class="text-[#8c9e78] font-light italic text-sm sm:text-base">Atualizando carrinho...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="cartStore.items.length === 0"
        class="text-center py-16 sm:py-20 px-4 bg-white/50 backdrop-blur-sm rounded-xl shadow-sm border border-[#eaddcf]">
        <ShoppingCart class="w-12 h-12 sm:w-16 sm:h-16 mx-auto text-[#8c9e78]/50 mb-3 sm:mb-4" />
        <h2 class="text-lg sm:text-xl font-medium text-[#3a5528] italic">Seu carrinho está vazio</h2>
        <p class="text-[#8c9e78] font-light text-sm sm:text-base mt-2 mb-6 sm:mb-8">Parece que você ainda não escolheu
          seus produtos favoritos.</p>
        <router-link to="/produtos"
          class="inline-block w-full sm:w-auto bg-[#0f2301] text-[#fffdf2] px-6 sm:px-8 py-3.5 sm:py-3 rounded-xl font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
          Começar a comprar
        </router-link>
      </div>

      <!-- Cart Items -->
      <div v-else class="flex flex-col lg:grid lg:grid-cols-3 gap-6 lg:gap-8">

        <!-- Lista de Itens -->
        <div class="lg:col-span-2 flex flex-col gap-3 sm:gap-4">
          <div v-for="item in cartStore.items" :key="item.variant_id"
            class="bg-white p-3 sm:p-4 rounded-xl shadow-sm border border-[#eaddcf] flex flex-row items-center gap-3 sm:gap-4 transition-all hover:bg-[#faf9f0] relative group block">

            <!-- Imagem do Produto -->
            <div
              class="w-20 h-20 sm:w-24 sm:h-24 bg-[#0f2301]/50 rounded-lg overflow-hidden flex-shrink-0 border border-[#0f2301]/20">
              <img v-if="item.image_url" :src="item.image_url" :alt="item.name" class="w-full h-full object-cover" />
              <span v-else
                class="flex items-center justify-center h-full text-[#8c9e78] text-[10px] sm:text-xs font-light">Sem
                img</span>
            </div>

            <div class="flex-1 min-w-0 flex flex-col justify-between py-0.5 sm:py-1 h-[5rem] sm:h-24">
              <div>
                <h3 class="font-medium text-[#3a5528] truncate text-sm sm:text-lg leading-tight">{{ item.name }}</h3>
                <p class="text-[11px] sm:text-sm text-[#8c9e78] font-light mt-0.5">Tamanho: <span
                    class="font-medium text-[#3a5528]">{{ item.size }}</span></p>
                <div class="font-medium text-[#6b8555] mt-0.5 sm:mt-1 text-xs sm:text-base">R$ {{ item.price.toFixed(2)
                  }}</div>
              </div>
            </div>

            <!-- Controles de Quantidade -->
            <div class="flex flex-col items-end justify-between py-0.5 sm:py-1 h-[5rem] sm:h-24 flex-shrink-0">
              <button @click="removeItem(item)"
                class="text-[#9a382d]/70 hover:text-[#9a382d] transition p-1.5 sm:p-1.5 -mr-1.5 sm:mr-0 rounded-lg hover:bg-red-50"
                title="Remover item" :disabled="cartStore.loading || processingItem === item.variant_id">
                <LoaderCircle v-if="processingItem === item.variant_id"
                  class="w-4 h-4 sm:w-5 sm:h-5 animate-spin text-[#9a382d]" />
                <Trash2 v-else class="w-4 h-4 sm:w-5 sm:h-5" />
              </button>

              <div
                class="flex items-center border border-[#eaddcf] rounded-lg bg-[#0f2301]/5 overflow-hidden shadow-sm h-8 sm:h-9">
                <button @click="updateQty(item, -1)"
                  class="px-2 sm:px-2.5 h-full hover:bg-[#0f2301]/10 transition text-[#3a5528] font-bold disabled:opacity-50 flex items-center justify-center w-7 sm:w-8"
                  :disabled="cartStore.loading || processingItem === item.variant_id">
                  <LoaderCircle v-if="processingItem === item.variant_id" class="w-3 h-3 animate-spin text-[#3a5528]" />
                  <span v-else>-</span>
                </button>
                <span class="text-[13px] sm:text-sm font-medium w-6 sm:w-8 text-center text-[#3a5528] select-none">{{
                  item.quantity }}</span>
                <button @click="updateQty(item, 1)"
                  class="px-2 sm:px-2.5 h-full hover:bg-[#0f2301]/10 transition text-[#3a5528] font-bold disabled:opacity-50 flex items-center justify-center w-7 sm:w-8"
                  :disabled="cartStore.loading || processingItem === item.variant_id">
                  <LoaderCircle v-if="processingItem === item.variant_id" class="w-3 h-3 animate-spin text-[#3a5528]" />
                  <span v-else>+</span>
                </button>
              </div>

              <div class="font-medium text-[#3a5528] text-sm sm:text-lg">R$ {{ (item.price * item.quantity).toFixed(2)
                }}</div>
            </div>

          </div>

          <!-- Botão Limpar Carrinho -->
          <div
            class="flex flex-col-reverse sm:flex-row justify-between items-center sm:pt-4 sm:border-t border-[#eaddcf] mt-2 sm:mt-4 gap-4 sm:gap-0">
            <router-link to="/produtos"
              class="text-xs sm:text-sm font-light italic text-[#8c9e78] hover:text-[#3a5528] transition-colors flex items-center justify-center gap-1 w-full sm:w-auto p-2 sm:p-0">
              <ChevronLeft class="w-4 h-4" /> Continuar comprando
            </router-link>
            <button @click="showClearModal = true"
              class="text-[#9a382d] hover:bg-red-50 text-xs sm:text-sm font-light italic flex items-center justify-center gap-2 border border-[#9a382d]/40 rounded-lg transition px-4 py-2.5 sm:py-2 w-full sm:w-auto">
              <Trash2 class="w-3.5 h-3.5 sm:w-4 sm:h-4" /> Esvaziar carrinho
            </button>
          </div>
        </div>

        <!-- Resumo do Pedido -->
        <div class="lg:col-span-1 mt-2 lg:mt-0">
          <div
            class="bg-white/50 backdrop-blur-sm p-4 sm:p-6 rounded-xl shadow-sm border border-[#eaddcf] lg:sticky lg:top-4">
            <h3 class="text-base sm:text-lg font-medium italic text-[#3a5528] mb-3 sm:mb-4">Resumo do Pedido</h3>

            <div class="flex flex-col gap-2.5 sm:gap-3 text-sm border-b border-[#eaddcf] pb-3 sm:pb-4 mb-3 sm:mb-4">
              <div class="flex justify-between items-center text-[#8c9e78] font-light text-xs sm:text-sm">
                <span>Subtotal ({{ cartStore.count }} itens)</span>
                <span class="font-medium text-[#3a5528]">R$ {{ cartStore.total.toFixed(2) }}</span>
              </div>

              <!-- Cupom aplicado -->
              <div v-if="cartStore.appliedCoupon"
                class="flex flex-row justify-between text-[#3a5528] font-light items-center gap-2 group relative min-h-[36px] sm:min-h-[40px] px-2 py-1 -mx-2 rounded hover:bg-[#0f2301]/5 transition-colors">

                <div class="flex items-center gap-1.5 sm:gap-2 relative cursor-help flex-1 min-w-0 group/tooltip">
                  <LoaderCircle v-if="cartStore.validatingCoupon"
                    class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0 animate-spin" />
                  <Tag v-else class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                  <div class="flex flex-row items-center min-w-0">
                    <span class="truncate text-xs sm:text-sm mr-1">Cupom</span>
                    <span class="text-[10px] sm:text-xs truncate font-medium">({{ cartStore.appliedCoupon }})</span>
                  </div>

                  <!-- Tooltip Customizado -->
                  <div
                    class="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-max max-w-[250px] bg-[#0f2301] text-[#fffdf2] text-xs px-3 py-2 rounded-lg opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-300 z-[99] shadow-xl pointer-events-none text-center leading-relaxed">
                    {{ cartStore.appliedCouponData?.descricao || 'Cupom de Desconto' }}
                    <div
                      class="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-[6px] border-transparent border-t-[#0f2301]">
                    </div>
                  </div>
                </div>

                <div class="flex items-center justify-end gap-2 flex-shrink-0 ml-2">
                  <div
                    class="flex items-center gap-2 transform transition-transform duration-300 ease-in-out sm:group-hover:-translate-x-8">
                    <div class="flex flex-col items-end">
                      <span v-if="cartStore.isFreeShipping"
                        class="font-medium text-[#3a5528] whitespace-nowrap text-[11px] sm:text-sm">Frete Grátis</span>
                      <span v-else class="font-medium text-[#3a5528] whitespace-nowrap text-[11px] sm:text-sm">- R$ {{
                        cartStore.discountAmount.toFixed(2) }}</span>
                      <span v-if="!cartStore.isFreeShipping && cartStore.appliedCouponData?.porcentagem"
                        class="text-[9px] sm:text-xs font-light">({{ cartStore.appliedCouponData.valor }}%)</span>
                    </div>
                  </div>

                  <button @click="cartStore.clearCoupon()" title="Remover cupom"
                    class="sm:absolute sm:right-0 sm:top-1/2 sm:-translate-y-1/2 sm:translate-x-12 sm:opacity-0 sm:pointer-events-none group-hover:translate-x-0 group-hover:opacity-100 group-hover:pointer-events-auto text-red-500 hover:text-red-800 hover:bg-red-100/80 rounded-full transition-all duration-300 p-1 sm:p-1.5 shrink-0 flex items-center justify-center">
                    <X class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </button>
                </div>
              </div>

              <!-- Frete -->
              <div v-if="cartStore.selectedShipping"
                class="flex flex-row justify-between text-[#3a5528] font-light items-center gap-2 group relative min-h-[36px] sm:min-h-[40px] px-2 py-1 -mx-2 rounded hover:bg-[#0f2301]/5 transition-colors">
                <div class="flex items-center gap-1.5 sm:gap-2 flex-1 min-w-0">
                  <Truck class="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                  <div class="flex flex-row items-center min-w-0">
                    <span class="truncate text-xs sm:text-sm mr-1">Frete</span>
                    <span class="text-[10px] sm:text-xs truncate font-medium">({{ cartStore.selectedShipping.name
                      }})</span>
                  </div>
                </div>
                <div class="flex items-center justify-end gap-2 flex-shrink-0 ml-2">
                  <div
                    class="flex items-center gap-2 transform transition-transform duration-300 ease-in-out sm:group-hover:-translate-x-8">
                    <span class="font-medium text-[#3a5528] whitespace-nowrap text-[11px] sm:text-sm">
                      <span v-if="cartStore.isFreeShipping">Grátis</span>
                      <span v-else>R$ {{ cartStore.shippingPrice.toFixed(2) }}</span>
                    </span>
                  </div>
                  <button @click="clearCepAndShipping" title="Remover frete"
                    class="sm:absolute sm:right-0 sm:top-1/2 sm:-translate-y-1/2 sm:translate-x-12 sm:opacity-0 sm:pointer-events-none group-hover:translate-x-0 group-hover:opacity-100 group-hover:pointer-events-auto text-red-500 hover:text-red-800 hover:bg-red-100/80 rounded-full transition-all duration-300 p-1 sm:p-1.5 shrink-0 flex items-center justify-center">
                    <X class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </button>
                </div>
              </div>
              <div v-else class="flex justify-between items-center text-[#8c9e78] font-light text-xs sm:text-sm">
                <span>Frete</span>
                <span class="font-medium text-[#6b8555] text-[10px] sm:text-xs">Calcule abaixo</span>
              </div>
            </div>

            <!-- Calcular Frete -->
            <div class="mb-3 sm:mb-4">
              <label class="block text-[10px] sm:text-xs font-medium text-[#3a5528] mb-1.5 sm:mb-2 italic">Calcular
                Frete</label>
              <div class="flex flex-row gap-2">
                <div class="relative flex-1">
                  <input v-model="cepInput" type="tel" placeholder="00000-000"
                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 sm:py-2 px-3 pr-8 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm"
                    @input="formatCep" @keyup.enter="handleCalcShipping" maxlength="9" />
                  <button v-if="cartStore.shippingOptions.length > 0" @click="clearCepAndShipping"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-[#8c9e78] hover:text-red-500 transition-colors p-1">
                    <X class="w-3.5 h-3.5" />
                  </button>
                </div>
                <button @click="handleCalcShipping"
                  :disabled="cartStore.loadingShipping || cepInput.replace(/\D/g, '').length < 8"
                  class="bg-[#0f2301] text-[#fffdf2] px-4 py-2.5 sm:py-2 rounded-lg font-light text-sm hover:bg-[#3a5528] transition-all disabled:opacity-50 flex items-center justify-center gap-2 min-w-[90px]">
                  <LoaderCircle v-if="cartStore.loadingShipping" class="w-4 h-4 animate-spin" />
                  <span v-else>Calcular</span>
                </button>
              </div>
              <p v-if="cartStore.shippingError" class="mt-1.5 sm:mt-2 text-[10px] sm:text-xs text-[#9a382d] font-light">
                {{
                  cartStore.shippingError }}</p>
            </div>

            <div v-if="cartStore.shippingOptions.length > 0" class="flex flex-col space-y-2 mb-3 sm:mb-4">
              <button v-for="opt in cartStore.shippingOptions" :key="opt.id" @click="cartStore.selectShipping(opt)"
                class="w-full flex items-center justify-between py-2.5 sm:py-3 px-3 border rounded-lg transition-all text-left"
                :class="cartStore.selectedShipping?.id === opt.id
                  ? 'border-[#0f2301] bg-[#0f2301]/5 shadow-sm'
                  : 'border-[#eaddcf] hover:border-[#3a5528]/40 bg-[#faf9f0]'">
                <div class="flex items-center gap-2.5 sm:gap-3">
                  <Truck class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#3a5528] flex-shrink-0" />
                  <div>
                    <p class="text-[11px] sm:text-sm font-medium text-[#0f2301]">{{ opt.name }}</p>
                    <p class="text-[10px] sm:text-xs text-[#8c9e78] font-light">{{ opt.delivery_time }} dias úteis</p>
                  </div>
                </div>
                <span class="font-medium text-[#0f2301] text-[11px] sm:text-sm whitespace-nowrap ml-2">
                  <span v-if="cartStore.isFreeShipping">R$ 0,00</span>
                  <span v-else>R$ {{ opt.price.toFixed(2) }}</span>
                </span>
              </button>

              <!-- Retirada - sempre disponível -->
              <button @click="cartStore.selectShipping(pickupOption)"
                class="w-full flex items-center justify-between py-2.5 sm:py-3 px-3 border rounded-lg transition-all text-left"
                :class="cartStore.selectedShipping?.id === 'pickup'
                  ? 'border-[#0f2301] bg-[#0f2301]/5 shadow-sm'
                  : 'border-[#eaddcf] hover:border-[#3a5528]/40 bg-[#faf9f0]'">
                <div class="flex items-center gap-2.5 sm:gap-3">
                  <MapPin class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#3a5528] flex-shrink-0" />
                  <div>
                    <p class="text-[11px] sm:text-sm font-medium text-[#0f2301]">Retirada</p>
                    <p class="text-[10px] sm:text-xs text-[#8c9e78] font-light">Jardim Camburi - Vitória, ES</p>
                  </div>
                </div>
                <span class="font-medium text-[#3a5528] text-[11px] sm:text-sm whitespace-nowrap ml-2">Grátis</span>
              </button>
            </div>

            <!-- Input de Cupom -->
            <div v-if="!cartStore.appliedCoupon" class="mb-3 sm:mb-4">
              <div class="flex flex-row gap-2">
                <div class="relative flex-1">
                  <input v-model="couponInput" type="text" placeholder="Código do cupom"
                    class="w-full bg-transparent border border-[#3a5528]/30 rounded-lg py-2.5 sm:py-2 px-3 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#3a5528] transition-colors font-light text-sm"
                    @keyup.enter="applyCoupon" />
                </div>
                <button @click="applyCoupon" :disabled="cartStore.validatingCoupon || !couponInput"
                  class="bg-[#0f2301] text-[#fffdf2] px-4 py-2.5 sm:py-2 rounded-lg font-light text-sm hover:bg-[#eaddcf] hover:text-[#0f2301] transition-all disabled:hover:bg-[#0f2301] disabled:hover:text-[#fffdf2] disabled:opacity-50 flex items-center justify-center min-w-[90px]">
                  <LoaderCircle v-if="cartStore.validatingCoupon" class="w-4 h-4 animate-spin" />
                  <span v-else>Aplicar</span>
                </button>
              </div>
            </div>

            <div class="flex justify-between items-end mb-5 sm:mb-6 border-t border-[#eaddcf] pt-3 sm:pt-4">
              <span class="text-base sm:text-lg font-medium italic text-[#3a5528]">Total</span>
              <div class="text-right">
                <span class="text-xl sm:text-2xl font-medium text-[#0f2301]">R$ {{ cartStore.finalTotal.toFixed(2)
                  }}</span>
                <p class="text-[10px] sm:text-xs text-[#8c9e78] font-light mt-0.5 sm:mt-1">ou em até 10x de R$ {{
                  (cartStore.finalTotal /
                    10).toFixed(2) }}</p>
              </div>
            </div>

            <button @click="handleCheckout"
              class="w-full bg-[#0f2301] text-[#fffdf2] py-3.5 sm:py-4 rounded-xl font-light italic tracking-wide text-base sm:text-lg hover:bg-[#3a5528] transition-all shadow-sm flex justify-center items-center gap-2">
              Finalizar Compra
            </button>

            <!-- Info Segurança -->
            <div class="mt-4 sm:mt-6 flex justify-center items-center gap-2 sm:gap-3 text-[#8c9e78]">
              <CreditCard class="w-4 h-4 sm:w-5 sm:h-5" />
              <span class="text-[11px] sm:text-xs flex items-center font-light">Transação Segura</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Modal de Confirmação -->
    <ConfirmClearCartModal :visible="showClearModal" :loading="cartStore.loading" @close="showClearModal = false"
      @confirm="handleClearCart" />

  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'
import { LoaderCircle, ShoppingCart, Trash2, Lock, CreditCard, ChevronLeft, Tag, X, Truck, MapPin } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import ConfirmClearCartModal from '@/components/cart/ConfirmClearCartModal.vue'

const cartStore = useCartStore()
const userStore = useUserStore()
const uiStore = useUIStore()
const router = useRouter()
const toast = useToast()

const showClearModal = ref(false)
const processingItem = ref(null)
const couponInput = ref('')
const cepInput = ref(cartStore.shippingCep ? cartStore.shippingCep.replace(/(\d{5})(\d{3})/, '$1-$2') : '')

// Opção especial de retirada (sem cálculo de frete)
const pickupOption = {
  id: 'pickup',
  name: 'Retirada',
  price: 0,
  delivery_time: null,
  company_name: 'Jardim Camburi — Vitória, ES',
  is_pickup: true
}

const formatCep = () => {
  let v = cepInput.value.replace(/\D/g, '')
  if (v.length > 5) v = v.slice(0, 5) + '-' + v.slice(5, 8)
  cepInput.value = v
}

const handleCalcShipping = async () => {
  await cartStore.calculateShipping(cepInput.value)
}

const clearCepAndShipping = () => {
  cepInput.value = ''
  cartStore.clearShipping()
}

const applyCoupon = async () => {
  if (!couponInput.value) return;
  const success = await cartStore.validateCoupon(couponInput.value)
  if (success) {
    couponInput.value = ''
  }
}

onMounted(() => {
  cartStore.fetchCart()
})

const updateQty = async (item, change) => {
  if (processingItem.value === item.variant_id) return

  const newQty = item.quantity + change
  if (newQty < 1) return

  processingItem.value = item.variant_id
  try {
    await cartStore.updateQuantity(item, newQty)
  } finally {
    processingItem.value = null
  }
}

const removeItem = async (item) => {
  if (processingItem.value === item.variant_id) return
  processingItem.value = item.variant_id
  try {
    await cartStore.removeItem(item)
  } finally {
    processingItem.value = null
  }
}

const handleClearCart = async () => {
  try {
    await cartStore.clearCart()
    showClearModal.value = false
  } catch (e) {
    console.error(e)
  }
}

const handleCheckout = () => {
  if (userStore.is_logged) {
    router.push('/checkout')
  } else {
    toast.info("Faça login para finalizar sua compra!")
    uiStore.openAuthModal()
  }
}

</script>