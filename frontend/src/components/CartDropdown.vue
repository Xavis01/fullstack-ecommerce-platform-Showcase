<script setup>
import { computed, ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { Trash2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const cartStore = useCartStore()
const userStore = useUserStore()
const router = useRouter()
const isLoggedIn = computed(() => userStore.is_logged)

// Track items being deleted for visual feedback
const deletingItems = ref(new Set())

const cartItems = computed(() => cartStore.items)
const subtotal = computed(() => cartStore.total)

// Currency formatter
const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value)
}

const handleRemoveItem = async (item) => {
    // Prevent multiple clicks
    if (deletingItems.value.has(item.variant_id)) return

    // Add to deleting set
    deletingItems.value.add(item.variant_id)

    try {
        await cartStore.removeItem(item)
    } finally {
        deletingItems.value.delete(item.variant_id)
    }
}

const goToCart = () => {
    router.push('/cart')
}

const goToCheckout = () => {
    router.push('/checkout')
}
</script>

<template>
    <div class="w-80 bg-[#233036] shadow-xl z-50 rounded-sm overflow-hidden  border-[#233036/50]">

        <div v-if="cartItems.length === 0" class="p-6 text-center text-gray-400 italic font-light text-sm">
            Seu carrinho está vazio.
        </div>

        <div v-else>
            <!-- Scrollable List -->
            <div class="max-h-[300px] overflow-y-auto px-4 py-4 space-y-4 custom-scrollbar">
                <div v-for="item in cartItems" :key="item.variant_id"
                    class="flex gap-3 group relative transition-all duration-300"
                    :class="{ 'opacity-50 grayscale pointer-events-none': deletingItems.has(item.variant_id) }">

                    <!-- Image -->
                    <div class="w-16 h-16 flex-shrink-0 bg-gray-800 rounded-sm overflow-hidden">
                        <img :src="item.image_url" :alt="item.name" class="w-full h-full object-cover">
                    </div>

                    <!-- Details -->
                    <div class="flex-1 min-w-0">
                        <div class="flex justify-between items-start">
                            <h4 class="text-[#ffffff] text-sm font-medium truncate pr-2">{{ item.name }}</h4>

                            <button @click="handleRemoveItem(item)"
                                class="text-gray-400 hover:text-white transition-colors"
                                :disabled="deletingItems.has(item.variant_id)">
                                <Trash2 :size="14" />
                            </button>
                        </div>

                        <p class="text-[#ffffff] text-xs mb-1">{{ item.size }}</p>

                        <div class="text-white text-xs font-light">
                            {{ item.quantity }} × {{ formatCurrency(item.price) }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="p-4 bg-[#1f2b30] border-t border-gray-700">
                <div class="flex justify-between items-center mb-4 text-white">
                    <span class="text-xs font-bold uppercase tracking-wider">Subtotal:</span>
                    <span class="text-sm font-bold">{{ formatCurrency(subtotal) }}</span>
                </div>

                <div class="grid gap-3" :class="isLoggedIn ? 'grid-cols-2' : 'grid-cols-1'">
                    <button @click="goToCart"
                        class="bg-[#0f2301] hover:bg-[#4a6336] text-white text-[10px] font-bold py-3 uppercase tracking-wider rounded-sm transition-colors text-center">
                        Ver Carrinho
                    </button>
                    <button v-if="isLoggedIn" @click="goToCheckout"
                        class="bg-[#0f2301] hover:bg-[#4a6336] text-white text-[10px] font-bold py-3 uppercase tracking-wider rounded-sm transition-colors text-center">
                        Finalizar Compra
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: #1f2b30;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #0f2301;
    border-radius: 2px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #4a6336;
}
</style>
