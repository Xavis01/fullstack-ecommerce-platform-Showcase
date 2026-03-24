<template>
    <div
        class="min-h-screen bg-[#060606] font-['Montserrat',sans-serif] overflow-x-hidden selection:bg-[#fffdf2] selection:text-[#060606]">

        <!-- HERO SECTION -->
        <header class="relative flex items-center justify-center pt-16 sm:pt-24 pb-12 sm:pb-16 overflow-hidden">
            <div class="relative w-full max-w-2xl px-8 transition-all duration-1000 ease-out"
                :class="{ 'opacity-100 translate-y-0': isMounted, 'opacity-0 translate-y-12': !isMounted }">

                <FuzzyImage src="/ROCCAArchive.png" class="w-full" :enable-hover="true" :base-intensity="0.45"
                    :hover-intensity="1.0" :fuzz-range="40" />
            </div>

            <!-- Social Buttons -->
            <div class="absolute bottom-4 right-4 sm:bottom-8 sm:right-8 flex gap-0 z-10 transition-all duration-1000 ease-out delay-500"
                :class="{ 'opacity-100': isMounted, 'opacity-0': !isMounted }">
                <a href="https://instagram.com/roccainternazionale" target="_blank" rel="noopener noreferrer"
                    class="block h-10 sm:h-12 hover:scale-110 transition-transform duration-300">
                    <FuzzyImage src="/fuzzy-insta.svg" class="w-auto h-full object-contain" :enable-hover="true"
                        :base-intensity="0.25" :hover-intensity="1.0" :fuzz-range="15" />
                </a>
                <a href="https://youtube.com/@RoccaArchive" target="_blank" rel="noopener noreferrer"
                    class="block h-10 sm:h-12 -ml-6 sm:-ml-4 hover:scale-110 transition-transform duration-300">
                    <FuzzyImage src="/fuzzy-youtube.svg" class="w-auto h-full object-contain" :enable-hover="true"
                        :base-intensity="0.25" :hover-intensity="1.0" :fuzz-range="15" />
                </a>
            </div>
        </header>

        <!-- BENTO GRID -->
        <section class="max-w-[1500px] mx-auto px-2 sm:px-4 pb-24 md:pb-32">
            <!-- Loader -->
            <div v-if="loading" class="flex justify-center py-20">
                <div class="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
            </div>

            <div v-else
                class="grid grid-cols-2 lg:grid-cols-6 md:grid-cols-4 auto-rows-[150px] md:auto-rows-[180px] lg:auto-rows-[250px] gap-2 sm:gap-2.5 grid-flow-row-dense">

                <!-- ────── BENTO MEDIA ITEMS ────── -->
                <div v-for="(item, idx) in bentoItems" :key="item.url" :ref="'bentoItem_' + idx"
                    class="group relative overflow-hidden bg-[#111] opacity-0 translate-y-[20px] transition-[opacity,transform] duration-700 ease-out will-change-transform [&.revealed]:opacity-100 [&.revealed]:translate-y-0"
                    :style="{ transitionDelay: (idx % 10) * 50 + 'ms' }" :class="item.cssClass">

                    <video v-if="item.isVideo" :src="item.url"
                        class="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-105"
                        autoplay muted loop playsinline :preload="idx < 8 ? 'auto' : 'metadata'"
                        @loadedmetadata="updateAspect(idx, $event.target.videoWidth, $event.target.videoHeight, $event.target.parentElement)"></video>

                    <template v-else>
                        <!-- Blur placeholder (mostra instantaneamente enquanto imagem real carrega) -->
                        <img v-if="item.blur && !item.loaded" :src="item.blur"
                            class="absolute inset-0 w-full h-full object-cover scale-110 blur-sm" alt=""
                            aria-hidden="true" />

                        <!-- Imagem real -->
                        <img :src="item.url" :alt="'Archive Media ' + idx"
                            class="w-full h-full object-cover transition-all duration-500 ease-out group-hover:scale-105"
                            :class="{ 'opacity-0': !item.loaded, 'opacity-100': item.loaded }"
                            :loading="idx < 8 ? 'eager' : 'lazy'" :fetchpriority="idx < 8 ? 'high' : 'auto'"
                            @error="onImgError" @load="onImageLoad(idx, $event)" />
                    </template>
                </div>
            </div>
        </section>

        <!-- FOOTER -->
        <footer
            class="py-8 sm:py-12 border-t border-white/10 text-center text-white/30 text-[8px] sm:text-[10px] uppercase tracking-[0.2em] sm:tracking-[0.4em] font-light px-4">
        </footer>

        <!-- Scroll to Top Button -->
        <button v-show="showScrollTop" @click="scrollToTop"
            class="fixed bottom-6 left-4 md:bottom-8 md:left-8 z-50 p-2.5 md:p-3 bg-[#fffdf2]/10 hover:bg-[#fffdf2]/20 backdrop-blur-md rounded-full text-[#fffdf2] transition-all duration-300 hover:-translate-y-1 active:scale-95 shadow-lg border border-[#fffdf2]/10">
            <ArrowUp class="w-4 h-4 md:w-5 md:h-5" />
        </button>

    </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue'
