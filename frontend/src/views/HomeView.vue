<template>
  <!-- Splash Screen -->
  <Teleport to="body">
    <div v-if="uiStore.isSplashActive" class="fixed inset-0 z-[100] pointer-events-none">
      <div class="absolute inset-0 bg-[#fffdf2] transition-opacity duration-[2000ms] ease-in-out"
        :class="{ 'opacity-0': uiStore.introStage >= 4 }"></div>
    </div>

    <div v-if="uiStore.isSplashActive" class="fixed inset-0 z-[1100] pointer-events-none">
      <div ref="splashLogoRef"
        class="fixed transition-all ease-[cubic-bezier(0.45,0,0.55,1)] flex items-center justify-center"
        style="will-change: top, left, width, height, transform;" :style="logoStyle">
        <!-- Mantém o controle de proporção para que a caixa (wrapper) não fique com tamanho zero -->
        <img src="/ROCCAVerde.png" alt="ROCCA Loading"
          class="h-full w-auto object-contain transition-opacity duration-300 ease-in-out"
          :class="uiStore.introStage >= 4 ? 'opacity-0' : 'opacity-100'" />
        <!-- Aparece posicionada em cima da anterior na mudança -->
        <img src="/ROCCABehe.png" alt="ROCCA Transition"
          class="absolute inset-0 w-full h-full object-contain transition-opacity duration-300 ease-in-out"
          :class="uiStore.introStage >= 4 ? 'opacity-100' : 'opacity-0'" />
      </div>
    </div>
  </Teleport>

  <!-- Main Content Wrappper -->
  <div class="min-h-screen bg-[#fffdf2] selection:bg-[#0f2301] selection:text-[#fffdf2] font-montserrat">

    <!-- Hero Block -->
    <div class="relative w-full overflow-hidden transition-all duration-[1200ms]" :class="{
      'opacity-0 blur-xl scale-110': shouldAnimate && (!isLoaded || uiStore.introStage < 3),
      'opacity-100 blur-0 scale-100': !shouldAnimate || (isLoaded && uiStore.introStage >= 3)
    }">
      <!-- Carousel Container -->
      <div class="relative w-full h-[100svh] md:h-[100vh] grid overflow-hidden" @touchstart="onTouchStart"
        @touchend="onTouchEnd">
        <transition-group name="fade">
          <video v-for="(video, index) in carouselVideos" :key="video" v-show="currentVideoIndex === index" :src="video"
            :ref="el => { if (el) videoRefs[index] = el }"
            class="w-full h-full object-cover block col-start-1 row-start-1" autoplay muted loop playsinline
            webkit-playsinline preload="auto" @loadeddata="onImageLoad"></video>
        </transition-group>

        <!-- Overlay Gradient (Softer Transition) -->
        <!-- <div
          class="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#fffdf2] to-transparent pointer-events-none opacity-60">
        </div> -->

        <!-- scroll Down Indicator (Destaques) -->
        <!-- <button @click="scrollToHighlights"
          class="absolute bottom-16 left-12 z-20 flex flex-col items-start gap-3 group transition-all duration-700 hover:-translate-y-2">
          <span
            class="text-white text-[10px] uppercase tracking-[0.5em] font-bold opacity-60 group-hover:opacity-100 transition-opacity">
            Destaques
          </span>
          <div class="relative w-32 h-[1px] bg-white/30 overflow-hidden">
            <div
              class="absolute top-0 left-0 h-full bg-white w-full -translate-x-full group-hover:translate-x-0 transition-transform duration-700">
            </div>
          </div>
        </button> -->

        <!-- Carousel Dots -->
        <div class="absolute bottom-6 md:bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-3 md:gap-4 z-20"
          v-if="carouselVideos.length > 1">
          <button v-for="(_, index) in carouselVideos" :key="index" @click="setCarouselVideo(index)"
            class="group relative p-2 overflow-hidden rounded-full" :aria-label="`Ir para vídeo ${index + 1}`">
            <div class="w-1.5 h-1.5 rounded-full transition-all duration-500"
              :class="currentVideoIndex === index ? 'bg-white scale-[1.8] shadow-lg' : 'bg-white/40 group-hover:bg-white/70'">
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Highlights Section (Premium Grid Refined) -->
    <section id="destaques" class="relative py-12 md:py-16 bg-[#fffdf2] overflow-visible md:overflow-hidden">

      <!-- Noise Texture Overlay (Sectional) -->
      <div class="absolute inset-0 pointer-events-none opacity-[0.02] z-0"
        style="background-image: url('data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E');">
      </div>

      <div class="max-w-[1500px] mx-auto px-4 md:px-6 relative z-10 pt-4">
        <!-- Text: Destaques (Absolute Top Left) -->
        <span
          class="absolute top-0 left-4 md:left-6 text-[#0f2301] text-[10px] md:text-xs uppercase tracking-[0.4em] md:tracking-[0.6em] font-bold block translate-x-1">
          Destaques
        </span>

        <!-- Section Header (Needs minimum height because logo is absolute) -->
        <div
          class="relative flex flex-col md:flex-row items-end justify-between mb-6 md:mb-10 min-h-[220px] md:min-h-[250px] reveal-item">

          <!-- Center: Logo perfectly centered, huge, and absolute -->
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none overflow-visible">
            <img src="/RoccaSummer.png" alt="ROCCA SUMMER'26"
              class="h-[55vh] md:h-auto w-auto md:w-[1200px] lg:w-[1600px] xl:w-[2400px] max-w-none object-contain pointer-events-auto" />
          </div>

          <!-- Empty div to push description to the right in flex layout -->
          <div class="hidden md:block md:w-1/3"></div>

          <!-- Description: full width on mobile, right-aligned on desktop -->
          <div class="w-full md:w-1/3 flex md:justify-end relative z-10 mt-auto">
            <div
              class="w-full md:w-auto md:max-w-xs text-[#bababa] font-light italic text-sm md:text-lg border-l border-[#eaddcf] pl-4 md:pl-8 pb-2 bg-[#fffdf2]/80 backdrop-blur-sm">
              Uma seção exclusiva das nossas peças de lançamento da coleção RoccaSummer'26.
            </div>
          </div>
        </div>

        <!-- Premium Bento Grid -->
        <div class="grid grid-cols-2 md:grid-cols-12 grid-rows-[auto] gap-2.5 md:gap-5">

          <!-- ROW 1 -->

          <!-- Card A: Tall featured (left) -->
          <div v-if="highlights[0]" class="col-span-2 md:col-span-5 md:row-span-2 reveal-item" data-delay="100"
            :draggable="editModeStore.isEditMode" @dragstart="onDragStart(0, $event)"
            @dragover.prevent="onDragOver(0, $event)" @drop="onDrop(0)" @dragend="onDragEnd"
            :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
            <!-- Edit mode drag handle overlay -->
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
              <div
                class="bg-black/40 backdrop-blur-[2px] rounded-xl px-4 py-2 flex items-center gap-2 text-white text-xs font-bold uppercase tracking-wider">
                <GripVertical class="w-4 h-4" />
                Destaque 1
              </div>
            </div>
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-10 border-2 border-dashed border-white/50 pointer-events-none"
              :class="dragOverIndex === 0 ? 'border-[#861e1f] bg-[#861e1f]/10' : ''"></div>
            <component :is="editModeStore.isEditMode ? 'div' : (highlights[0].is_coming_soon ? 'div' : 'router-link')"
              :to="editModeStore.isEditMode ? undefined : (highlights[0].is_coming_soon ? undefined : `/produto/${highlights[0].id}`)"
              class="product-card group h-full min-h-[320px] md:min-h-[480px]"
              :class="{ 'cursor-not-allowed': !editModeStore.isEditMode && highlights[0].is_coming_soon }">
              <img :src="highlights[0].thumbnail_url || highlights[0].image_url" :alt="highlights[0].name"
                class="card-img" loading="lazy" />
              <!-- Always-visible label -->
              <!-- <div class="absolute top-4 left-4 md:top-6 md:left-6 z-10">
                <span class="badge">Editor's Pick</span>
              </div> -->
              <!-- Info overlay -->
              <div class="card-info card-info-mobile">
                <p class="card-name">{{ highlights[0].name }}</p>
                <p class="card-price">{{ highlights[0].is_coming_soon ? 'Em breve' : formatPrice(highlights[0].price) }}
                </p>
              </div>
            </component>
          </div>

          <!-- Card B: Square (middle-top) -->
          <div v-if="highlights[1]" class="md:col-span-4 reveal-item" data-delay="200"
            :draggable="editModeStore.isEditMode" @dragstart="onDragStart(1, $event)"
            @dragover.prevent="onDragOver(1, $event)" @drop="onDrop(1)" @dragend="onDragEnd"
            :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
              <div
                class="bg-black/40 backdrop-blur-[2px] rounded-xl px-4 py-2 flex items-center gap-2 text-white text-xs font-bold uppercase tracking-wider">
                <GripVertical class="w-4 h-4" />
                Destaque 2
              </div>
            </div>
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-10 border-2 border-dashed border-white/50 pointer-events-none"
              :class="dragOverIndex === 1 ? 'border-[#861e1f] bg-[#861e1f]/10' : ''"></div>
            <component :is="editModeStore.isEditMode ? 'div' : (highlights[1].is_coming_soon ? 'div' : 'router-link')"
              :to="editModeStore.isEditMode ? undefined : (highlights[1].is_coming_soon ? undefined : `/produto/${highlights[1].id}`)"
              class="product-card group h-full md:aspect-square"
              :class="{ 'cursor-not-allowed': !editModeStore.isEditMode && highlights[1].is_coming_soon }">
              <img :src="highlights[1].thumbnail_url || highlights[1].image_url" :alt="highlights[1].name"
                class="card-img" loading="lazy" />
              <div class="card-info card-info-mobile">
                <p class="card-name">{{ highlights[1].name }}</p>
                <p class="card-price">{{ highlights[1].is_coming_soon ? 'Em breve' : formatPrice(highlights[1].price) }}
                </p>
              </div>
            </component>
          </div>

          <!-- Decorative Video / Instagram Spot (right-top) -->
          <div class="md:col-span-3 reveal-item" data-delay="300">
            <a href="https://instagram.com/roccainternazionale" target="_blank" rel="noopener noreferrer"
              class="block h-full aspect-[3/5] md:aspect-auto md:min-h-[240px] overflow-hidden border border-[#eaddcf] relative group">

              <video src="/videos/jorts_loop.MOV" autoplay loop muted playsinline
                class="absolute inset-0 w-full h-full object-cover transition-transform duration-[3s] group-hover:scale-110 grayscale-[30%]">
              </video>

              <!-- <div class="absolute inset-0  from-[#3a5528]/60 to-transparent pointer-events-none"></div> -->

              <div class="absolute bottom-4 left-4 md:bottom-6 md:left-6 text-[#fffdf2] flex items-center gap-2">
                <Instagram class="w-3.5 h-3.5 md:w-4 md:h-4" />
                <p
                  class="text-xs md:text-sm font-light italic mt-0.5 hover:underline decoration-1 underline-offset-4 pointer-events-auto">
                  @roccainternazionale</p>
              </div>
            </a>
          </div>

          <!-- ROW 2 -->

          <!-- Card C: Tall wide (middle-bottom, spanning 4+3=7 cols on row 2) -->
          <div v-if="highlights[2]" class="md:col-span-4 reveal-item" data-delay="350"
            :draggable="editModeStore.isEditMode" @dragstart="onDragStart(2, $event)"
            @dragover.prevent="onDragOver(2, $event)" @drop="onDrop(2)" @dragend="onDragEnd"
            :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
              <div
                class="bg-black/40 backdrop-blur-[2px] rounded-xl px-4 py-2 flex items-center gap-2 text-white text-xs font-bold uppercase tracking-wider">
                <GripVertical class="w-4 h-4" />
                Destaque 3
              </div>
            </div>
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-10 border-2 border-dashed border-white/50 pointer-events-none"
              :class="dragOverIndex === 2 ? 'border-[#861e1f] bg-[#861e1f]/10' : ''"></div>
            <component :is="editModeStore.isEditMode ? 'div' : (highlights[2].is_coming_soon ? 'div' : 'router-link')"
              :to="editModeStore.isEditMode ? undefined : (highlights[2].is_coming_soon ? undefined : `/produto/${highlights[2].id}`)"
              class="product-card group aspect-[3/5] md:aspect-square"
              :class="{ 'cursor-not-allowed': !editModeStore.isEditMode && highlights[2].is_coming_soon }">
              <img :src="highlights[2].thumbnail_url || highlights[2].image_url" :alt="highlights[2].name"
                class="card-img" loading="lazy" />
              <div class="card-info card-info-mobile">
                <p class="card-name">{{ highlights[2].name }}</p>
                <p class="card-price">{{ highlights[2].is_coming_soon ? 'Em breve' : formatPrice(highlights[2].price) }}
                </p>
              </div>
            </component>
          </div>

          <!-- Card D: Tall right (shares row 2, 3 cols) -->
          <div v-if="highlights[3]" class="md:col-span-3 reveal-item" data-delay="450"
            :draggable="editModeStore.isEditMode" @dragstart="onDragStart(3, $event)"
            @dragover.prevent="onDragOver(3, $event)" @drop="onDrop(3)" @dragend="onDragEnd"
            :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
              <div
                class="bg-black/40 backdrop-blur-[2px] rounded-xl px-4 py-2 flex items-center gap-2 text-white text-xs font-bold uppercase tracking-wider">
                <GripVertical class="w-4 h-4" />
                Destaque 4
              </div>
            </div>
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-10 border-2 border-dashed border-white/50 pointer-events-none"
              :class="dragOverIndex === 3 ? 'border-[#861e1f] bg-[#861e1f]/10' : ''"></div>
            <component :is="editModeStore.isEditMode ? 'div' : (highlights[3].is_coming_soon ? 'div' : 'router-link')"
              :to="editModeStore.isEditMode ? undefined : (highlights[3].is_coming_soon ? undefined : `/produto/${highlights[3].id}`)"
              class="product-card group h-full md:aspect-[3/4]"
              :class="{ 'cursor-not-allowed': !editModeStore.isEditMode && highlights[3].is_coming_soon }">
              <img :src="highlights[3].thumbnail_url || highlights[3].image_url" :alt="highlights[3].name"
                class="card-img" loading="lazy" />
              <div class="card-info card-info-mobile">
                <p class="card-name">{{ highlights[3].name }}</p>
                <p class="card-price">{{ highlights[3].is_coming_soon ? 'Em breve' : formatPrice(highlights[3].price) }}
                </p>
              </div>
            </component>
          </div>

          <!-- ROW 3: two wide cards spanning half width each -->
          <div v-if="highlights[4]" class="md:col-span-6 reveal-item" data-delay="550"
            :draggable="editModeStore.isEditMode" @dragstart="onDragStart(4, $event)"
            @dragover.prevent="onDragOver(4, $event)" @drop="onDrop(4)" @dragend="onDragEnd"
            :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
              <div
                class="bg-black/40 backdrop-blur-[2px] rounded-xl px-4 py-2 flex items-center gap-2 text-white text-xs font-bold uppercase tracking-wider">
                <GripVertical class="w-4 h-4" />
                Destaque 5
              </div>
            </div>
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-10 border-2 border-dashed border-white/50 pointer-events-none"
              :class="dragOverIndex === 4 ? 'border-[#861e1f] bg-[#861e1f]/10' : ''"></div>
            <component :is="editModeStore.isEditMode ? 'div' : (highlights[4].is_coming_soon ? 'div' : 'router-link')"
              :to="editModeStore.isEditMode ? undefined : (highlights[4].is_coming_soon ? undefined : `/produto/${highlights[4].id}`)"
              class="product-card group aspect-square"
              :class="{ 'cursor-not-allowed': !editModeStore.isEditMode && highlights[4].is_coming_soon }">
              <img :src="highlights[4].thumbnail_url || highlights[4].image_url" :alt="highlights[4].name"
                class="card-img" loading="lazy" />
              <div class="card-info card-info-mobile">
                <p class="card-name">{{ highlights[4].name }}</p>
                <p class="card-price">{{ highlights[4].is_coming_soon ? 'Em breve' : formatPrice(highlights[4].price) }}
                </p>
              </div>
            </component>
          </div>

          <div v-if="highlights[5]" class="md:col-span-6 reveal-item" data-delay="650"
            :draggable="editModeStore.isEditMode" @dragstart="onDragStart(5, $event)"
            @dragover.prevent="onDragOver(5, $event)" @drop="onDrop(5)" @dragend="onDragEnd"
            :class="editModeStore.isEditMode ? 'cursor-grab active:cursor-grabbing' : ''">
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
              <div
                class="bg-black/40 backdrop-blur-[2px] rounded-xl px-4 py-2 flex items-center gap-2 text-white text-xs font-bold uppercase tracking-wider">
                <GripVertical class="w-4 h-4" />
                Destaque 6
              </div>
            </div>
            <div v-if="editModeStore.isEditMode"
              class="absolute inset-0 z-10 border-2 border-dashed border-white/50 pointer-events-none"
              :class="dragOverIndex === 5 ? 'border-[#861e1f] bg-[#861e1f]/10' : ''"></div>
            <component :is="editModeStore.isEditMode ? 'div' : (highlights[5].is_coming_soon ? 'div' : 'router-link')"
              :to="editModeStore.isEditMode ? undefined : (highlights[5].is_coming_soon ? undefined : `/produto/${highlights[5].id}`)"
              class="product-card group aspect-square"
              :class="{ 'cursor-not-allowed': !editModeStore.isEditMode && highlights[5].is_coming_soon }">
              <img :src="highlights[5].thumbnail_url || highlights[5].image_url" :alt="highlights[5].name"
                class="card-img" loading="lazy" />
              <div class="card-info card-info-mobile">
                <p class="card-name">{{ highlights[5].name }}</p>
                <p class="card-price">{{ highlights[5].is_coming_soon ? 'Em breve' : formatPrice(highlights[5].price) }}
                </p>
              </div>
            </component>
          </div>
        </div>

        <!-- View All CTA -->
        <div class="mt-16 md:mt-32 text-center reveal-item">
          <router-link to="/produtos"
            class="inline-block px-12 md:px-20 py-4 md:py-5 rounded-full border border-[#0f2301] text-[#0f2301] font-bold italic tracking-widest uppercase text-[9px] md:text-[10px] hover:bg-[#0f2301] hover:text-[#fffdf2] transition-all duration-700 shadow-xl active:scale-95">
            Ver Tudo
          </router-link>
        </div>
      </div>
    </section>

    <!-- Brand Quote Section -->
    <section class="py-20 md:py-48 text-center reveal-section">
      <div class="max-w-4xl mx-auto px-6">
        <Quote class="w-8 h-8 md:w-12 md:h-12 text-[#0f2301]/10 mx-auto mb-8 md:mb-12" />
        <h3 class="text-2xl md:text-5xl font-light italic text-[#3a5528] tracking-tighter leading-tight reveal-item">
          "Il marchio <span class="font-bold non-italic tracking-normal">italiano</span> originale."
        </h3>
      </div>
    </section>

    <!-- Scroll to Top Button -->
    <button v-show="showScrollTop" @click="scrollToTop"
      class="fixed bottom-6 left-4 md:bottom-8 md:left-8 z-50 p-2.5 md:p-3 bg-[#0f2301]/10 hover:bg-[#0f2301]/20 backdrop-blur-md rounded-full text-[#0f2301] transition-all duration-300 hover:-translate-y-1 active:scale-95 shadow-lg border border-[#0f2301]/10">
      <ArrowUp class="w-4 h-4 md:w-5 md:h-5" />
    </button>

    <!-- Save Highlights Order Button (Edit Mode) -->
    <Teleport to="body">
      <Transition name="slide-up">
        <button v-if="editModeStore.isEditMode" @click="saveHighlightsOrder" :disabled="isSavingOrder"
          class="fixed bottom-6 right-4 md:bottom-8 md:right-8 z-[200] flex items-center gap-2.5 px-5 py-3.5 bg-[#0f2301] text-[#fffdf2] rounded-full shadow-2xl font-bold text-xs uppercase tracking-widest hover:bg-[#1a3805] active:scale-95 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed border border-[#0f2301]/50">
          <Check v-if="!isSavingOrder" class="w-4 h-4" />
          <LoaderCircle v-else class="w-4 h-4 animate-spin" />
          {{ isSavingOrder ? 'Salvando...' : 'Salvar Alterações' }}
        </button>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useRoute } from 'vue-router'
