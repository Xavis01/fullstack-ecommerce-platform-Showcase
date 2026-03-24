<template>
    <div class="rocca-select font-montserrat">
        <div class="relative">
            <button type="button" @click="toggleDropdown" :disabled="disabled" :class="[
                'w-full px-4 py-3 h-11 border border-[#0f2301]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f2301] focus:border-[#0f2301] transition-all font-montserrat italic text-[#3a5528] text-left flex items-center justify-between',
                disabled ? 'bg-gray-100 cursor-not-allowed opacity-50' : 'bg-white cursor-pointer hover:border-[#0f2301]/50'
            ]">
                <div class="flex items-center gap-3 flex-1 min-w-0">
                    <img v-if="selectedOption?.image && showImages" :src="getImageUrl(selectedOption.image)"
                        @load="handleImageLoad(selectedOption.value)" @error="handleImageError(selectedOption.value)"
                        class="w-8 h-8 object-cover rounded flex-shrink-0"
                        :class="{ 'opacity-0': imageLoadingStates[selectedOption.value] }" />
                    <div v-if="selectedOption?.image && showImages && imageLoadingStates[selectedOption.value]"
                        class="w-8 h-8 flex items-center justify-center flex-shrink-0 absolute">
                        <LoaderCircle class="w-4 h-4 animate-spin text-[#0f2301]" />
                    </div>
                    <!-- Icon Support -->
                    <component v-if="selectedOption?.icon" :is="selectedOption.icon" class="w-5 h-5 text-[#3a5528]" />
                    <span class="truncate">{{ displayValue }}</span>
                </div>
                <ChevronDown class="w-5 h-5 text-[#3a5528] flex-shrink-0 transition-transform"
                    :class="{ 'rotate-180': isOpen }" />
            </button>
        </div>

        <Teleport to="body">
            <div v-if="isOpen" class="fixed inset-0 z-[9999]" @click="closeDropdown">
                <div class="absolute bg-white rounded-xl shadow-2xl border border-[#0f2301]/20 overflow-hidden"
                    :style="dropdownStyle" @click.stop>
                    <div v-if="searchable" class="p-3 border-b border-[#0f2301]/10">
                        <input ref="searchInput" v-model="searchQuery" type="text" placeholder="Buscar..."
                            class="w-full px-3 py-2 border border-[#0f2301]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f2301] text-[#3a5528] font-montserrat italic text-sm" />
                    </div>

                    <div class="max-h-[230px] overflow-y-auto">
                        <button v-for="option in filteredOptions" :key="option.value" type="button"
                            @click="selectOption(option)" :disabled="option.disabled" :class="[
                                'w-full px-4 py-3 text-left flex items-center gap-3 transition-colors font-montserrat italic text-[#3a5528]',
                                option.value === modelValue ? 'bg-[#0f2301] text-[#fffdf2]' : 'hover:bg-[#0f2301]/50',
                                option.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                            ]">
                            <img v-if="option.image && showImages" :src="getImageUrl(option.image)"
                                @load="handleImageLoad(option.value)" @error="handleImageError(option.value)"
                                class="w-8 h-8 object-cover rounded flex-shrink-0"
                                :class="{ 'opacity-0': imageLoadingStates[option.value] }" />
                            <div v-if="option.image && showImages && imageLoadingStates[option.value]"
                                class="w-8 h-8 flex items-center justify-center flex-shrink-0">
                                <LoaderCircle class="w-4 h-4 animate-spin"
                                    :class="option.value === modelValue ? 'text-[#0f2301]' : 'text-[#0f2301]'" />
                            </div>
                            <!-- Icon Support -->
                            <component v-if="option.icon" :is="option.icon" class="w-5 h-5"
                                :class="option.value === modelValue ? 'text-[#fffdf2]' : 'text-[#3a5528]'" />
                            <span class="flex-1">{{ option.label }}</span>
                        </button>

                        <div v-if="filteredOptions.length === 0" class="px-4 py-8 text-center text-[#3a5528]/50 italic">
                            Nenhuma opção encontrada
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ChevronDown, LoaderCircle } from 'lucide-vue-next'

