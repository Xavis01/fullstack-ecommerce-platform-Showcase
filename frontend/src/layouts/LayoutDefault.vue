<template>
  <div class="overflow-x-hidden relative w-full">
    <NavBar />
    <!-- pt-[108px]: banner (~32px) + nav top-8 (32px) + py-4 (16px) + logo h-11 (44px) - apenas em páginas não-home -->
    <div :class="isTransparentNav ? '' : 'pt-[98px]'">
      <main class="min-h-screen">
        <slot />
      </main>
      <Footer />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const isTransparentNav = computed(() => route.path === '/' || route.path === '/archive')
</script>