import { ArrowRight, Quote, Instagram, ArrowUp, GripVertical, Check, LoaderCircle } from 'lucide-vue-next'
import api from '@/api'
import { useEditModeStore } from '@/stores/editMode'
import { useToast } from 'vue-toastification'

const uiStore = useUIStore()
const route = useRoute()
const editModeStore = useEditModeStore()
const toast = useToast()
const isLoaded = ref(false)
const splashLogoRef = ref(null)

const highlights = ref([])
const hasSeenSplashStr = () => sessionStorage.getItem('splash_shown') === 'true'
const shouldAnimate = ref(!hasSeenSplashStr())
let observer = null

// Drag-and-drop state for highlights
const dragFromIndex = ref(null)
const dragOverIndex = ref(null)
const isSavingOrder = ref(false)

const onDragStart = (index, event) => {
  dragFromIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOver = (index, event) => {
  dragOverIndex.value = index
}

const onDrop = (toIndex) => {
  if (dragFromIndex.value === null || dragFromIndex.value === toIndex) {
    dragOverIndex.value = null
    return
  }
  const updated = [...highlights.value]
  const [moved] = updated.splice(dragFromIndex.value, 1)
  updated.splice(toIndex, 0, moved)
  highlights.value = updated
  dragFromIndex.value = null
  dragOverIndex.value = null
}

const onDragEnd = () => {
  dragFromIndex.value = null
  dragOverIndex.value = null
}

const saveHighlightsOrder = async () => {
  isSavingOrder.value = true
  try {
    const order = highlights.value.map(h => h.id)
    await api.put('/admin/products/highlights/reorder', { order })
    toast.success('Destaques reordenados com sucesso!')
    editModeStore.disableEditMode()
  } catch (e) {
    console.error(e)
    toast.error('Erro ao salvar ordem dos destaques')
  } finally {
    isSavingOrder.value = false
  }
}

const lockScroll = () => {
  document.body.classList.add('overflow-hidden')
}

const unlockScroll = () => {
  document.body.classList.remove('overflow-hidden')
}

const showScrollTop = ref(false)
const handleScroll = () => {
  showScrollTop.value = window.scrollY > 300
}
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const logoStyle = ref({
  top: '50%',
  left: '50%',
  height: '180px',
  transform: 'translate(-50%, -50%)',
  opacity: 1
})

const formatPrice = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const fetchHighlights = async () => {
  try {
    const res = await api.get('/products/highlights')
    highlights.value = res.data
    // Re-observe after data is loaded and DOM updated
    nextTick(() => {
      initObserver()
    })
  } catch (e) {
    console.error('Erro ao carregar destaques:', e)
  }
}

const scrollToHighlights = () => {
  const el = document.getElementById('destaques')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const initObserver = () => {
  if (observer) observer.disconnect()

  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed')
      }
    })
  }, { threshold: 0.05, rootMargin: '0px 0px 0px 0px' })

  document.querySelectorAll('.reveal-section, .reveal-item').forEach(el => {
    observer.observe(el)
  })
}

