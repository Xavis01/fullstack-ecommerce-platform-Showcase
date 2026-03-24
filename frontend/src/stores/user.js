import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)

  const fetchUser = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      user.value = null
      return
    }

    try {
      const res = await api.get('/me')
      user.value = res.data

      // Sincronizar carrinho após login
      try {
        const { useCartStore } = await import('@/stores/cart')
        const cartStore = useCartStore()
        await cartStore.mergeCart()
      } catch (e) {
        console.error("Erro ao sincronizar carrinho", e)
      }

    } catch (err) {
      user.value = null
    }
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('token')
  }

  const is_logged = computed(() => !!user.value)  

  const is_admin = computed(() => user.value?.is_admin === true)

  return { user, fetchUser, logout, is_logged, is_admin }
})
