<!-- src/App.vue -->
<template>
  <LayoutDefault class="bg-[#fffdf2]">
    <router-view />
    <AuthModal :visible="uiStore.authModalVisible" @close="uiStore.closeAuthModal" />
    <AdminSidebar :visible="showAdminSidebar" @close="closeSidebar" />
  </LayoutDefault>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed, onMounted } from 'vue'
import LayoutDefault from '@/layouts/LayoutDefault.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AuthModal from '@/components/AuthModal.vue'
import { useUserStore } from '@/stores/user'
import { useUIStore } from '@/stores/ui'

const userStore = useUserStore()
const uiStore = useUIStore()
const route = useRoute()
const router = useRouter()

// O sidebar aparece somente se a rota for exatamente "/admin"
const showAdminSidebar = computed(() => route.path === '/admin')

onMounted(async () => {
  userStore.fetchUser()
  await router.isReady()
  if (route.path !== '/') {
    uiStore.finishSplash()
  }
})

function closeSidebar() {
  router.push('/') // ou qualquer página pública que você quiser
}
</script>