const onImageLoad = () => {
  requestAnimationFrame(() => {
    isLoaded.value = true
  })
}

const carouselVideos = ['/videos/teaser_sensorial.mp4', '/videos/spoiler_film.mp4']
const currentVideoIndex = ref(0)
const videoRefs = ref([])

const playCurrentVideo = () => {
  videoRefs.value.forEach((video, index) => {
    if (video) {
      video.muted = true;
      video.defaultMuted = true;
      video.playsInline = true;

      // Required for iOS low power mode
      video.setAttribute('playsinline', '');
      video.setAttribute('webkit-playsinline', '');

      if (index === currentVideoIndex.value) {
        // Only reset time if it's not already playing to allow loop
        if (video.paused) {
          video.currentTime = 0;
        }

        const playPromise = video.play();
        if (playPromise !== undefined) {
          playPromise.catch(e => {
            console.warn('Autoplay prevented, possibly requires user interaction', e);
            // Fallback: wait for user interaction to resume the loop
            const forcePlayOnTouch = () => {
              if (currentVideoIndex.value === index) {
                video.play();
              }
              document.removeEventListener('touchstart', forcePlayOnTouch);
              document.removeEventListener('click', forcePlayOnTouch);
            };
            document.addEventListener('touchstart', forcePlayOnTouch, { once: true });
            document.addEventListener('click', forcePlayOnTouch, { once: true });
          });
        }
      } else {
        video.pause();
      }
    }
  })
}