const props = defineProps({
    modelValue: {
        type: [String, Number, Object],
        default: null
    },
    options: {
        type: Array,
        required: true,
        // Format: [{ value: any, label: string, image?: string, disabled?: boolean }]
    },
    placeholder: {
        type: String,
        default: 'Selecione...'
    },
    searchable: {
        type: Boolean,
        default: false
    },
    showImages: {
        type: Boolean,
        default: false
    },
    disabled: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const dropdownStyle = ref({})
const buttonRef = ref(null)
const searchInput = ref(null)
const imageLoadingStates = ref({})

const selectedOption = computed(() => {
    return props.options.find(opt => opt.value === props.modelValue)
})

const displayValue = computed(() => {
    return selectedOption.value?.label || props.placeholder
})

const filteredOptions = computed(() => {
    if (!props.searchable || !searchQuery.value) {
        return props.options
    }
    const query = searchQuery.value.toLowerCase()
    return props.options.filter(opt =>
        opt.label.toLowerCase().includes(query)
    )
})

const cdnBaseUrl = import.meta.env.VITE_CDN_BASE_URL || ''

const getImageUrl = (imagePath) => {
    if (!imagePath) return ''
    if (imagePath.startsWith('http')) return imagePath
    // Remove all leading slashes and 'uploads/' to sanitize
    const cleanPath = imagePath.replace(/^(\/?uploads\/)+/, '')
    return `${cdnBaseUrl}/uploads/${cleanPath}`
}

const handleImageLoad = (optionValue) => {
    imageLoadingStates.value[optionValue] = false
}

const handleImageError = (optionValue) => {
    imageLoadingStates.value[optionValue] = false
}

const toggleDropdown = (event) => {
    if (props.disabled) return
    isOpen.value = !isOpen.value
    if (isOpen.value) {
        calculatePosition(event.target)
        if (props.searchable) {
            nextTick(() => {
                searchInput.value?.focus()
            })
        }
    }
}

const calculatePosition = (buttonElement) => {
    const rect = buttonElement.getBoundingClientRect()
    const dropdownHeight = 300
    const spaceBelow = window.innerHeight - rect.bottom
    const spaceAbove = rect.top
    const margin = 16

    let top = rect.bottom + 8
    let left = rect.left

    if (spaceBelow < dropdownHeight + margin && spaceAbove > spaceBelow) {
        top = rect.top - dropdownHeight - 8
    }

    const dropdownWidth = rect.width
    if (left + dropdownWidth > window.innerWidth - margin) {
        left = window.innerWidth - dropdownWidth - margin
    }

    dropdownStyle.value = {
        top: `${top}px`,
        left: `${left}px`,
        minWidth: `${rect.width}px`
    }
}

const selectOption = (option) => {
    if (option.disabled) return
    emit('update:modelValue', option.value)
    emit('change', option)
    closeDropdown()
}

const closeDropdown = () => {
    isOpen.value = false
    searchQuery.value = ''
}

// Initialize loading states for options with images
watch(() => props.options, (newOptions) => {
    newOptions.forEach(opt => {
        if (opt.image && imageLoadingStates.value[opt.value] === undefined) {
            imageLoadingStates.value[opt.value] = true
        }
    })
}, { immediate: true, deep: true })

// Close on Escape
const handleEscape = (e) => {
    if (e.key === 'Escape' && isOpen.value) {
        closeDropdown()
    }
}

import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
    document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
/* Custom scrollbar */
.max-h-64::-webkit-scrollbar {
    width: 8px;
}

.max-h-64::-webkit-scrollbar-track {
    background: #0f2301;
}

.max-h-64::-webkit-scrollbar-thumb {
    background: #0f2301;
    border-radius: 4px;
}

.max-h-64::-webkit-scrollbar-thumb:hover {
    background: #3a5528;
}
</style>
