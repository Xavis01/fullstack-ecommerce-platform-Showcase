<template>
    <div class="transition group">
        <!-- Se é "em breve" ou modo edição, renderiza como div (sem link); caso contrário, router-link normal -->
        <component :is="(isComingSoon || editModeStore.isEditMode) ? 'div' : 'router-link'"
            :to="(isComingSoon || editModeStore.isEditMode) ? undefined : `/produto/${product.id}`">
            <div @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave"
                class="relative w-full aspect-[3/4] overflow-hidden mb-4 bg-gray-100 flex items-center justify-center"
                :class="{ 'cursor-not-allowed': isComingSoon && !editModeStore.isEditMode }"
                :style="blurPlaceholderStyle">

                <!-- Loader (apenas enquanto a imagem principal não carregar E não tiver placeholder) -->
                <div v-if="!mainImageLoaded && !product.placeholder_blur"
                    class="absolute inset-0 flex items-center justify-center z-10 bg-gray-50/50 backdrop-blur-[1px]">
                    <LoaderCircle class="animate-spin text-gray-400" />
                </div>

                <!-- Primeira imagem (Main) — usa thumbnail se disponível -->
                <img :src="mainImageSrc" :alt="product.name" loading="lazy" @load="handleMainImageLoad"
                    @error="handleMainImageLoad"
                    class="object-cover w-full h-full transition-opacity duration-500 ease-in-out" :class="{
                        'opacity-0': !mainImageLoaded || (isHovered && hasSecondImage),
                        'brightness-50': isComingSoon
                    }" />

                <!-- Segunda imagem (Hover) — carregada sob demanda no primeiro hover -->
                <img v-if="shouldLoadSecondImage && !isComingSoon" :src="secondImageUrl" :alt="product.name"
                    loading="lazy" @load="handleSecondImageLoad" @error="handleSecondImageLoad"
                    class="absolute inset-0 object-cover w-full h-full transition-opacity duration-500 ease-in-out"
                    :class="{ 'opacity-0': !isHovered || !secondImageLoaded, 'opacity-100': isHovered && secondImageLoaded }" />

                <!-- Overlay "Em Breve" -->
                <div v-if="isComingSoon"
                    class="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
                    <span
                        class="text-white text-[9px] md:text-[10px] font-bold uppercase tracking-[0.35em] md:tracking-[0.5em] select-none">
                        Em breve
                    </span>
                </div>
            </div>
            <div class="text-center space-y-2">
                <h3 class="text-sm md:text-base italic text-[#0f2301] font-montserrat">{{ product.name }}</h3>

                <p v-if="isComingSoon"
                    class="text-[9px] md:text-[10px] uppercase tracking-[0.2em] text-[#8c9e78] font-montserrat font-bold">
                    Em breve
                </p>
                <p v-else-if="isOutOfStock"
                    class="text-[9px] md:text-[10px] uppercase tracking-[0.2em] text-[#8c9e78] font-montserrat font-bold">
                    Esgotado
                </p>
                <p v-else class="text-sm md:text-base text-[#0f2301] font-montserrat">
                    R$ {{ product.price.toFixed(2).replace('.', ',') }}
                </p>
            </div>
        </component>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { useEditModeStore } from '@/stores/editMode'

const props = defineProps({
    product: Object
})

const editModeStore = useEditModeStore()
const isHovered = ref(false)
const mainImageLoaded = ref(false)
const secondImageLoaded = ref(false)
const hasHoveredOnce = ref(false) // Controla se já fez hover (lazy load da segunda imagem)

const isComingSoon = computed(() => props.product?.is_coming_soon === true)
const isOutOfStock = computed(() => {
    if (!props.product.variants || props.product.variants.length === 0) return false
    return props.product.variants.every(variant => variant.stock === 0)
})

// ===== Imagem principal: usa thumbnail_url se disponível, senão image_url =====
const mainImageSrc = computed(() => {
    return props.product.thumbnail_url || props.product.image_url
})

// ===== Blur placeholder como background (Phase 4) =====
const blurPlaceholderStyle = computed(() => {
    if (props.product.placeholder_blur) {
        return {
            backgroundImage: `url(${props.product.placeholder_blur})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
        }
    }
    return {}
})

// ===== Segunda imagem (hover) — só tem se existirem imagens extras =====
const hasSecondImage = computed(() => {
    return props.product.images && props.product.images.some(img => !img.is_cover) || (props.product.images && props.product.images.length > 1)
})

// Só carrega a segunda imagem após o primeiro hover (lazy hover)
const shouldLoadSecondImage = computed(() => {
    return hasSecondImage.value && hasHoveredOnce.value
})

const secondImageUrl = computed(() => {
    if (!hasSecondImage.value) return null
    const nonCoverImage = props.product.images.find(img => !img.is_cover && img.url !== props.product.image_url)
    return nonCoverImage ? nonCoverImage.url : (props.product.images[1] ? props.product.images[1].url : null)
})

const handleMainImageLoad = () => {
    mainImageLoaded.value = true
}

const handleSecondImageLoad = () => {
    secondImageLoaded.value = true
}

// Event listeners para hover
const handleMouseEnter = () => {
    if (!isComingSoon.value && hasSecondImage.value) {
        hasHoveredOnce.value = true // Dispara carregamento da segunda imagem
        if (secondImageLoaded.value) {
            isHovered.value = true
        } else {
            // Espera a segunda imagem carregar, depois mostra
            const checkLoaded = setInterval(() => {
                if (secondImageLoaded.value) {
                    isHovered.value = true
                    clearInterval(checkLoaded)
                }
            }, 50)
            // Safety: para de checar depois de 3s
            setTimeout(() => clearInterval(checkLoaded), 3000)
        }
    }
}

const handleMouseLeave = () => {
    isHovered.value = false
}
</script>