import { ArrowUp } from 'lucide-vue-next'
import api from '@/api'
import FuzzyImage from '@/components/FuzzyImage.vue'

const isMounted = ref(false)
const loading = ref(true)
const bentoItems = ref([])
const showScrollTop = ref(false)
let observer = null

// Graceful fallback on missing images
const onImgError = (e) => {
    e.target.style.display = 'none'
}

const onImageLoad = (idx, event) => {
    // Marcar imagem como carregada (para crossfade do blur → real)
    if (bentoItems.value[idx]) {
        bentoItems.value[idx].loaded = true
    }
    // <template> não é um nó DOM real, então img.parentElement já é o div do bento item
    updateAspect(idx, event.target.naturalWidth, event.target.naturalHeight, event.target.parentElement)
}

const updateAspect = (idx, width, height, parentEl) => {
    if (!bentoItems.value[idx] || bentoItems.value[idx].aspectChecked) return;

    // Fallback se não conseguir ler dimensões
    if (!width || !height) return;

    const aspect = width / height;
    let newClass = bentoItems.value[idx].cssClass;

    // Redesenhando o grid para ser de 6 colunas lg, 4 md, 2 mobile. 
    // Assim as peças encaixam com menos sobra.
    if (aspect > 1.2) {
        // Horizontal: Ocupa 2 colunas
        newClass = 'col-span-2 row-span-1'
    } else if (aspect < 0.8) {
        // Vertical/Retrato: Ocupa 1 coluna e 2 linhas (ou um quadrado maior dependendo do random)
        const verticalOrSquare = [
            'col-span-1 row-span-2', // True vertical
            'col-span-1 row-span-1', // Square (corta no cover)
            'col-span-2 row-span-2', // Large Square (corta no cover)
        ];
        newClass = verticalOrSquare[Math.floor(Math.random() * verticalOrSquare.length)];
    } else {
        // Quadrado
        const squares = [
            'col-span-1 row-span-1',
            'col-span-2 row-span-2'
        ];
        newClass = squares[Math.floor(Math.random() * squares.length)];
    }

    if (bentoItems.value[idx].cssClass !== newClass) {
        bentoItems.value[idx].cssClass = newClass
    }
    bentoItems.value[idx].aspectChecked = true;

    // Defer visibility observer to ONLY attach after this specific item has sized itself
    if (observer && parentEl) {
        observer.observe(parentEl);
    }
}

const initObserver = () => {
    if (observer) observer.disconnect()

    const options = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    }

    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed')
                observer.unobserve(entry.target)
            }
        })
    }, options)

    // Elements are individually observed inside updateAspect() when their grid size is locked in
}

const loadArchiveMedia = async () => {
    try {
        // Carregar mídia e manifesto em paralelo
        const [mediaRes, manifestRes] = await Promise.all([
            api.get('/archive-media'),
            api.get('/archive-manifest')
        ])

        const manifest = manifestRes.data || {}

        // shuffle array randomly
        const shuffled = mediaRes.data.sort(() => 0.5 - Math.random())

        bentoItems.value = shuffled.map((file) => {
            const isVideo = file.toLowerCase().endsWith('.mov') || file.toLowerCase().endsWith('.mp4')
            const url = `/bentoGridArquive/${file}`
            const blurData = manifest[file] || null

            return {
                url,
                isVideo,
                blur: blurData?.blur || null,
                loaded: false,
                cssClass: 'col-span-1 row-span-1', // Default Square initially
                aspectChecked: false
            }
        })

    } catch (error) {
        console.error('Error loading archive media:', error)
    } finally {
        loading.value = false
        await nextTick()
        isMounted.value = true
        // Initialize observer instance, but defer actual `.observe()` actions to img load callbacks
        initObserver()
    }
}

const checkScroll = () => {
    showScrollTop.value = window.scrollY > 500
}

const scrollToTop = () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    })
}

onMounted(async () => {
    window.addEventListener('scroll', checkScroll)
    await loadArchiveMedia()
})

onBeforeUnmount(() => {
    window.removeEventListener('scroll', checkScroll)
    if (observer) observer.disconnect()
})
</script>
