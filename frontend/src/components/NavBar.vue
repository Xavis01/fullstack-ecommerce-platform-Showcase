<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'
import { useCartStore } from '@/stores/cart'
import { useEditModeStore } from '@/stores/editMode'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import AuthModal from '@/components/AuthModal.vue'
import CartDropdown from '@/components/CartDropdown.vue'
import { useRouter, useRoute } from 'vue-router'
import { ShoppingBag, User, Menu, UserStar, Home, Pencil } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const uiStore = useUIStore()
const cartStore = useCartStore()
const editModeStore = useEditModeStore()
const toast = useToast()

const userName = computed(() => userStore.user?.name || null)
const isAdmin = computed(() => userStore.is_admin)

const showAdminSidebar = ref(false)
const showUserSidebar = ref(false)
const showAuthModal = ref(false)
const isCartHovered = ref(false)

// UI Animation States
const showLinks = computed(() => uiStore.introStage >= 1)
const showBanner = computed(() => uiStore.introStage >= 2)
const showBorder = computed(() => uiStore.introStage >= 4)
const showLogo = computed(() => !uiStore.isSplashActive || uiStore.introStage >= 4)

// Scroll hide logic
const scrolled = ref(false)
const isHomePage = computed(() => route.path === '/')
const isArchivePage = computed(() => route.path === '/archive')
const isProductsPage = computed(() => route.path === '/produtos')
const isDarkTheme = computed(() => isHomePage.value || isArchivePage.value)

// Edit mode: só visível em home e produtos, e apenas para admins
const showEditModeBtn = computed(() => isAdmin.value && (isHomePage.value || isProductsPage.value))

// Logo source: white on dark theme pages, dark on other pages
const logoSrc = computed(() => isDarkTheme.value ? '/ROCCABehe.png' : '/ROCCAVerde.png')
const showNavLogo = computed(() => !isArchivePage.value)