const setCarouselVideo = (index) => {
  currentVideoIndex.value = index
  nextTick(() => playCurrentVideo())
}

const nextCarouselVideo = () => {
  currentVideoIndex.value = (currentVideoIndex.value + 1) % carouselVideos.length
  nextTick(() => playCurrentVideo())
}

// Touch swipe support for video carousel
const touchStartX = ref(0)
const onTouchStart = (e) => {
  touchStartX.value = e.changedTouches[0].screenX
}
const onTouchEnd = (e) => {
  const diff = touchStartX.value - e.changedTouches[0].screenX
  if (Math.abs(diff) > 50) {
    if (diff > 0) {
      // Swipe left → next video
      nextCarouselVideo()
    } else {
      // Swipe right → previous video
      const prev = (currentVideoIndex.value - 1 + carouselVideos.length) % carouselVideos.length
      setCarouselVideo(prev)
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  fetchHighlights()
  nextTick(() => {
    playCurrentVideo()
    initObserver() // init immediately so header is visible even without products
  })

  if (route.path === '/') {
    const hasSeenSplash = hasSeenSplashStr()
    if (hasSeenSplash) {
      uiStore.finishSplash()
      shouldAnimate.value = false
      isLoaded.value = true
      return
    }

    sessionStorage.setItem('splash_shown', 'true')
    uiStore.startSplash()
    const navbarLogo = document.getElementById('navbar-logo')

    if (navbarLogo) {
      setTimeout(() => {
        const startRect = splashLogoRef.value?.getBoundingClientRect()
        if (startRect) {
          logoStyle.value = {
            top: `${startRect.top}px`,
            left: `${startRect.left}px`,
            height: `${startRect.height}px`,
            width: `${startRect.width}px`,
            transform: 'none',
            opacity: 1,
            position: 'fixed',
            transition: 'none'
          }
        }

        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            const rect = navbarLogo.getBoundingClientRect()
            logoStyle.value = {
              top: `${rect.top}px`,
              left: `${rect.left}px`,
              height: `${rect.height}px`,
              width: `${rect.width}px`,
              transform: 'none',
              opacity: 1,
              transitionDuration: '2000ms'
            }

            setTimeout(() => uiStore.setStage(1), 500)
            setTimeout(() => uiStore.setStage(2), 1000)
            setTimeout(() => uiStore.setStage(3), 600)

            setTimeout(() => {
              uiStore.setStage(4)
              setTimeout(() => {
                uiStore.finishSplash()
              }, 2000)
            }, 2000)
          })
        })
      }, 1500)
    } else {
      uiStore.finishSplash()
    }
  } else {
    uiStore.finishSplash()
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (observer) observer.disconnect()
  videoRefs.value.forEach(video => {
    if (video) video.pause()
  })
})
</script>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500&display=swap');

