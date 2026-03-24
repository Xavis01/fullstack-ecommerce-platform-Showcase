import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { useToast } from 'vue-toastification'

export const useCartStore = defineStore('cart', () => {
    const items = ref([])
    const loading = ref(false)
    const appliedCoupon = ref(localStorage.getItem('saved_coupon_code') || null)
    const appliedCouponData = ref(JSON.parse(localStorage.getItem('saved_coupon_data') || 'null'))
    const discountAmount = ref(0)
    const validatingCoupon = ref(false)
    const userStore = useUserStore()
    const toast = useToast()

    // Shipping state
    const shippingCep = ref(sessionStorage.getItem('shipping_cep') || '')
    const shippingOptions = ref([])
    const selectedShipping = ref(JSON.parse(sessionStorage.getItem('selected_shipping') || 'null'))
    const loadingShipping = ref(false)
    const shippingError = ref('')

    // Carrega itens do localStorage ao iniciar
    const initCart = () => {
        const storedItems = localStorage.getItem('guest_cart')
        if (storedItems) {
            items.value = JSON.parse(storedItems)
        }
    }

    // Salva itens no localStorage (apenas se deslogado)
    const saveToLocalStorage = () => {
        if (!userStore.is_logged) {
            localStorage.setItem('guest_cart', JSON.stringify(items.value))
        }
    }

    // Busca carrinho (API ou Local)
    const fetchCart = async () => {
        loading.value = true
        if (userStore.is_logged) {
            try {
                const res = await api.get('/cart/view')
                items.value = res.data.cart.map(item => ({
                    ...item,
                    variant_id: item.variant_id
                }))
            } catch (err) {
                console.error('Erro ao buscar carrinho:', err)
            }
        } else {
            initCart()
        }
        
        if (appliedCoupon.value && items.value.length > 0 && discountAmount.value === 0) {
            await validateCoupon(appliedCoupon.value)
        }
        
        loading.value = false
    }

    // Adiciona Item
    const addItem = async (product, variantId, size, quantity) => {
        loading.value = true
        if (userStore.is_logged) {
            try {
                await api.post('/cart/add', {
                    product_id: product.id,
                    size: size,
                    quantity: quantity
                })
                await fetchCart()
            } catch (err) {
                console.error(err)
                toast.error('Erro ao adicionar produto.')
            }
        } else {
            const existingItem = items.value.find(item => item.variant_id === variantId)
            
            if (existingItem) {
                existingItem.quantity += quantity
                existingItem.subtotal = existingItem.quantity * existingItem.price
            } else {
                items.value.push({
                    product_id: product.id,
                    variant_id: variantId,
                    name: product.name,
                    size: size,
                    price: parseFloat(product.price),
                    quantity: quantity,
                    image_url: product.image_url, 
                    subtotal: parseFloat(product.price) * quantity
                })
            }
            saveToLocalStorage()
        }
        loading.value = false
    }

    // Atualiza Quantidade (+/-)
    const updateQuantity = async (item, newQuantity) => {
        if (newQuantity < 1) return

        loading.value = true
        if (userStore.is_logged) {
            try {
                const diff = newQuantity - item.quantity
                if (diff > 0) {
                     await api.post('/cart/add', {
                        product_id: item.product_id,
                        size: item.size,
                        quantity: diff
                    })
                } else if (diff < 0) {
                     await api.put('/cart/update', {
                        product_id: item.product_id,
                        size: item.size,
                        quantity: newQuantity
                     })
                }
                await fetchCart()
            } catch (err) {
                console.error(err)
                toast.error('Erro ao atualizar quantidade.')
            }
        } else {
            const localItem = items.value.find(i => i.variant_id === item.variant_id)
            if (localItem) {
                localItem.quantity = newQuantity
                localItem.subtotal = localItem.price * newQuantity
                saveToLocalStorage()
            }
        }
        loading.value = false
    }

    // Remove Item
    const removeItem = async (item) => {
        loading.value = true
        if (userStore.is_logged) {
            try {
                await api.delete('/cart/remove', {
                    data: {
                        product_id: item.product_id,
                        size: item.size,
                    }
                })
                await fetchCart()
                toast.success('Item removido.')
            } catch (err) {
                console.error(err)
                toast.error('Erro ao remover item.')
            }
        } else {
            items.value = items.value.filter(i => i.variant_id !== item.variant_id)
            saveToLocalStorage()
            toast.success('Item removido.')
        }
        loading.value = false
    }

    // Limpa Carrinho
    const clearCart = async () => {
        loading.value = true
        if (userStore.is_logged) {
            try {
                await api.delete('/cart/clear')
                items.value = []
                toast.success('Carrinho limpo')
            } catch (err) {
                console.error(err)
            }
        } else {
            items.value = []
            localStorage.removeItem('guest_cart')
            toast.success('Carrinho limpo')
        }
        clearShipping()
        loading.value = false
    }

    const clearCart2 = async () => {
        loading.value = true
        if (userStore.is_logged) {
            try {
                await api.delete('/cart/clear')
                items.value = []
                toast.success('Código PIX gerado!')
            } catch (err) {
                console.error(err)
            }
        } else {
            items.value = []
            localStorage.removeItem('guest_cart')
            toast.success('Carrinho limpo')
        }
        clearShipping()
        loading.value = false
    }

    // Mesclar Carrinho (Chamado ao logar)
    const mergeCart = async () => {
        const guestItems = JSON.parse(localStorage.getItem('guest_cart') || '[]')
        if (guestItems.length > 0) {
            try {
                await api.post('/cart/merge', { items: guestItems })
                localStorage.removeItem('guest_cart')
                await fetchCart()
                // toast.success('Seus itens foram salvos no carrinho!')
            } catch (err) {
                console.error('Erro ao mesclar carrinho:', err)
                toast.error('Erro ao sincronizar carrinho.')
            }
        } else {
            await fetchCart()
        }
    }

    // Valida Cupom
    const validateCoupon = async (couponCode) => {
        if (!couponCode) {
            appliedCoupon.value = null
            appliedCouponData.value = null
            discountAmount.value = 0
            return false
        }
        
        validatingCoupon.value = true
        try {
            const res = await api.post('/public-coupons/validate', {
                coupon_code: couponCode,
                cart_items: items.value
            })
            
            if (res.data.valid) {
                 appliedCoupon.value = res.data.coupon_code
                 appliedCouponData.value = {
                     porcentagem: res.data.porcentagem,
                     valor: res.data.valor,
                     descricao: res.data.descricao,
                     frete_gratis: res.data.frete_gratis
                 }
                 discountAmount.value = res.data.discount_amount
                 localStorage.setItem('saved_coupon_code', res.data.coupon_code)
                 localStorage.setItem('saved_coupon_data', JSON.stringify(appliedCouponData.value))
                 const msg = res.data.frete_gratis && res.data.discount_amount === 0
                     ? (res.data.message || 'Cupom de frete grátis aplicado!')
                     : (res.data.message || 'Cupom aplicado!')
                 toast.success(msg)
                 return true
            }
        } catch (err) {
            console.error(err)
            appliedCoupon.value = null
            appliedCouponData.value = null
            discountAmount.value = 0
            toast.error(err.response?.data?.message || 'Cupom inválido ou não se aplica aos itens.')
            return false
        } finally {
            validatingCoupon.value = false
        }
    }

    const clearCoupon = () => {
         appliedCoupon.value = null
         appliedCouponData.value = null
         discountAmount.value = 0
         localStorage.removeItem('saved_coupon_code')
         localStorage.removeItem('saved_coupon_data')
    }

    // ====== Shipping Methods ======
    const calculateShipping = async (cep) => {
        const cleanCep = cep.replace(/\D/g, '')
        if (cleanCep.length < 8 || items.value.length === 0) return

        loadingShipping.value = true
        shippingError.value = ''
        shippingOptions.value = []
        selectedShipping.value = null
        sessionStorage.removeItem('selected_shipping')

        try {
            const products = items.value.map(item => ({
                product_id: item.product_id,
                quantity: item.quantity
            }))
            const res = await api.post('/shipping/calculate', {
                cep: cleanCep,
                products
            })
            shippingOptions.value = res.data.shipping_options
            shippingCep.value = cleanCep
            sessionStorage.setItem('shipping_cep', cleanCep)
        } catch (err) {
            shippingError.value = err.response?.data?.error || 'Erro ao calcular frete.'
        } finally {
            loadingShipping.value = false
        }
    }

    const selectShipping = (option) => {
        selectedShipping.value = option
        sessionStorage.setItem('selected_shipping', JSON.stringify(option))
    }

    const clearShipping = () => {
        shippingCep.value = ''
        shippingOptions.value = []
        selectedShipping.value = null
        shippingError.value = ''
        sessionStorage.removeItem('shipping_cep')
        sessionStorage.removeItem('selected_shipping')
    }

    const total = computed(() => {
        return items.value.reduce((acc, item) => acc + (item.price * item.quantity), 0)
    })

    const isFreeShipping = computed(() => {
        return !!appliedCouponData.value?.frete_gratis
    })

    const shippingPrice = computed(() => {
        if (isFreeShipping.value) return 0
        return selectedShipping.value ? selectedShipping.value.price : 0
    })

    const finalTotal = computed(() => {
        const t = total.value - discountAmount.value + shippingPrice.value
        return t > 0 ? t : 0
    })

    const count = computed(() => {
        return items.value.reduce((acc, item) => acc + item.quantity, 0)
    })

    return {
        items,
        loading,
        total,
        count,
        appliedCoupon,
        appliedCouponData,
        discountAmount,
        finalTotal,
        validatingCoupon,
        isFreeShipping,
        shippingCep,
        shippingOptions,
        selectedShipping,
        loadingShipping,
        shippingError,
        shippingPrice,
        fetchCart,
        addItem,
        updateQuantity,
        removeItem,
        clearCart,
        clearCart2,
        mergeCart,
        validateCoupon,
        clearCoupon,
        calculateShipping,
        selectShipping,
        clearShipping,
    }
})