function onScroll() {
  scrolled.value = window.scrollY > 60
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

// Helper for transitions
const transitionClass = "transition-all duration-700 ease-out"

function logout() {
  editModeStore.disableEditMode()
  userStore.logout()
  toast.info('Você saiu da sua conta.')
  router.push('/')
}

async function goToDestaques() {
  if (!isHomePage.value) {
    await router.push('/')
    // aguarda o DOM da home carregar antes de rolar
    await new Promise(resolve => setTimeout(resolve, 400))
  }
  const el = document.getElementById('destaques')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div>
    <!-- Faixa de cupom (sempre fixa) -->
    <div
      class="fixed top-0 left-0 w-full bg-[#861e1f] text-white text-center py-1.5 md:py-2 text-[10px] md:text-xs font-light tracking-wide z-[105] transition-all duration-1000 ease-out"
      :style="showBanner ? 'opacity: 1; transform: translateY(0)' : 'opacity: 0; transform: translateY(-100%)'">
      Cupom de primeira compra: <span class="italic">FAMIGLIA10</span>
    </div>

    <!-- Gradiente preto abaixo do banner (só na home, some ao rolar) -->
    <div v-if="isHomePage" class="gradient-overlay" :class="{ 'gradient-hidden': scrolled }"></div>

    <!-- Navbar principal -->
    <nav
      class="fixed top-7 md:top-8 left-0 w-full flex justify-between items-center px-4 md:px-8 py-3 md:py-4 bg-transparent z-[105] transition-all duration-500"
      :class="[
        showBorder ? 'border-[#0f2301]' : 'border-transparent',
        scrolled ? 'opacity-0 pointer-events-none -translate-y-2' : 'opacity-100 translate-y-0'
      ]">

      <!-- Lado esquerdo -->
      <div class="flex gap-3 md:gap-14 items-center">
        <!-- Hamburger mobile (sempre visível no mobile) -->
        <button @click="isAdmin ? showAdminSidebar = true : showUserSidebar = true"
          class="md:hidden hover:opacity-70 transition-opacity" :class="[
            transitionClass,
            showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            isDarkTheme ? 'text-[#fffdf2]' : 'text-[#0f2301]'
          ]" style="transition-delay: 100ms">
          <Menu :size="22" :stroke-width="1.5" />
        </button>

        <!-- SHOP -->
        <router-link to="/produtos" class="nav-link relative text-xs font-light tracking-wider uppercase italic" :class="[
          transitionClass,
          showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
          isDarkTheme ? 'text-[#fffdf2] hover:text-[#eaddcf]' : 'text-[#0f2301] hover:text-[#324424]'
        ]" style="transition-delay: 600ms">
          SHOP
        </router-link>

        <!-- ARCHIVE (hidden mobile) -->
        <router-link to="/archive"
          class="hidden md:block nav-link relative text-xs font-light tracking-wider uppercase italic" :class="[
            transitionClass,
            showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            isDarkTheme ? 'text-[#fffdf2] hover:text-[#eaddcf]' : 'text-[#0f2301] hover:text-[#324424]'
          ]" style="transition-delay: 400ms">
          ARCHIVE
        </router-link>

        <!-- DESTAQUES (hidden mobile) -->
        <button @click="goToDestaques"
          class="hidden md:block nav-link relative text-xs font-light tracking-wider uppercase italic" :class="[
            transitionClass,
            showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            isDarkTheme ? 'text-[#fffdf2] hover:text-[#eaddcf]' : 'text-[#0f2301] hover:text-[#324424]'
          ]" style="transition-delay: 200ms">
          DESTAQUES
        </button>
      </div>

      <!-- Logo ROCCA no centro -->
      <router-link to="/" class="absolute left-1/2 transform -translate-x-1/2 transition-all duration-500"
        :class="(showLogo && showNavLogo) ? 'opacity-100' : 'opacity-0 pointer-events-none'">
        <img id="navbar-logo" :src="logoSrc" alt="ROCCA" class="h-8 md:h-11" />
      </router-link>

      <!-- Ícones da direita -->
      <div class="flex gap-4 md:gap-6 items-center">

        <!-- Home Page (Only on Archive) -->
        <router-link v-if="isArchivePage" to="/" class="block relative py-2" :class="[
          transitionClass,
          showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
          'text-[#fffdf2]'
        ]" style="transition-delay: 0ms">
          <Home :size="20" :stroke-width="2" class="md:!w-[22px] md:!h-[22px] hover:opacity-70 transition-opacity" />
        </router-link>

        <!-- Edit Mode Button (Admin only, Home & Products) -->
        <button v-if="showEditModeBtn" @click="editModeStore.toggleEditMode()"
          :title="editModeStore.isEditMode ? 'Sair do Modo Edição' : 'Ativar Modo Edição'"
          class="relative py-2 transition-all duration-300" :class="[
            transitionClass,
            showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            editModeStore.isEditMode
              ? 'text-[#861e1f]'
              : isDarkTheme ? 'text-[#fffdf2]' : 'text-[#0f2301]'
          ]" style="transition-delay: 50ms">
          <Pencil :size="20" :stroke-width="2" class="md:!w-[22px] md:!h-[22px] hover:opacity-70 transition-opacity" />
          <!-- Dot indicador quando ativo -->
          <span v-if="editModeStore.isEditMode"
            class="absolute top-0 right-0 w-2 h-2 bg-[#861e1f] rounded-full animate-pulse"></span>
        </button>

        <!-- Cart Section -->
        <div class="relative group" @mouseenter="isCartHovered = true" @mouseleave="isCartHovered = false">
          <router-link to="/cart" class="block relative py-2" :class="[
            transitionClass,
            showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            isDarkTheme ? 'text-[#fffdf2]' : 'text-[#0f2301]'
          ]" style="transition-delay: 0ms">
            <ShoppingBag :size="20" :stroke-width="2"
              class="md:!w-[22px] md:!h-[22px] hover:opacity-70 transition-opacity" />

            <!-- Badge -->
            <div v-if="cartStore.count > 0" :key="cartStore.count"
              class="absolute top-0 -right-2 bg-[#0f2301] text-white text-[10px] md:text-[11px] font-bold h-4 w-4 md:h-[18px] md:w-[18px] flex items-center justify-center rounded-full border border-[#0f2301] shadow-sm z-10 pointer-events-none animate-jelly">
              {{ cartStore.count }}
            </div>
          </router-link>

          <!-- Hover Dropdown (hidden mobile) -->
          <transition enter-active-class="transition ease-out duration-300 transform"
            enter-from-class="opacity-0 translate-y-4 scale-95" enter-to-class="opacity-100 translate-y-0 scale-100"
            leave-active-class="transition ease-in duration-200 transform"
            leave-from-class="opacity-100 translate-y-0 scale-100" leave-to-class="opacity-0 translate-y-4 scale-95">
            <div v-show="isCartHovered" class="hidden md:block absolute right-0 top-full pt-2">
              <CartDropdown />
            </div>
          </transition>
        </div>

        <!-- Menu Hambúrguer desktop (Apenas se logado, hidden mobile) -->
        <button v-if="userName" @click="isAdmin ? showAdminSidebar = true : showUserSidebar = true"
          class="hidden md:block hover:opacity-70 transition-opacity" :class="[
            transitionClass,
            showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            isDarkTheme ? 'text-[#fffdf2]' : 'text-[#0f2301]'
          ]" style="transition-delay: 100ms">
          <Menu :size="24" :stroke-width="1.5" class="hover:opacity-70 transition-opacity" />
        </button>

        <!-- Ícone de usuário / Login (mobile: só deslogado | desktop: sempre) -->
        <div :class="[transitionClass, showLinks ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4']"
          style="transition-delay: 200ms">
          <!-- Botão login (deslogado) -->
          <button v-if="!userName" @click="showAuthModal = true" class="group flex items-center"
            :class="isDarkTheme ? 'text-[#fffdf2]' : 'text-[#0f2301]'">
            <User :size="20" :stroke-width="2"
              class="md:!w-[22px] md:!h-[22px] transition-opacity group-hover:opacity-70" />
            <div
              class="hidden md:block max-w-0 overflow-hidden group-hover:max-w-[100px] transition-all duration-700 ease-in-out">
              <span
                class="ml-2 text-xs font-light tracking-wider uppercase italic whitespace-nowrap block transform translate-x-full group-hover:translate-x-0 transition-transform duration-700 ease-in-out">
                ENTRAR
              </span>
            </div>
          </button>

          <!-- Usuário logado (hidden mobile) -->
          <div v-else class="hidden md:flex items-center gap-2 group/user"
            :class="isDarkTheme ? 'text-[#fffdf2]' : 'text-[#0f2301]'">
            <div class="flex items-center">
              <UserStar v-if="isAdmin" :size="22" :stroke-width="2" />
              <User v-else :size="22" :stroke-width="2" />
            </div>
            <div class="h-4 overflow-hidden group cursor-pointer">
              <div class="flex flex-col transition-transform duration-300 group-hover:-translate-y-4">
                <span
                  class="h-4 flex items-center justify-start text-xs font-light tracking-wider uppercase italic whitespace-nowrap">
                  {{ userName.split(' ')[0] }}
                </span>
                <button @click="logout"
                  class="h-4 flex items-center justify-start text-xs font-light tracking-wider uppercase italic hover:opacity-70 w-full text-left whitespace-nowrap">
                  SAIR
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Modal lateral Admin -->
    <AdminSidebar :visible="showAdminSidebar" :userName="userName || 'Administrador'" @close="showAdminSidebar = false"
      @logout="logout" />

    <!-- Modal lateral Usuário -->
    <UserSidebar :visible="showUserSidebar" :userName="userName || 'Cliente'" @close="showUserSidebar = false"
      @logout="logout" @request-login="showAuthModal = true" />

    <!-- Modal de Autenticação -->
    <AuthModal :visible="showAuthModal" @close="showAuthModal = false" />
  </div>
</template>

<style scoped>
@keyframes jelly {
  0% {
    transform: scale(0.9, 1.1);
  }

  25% {
    transform: scale(1.1, 0.9);
  }

  50% {
    transform: scale(0.95, 1.05);
  }

  75% {
    transform: scale(1.02, 0.98);
  }

  100% {
    transform: scale(1, 1);
  }
}

.animate-jelly {
  animation: jelly 0.5s;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 1px;
  background-color: currentColor;
  transition: width 0.3s ease-out;
}

.nav-link:active::after,
.nav-link.router-link-active::after {
  width: 100%;
}

/* Gradiente preto abaixo do cupom até metade da navbar */
.gradient-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  /* cupom (~32px) + metade da navbar (~36px) = ~68px */
  height: 68px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.55) 0%, rgba(0, 0, 0, 0) 100%);
  z-index: 104;
  pointer-events: none;
  opacity: 1;
  transition: opacity 0.5s ease;
}

.gradient-overlay.gradient-hidden {
  opacity: 0;
}
</style>