.font-montserrat {
  font-family: 'Montserrat', sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 1.5s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Hide native video controls on mobile (iOS/Safari) */
video::-webkit-media-controls {
  display: none !important;
}

video::-webkit-media-controls-start-playback-button {
  display: none !important;
}

video {
  pointer-events: none;
}

/* Premium Card System */
.product-card {
  display: block;
  position: relative;
  overflow: hidden;
  /* border-radius: 3rem; */
  border: 1px solid #eaddcf;
  background: #0f2301;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 2s cubic-bezier(0.16, 1, 0.3, 1);
}

.group:hover .card-img {
  transform: scale(1.08);
}

.card-info {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1.25rem 1.25rem 1.25rem 1.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.55) 0%, rgba(0, 0, 0, 0) 55%);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.group:hover .card-info {
  opacity: 1;
  transform: translateY(0);
}

/* Mobile: always show card info (no hover on touch) */
.card-info-mobile {
  opacity: 1;
  transform: translateY(0);
}

@media (min-width: 768px) {
  .card-info {
    padding: 2rem 2rem 2rem 2.5rem;
  }

  .card-info-mobile {
    opacity: 0;
    transform: translateY(8px);
  }

  .group:hover .card-info-mobile {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-name {
  font-size: 1.15rem;
  font-weight: 300;
  font-style: italic;
  color: #ffffff;
  letter-spacing: -0.02em;
  margin-bottom: 0.3rem;
  line-height: 1.2;
}

.card-price {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.75);
}

.badge {
  display: inline-block;
  padding: 0.35rem 1rem;
  background: rgba(255, 253, 242, 0.85);
  backdrop-filter: blur(8px);
  border-radius: 9999px;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #3a5528;
}

/* Scroll Reveal */
.reveal-section {
  opacity: 0;
  transform: translateY(40px);
  transition: all 1.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal-section.revealed {
  opacity: 1;
  transform: translateY(0);
}

.reveal-item {
  opacity: 0;
  transform: translateY(30px);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal-item.revealed {
  opacity: 1;
  transform: translateY(0);
}

.reveal-item[data-delay="100"] {
  transition-delay: 0.1s;
}

.reveal-item[data-delay="200"] {
  transition-delay: 0.2s;
}

.reveal-item[data-delay="300"] {
  transition-delay: 0.3s;
}

.reveal-item[data-delay="400"] {
  transition-delay: 0.4s;
}

.reveal-item[data-delay="500"] {
  transition-delay: 0.5s;
}

.reveal-item[data-delay="600"] {
  transition-delay: 0.6s;
}

/* Custom Animations */
@keyframes trackingIn {
  from {
    letter-spacing: 1em;
    opacity: 0;
  }

  to {
    letter-spacing: 0.6em;
    opacity: 0.6;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fadeIn 2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes dash {
  from {
    stroke-dashoffset: 100;
  }

  to {
    stroke-dashoffset: 0;
  }
}

/* Slide-up transition for save button */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(120%);
  opacity: 0;
}

/* Grid items in edit mode need relative positioning for overlays */
.reveal-item {
  position: relative;
}
</style>
