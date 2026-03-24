import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './index.css'
import Toast, { POSITION } from 'vue-toastification'
import 'vue-toastification/dist/index.css' 
import router from './router'
import api from './api'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'

const app = createApp(App)

app.use(Toast, {
    position: POSITION.TOP_RIGHT,
    timeout: 3000,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    icon: true,
    transition: 'Vue-Toastification__fade'
  })

app.use(createPinia())
app.use(router)

// Configurar interceptor global para expiração de sessão (401)
// Deve ser feito aqui para ter acesso às stores Pinia já inicializadas
let isHandling401 = false

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401 && !isHandling401) {
      isHandling401 = true
      const userStore = useUserStore()
      const uiStore = useUIStore()

      // Só abre o modal se o usuário já estava logado na sessão atual
      // (sessão expirada durante o uso). Se o 401 vier na inicialização
      // com um token antigo no localStorage, apenas limpa silenciosamente.
      const wasLoggedIn = !!userStore.user

      // Logout e limpar estado
      userStore.logout()

      if (wasLoggedIn) {
        // Se não estiver na home, redirecionar
        if (router.currentRoute.value.path !== '/') {
          router.push('/')
        }
        // Abrir modal de login apenas para sessão expirada durante o uso
        uiStore.openAuthModal()
      }

      // Reset do guard após 2s para permitir futuros 401 legítimos
      setTimeout(() => { isHandling401 = false }, 2000)
    }
    return Promise.reject(error)
  }
)

app.mount('#app')