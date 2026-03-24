<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ChevronUp, ChevronDown, Loader2, Check } from 'lucide-vue-next'

const props = defineProps({
    modelValue: { type: Array, default: () => [] },
    items: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    placeholder: { type: String, default: 'Selecione' }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const buttonRef = ref(null)
const dropdownStyle = ref({})

const toggle = () => {
    if (!props.loading) {
        isOpen.value = !isOpen.value
        if (isOpen.value) {
            nextTick(() => calculatePosition())
        }
    }
}

const calculatePosition = () => {
    if (!buttonRef.value) return
    const rect = buttonRef.value.getBoundingClientRect()
    const dropdownHeight = 220
    const spaceBelow = window.innerHeight - rect.bottom
    const spaceAbove = rect.top
    const margin = 8

    let top = rect.bottom + 4
    let left = rect.left

    if (spaceBelow < dropdownHeight + margin && spaceAbove > spaceBelow) {
        top = rect.top - dropdownHeight - 4
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

const toggleSelection = (item) => {
    const currentValues = [...props.modelValue]
    const index = currentValues.indexOf(item.id)

    if (index === -1) {
        currentValues.push(item.id)
    } else {
        currentValues.splice(index, 1)
    }

    emit('update:modelValue', currentValues)
}

const isSelected = (item) => {
    return props.modelValue.includes(item.id)
}

const displayText = computed(() => {
    if (props.loading) return 'Carregando...'
    if (props.modelValue.length === 0) return props.placeholder

    if (props.modelValue.length === 1) {
        const item = props.items.find(i => i.id === props.modelValue[0])
        return item ? item.name : props.placeholder
    }

    return `${props.modelValue.length} selecionados`
})

const closeDropdown = () => {
    isOpen.value = false
}

// Close on Escape
const handleEscape = (e) => {
    if (e.key === 'Escape' && isOpen.value) closeDropdown()
}

onMounted(() => {
    document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
    <div class="relative">
        <!-- Trigger -->
        <button ref="buttonRef" type="button" @click="toggle" :disabled="loading"
            class="w-full px-3 py-2.5 border rounded-lg shadow-sm text-left flex items-center justify-between transition-all bg-white"
            :class="isOpen
                ? 'border-[#0f2301] ring-2 ring-[#0f2301]/30'
                : 'border-[#0f2301]/30 hover:border-[#0f2301]/60'">
            <!-- Loading state -->
            <span v-if="loading" class="flex items-center gap-2 text-[#3a5528]/50 italic text-sm tracking-wide"
                style="font-family: 'Montserrat', sans-serif;">
                <Loader2 class="w-4 h-4 animate-spin shrink-0" />
                Carregando...
            </span>
            <!-- Selected / placeholder -->
            <span v-else class="text-sm tracking-wide italic truncate" style="font-family: 'Montserrat', sans-serif;"
                :class="modelValue.length > 0 ? 'text-[#3a5528]' : 'text-[#3a5528]/40'">
                {{ displayText }}
            </span>
            <ChevronUp v-if="isOpen" class="w-4 h-4 text-[#3a5528] shrink-0 ml-2" />
            <ChevronDown v-else class="w-4 h-4 text-[#3a5528]/50 shrink-0 ml-2" />
        </button>

        <!-- Overlay + Dropdown via Teleport -->
        <Teleport to="body">
            <div v-if="isOpen && !loading" class="fixed inset-0 z-[9998]" @click="closeDropdown">
                <div class="absolute bg-white rounded-lg shadow-lg border border-[#0f2301]/20 overflow-hidden max-h-48 overflow-y-auto"
                    :style="dropdownStyle" @click.stop>
                    <button type="button" v-for="item in items" :key="item.id" @click="toggleSelection(item)"
                        class="w-full px-4 py-2.5 text-left text-sm tracking-wide transition-colors italic flex items-center justify-between"
                        style="font-family: 'Montserrat', sans-serif;" :class="isSelected(item)
                            ? 'bg-[#0f2301]/10 text-[#3a5528]'
                            : 'text-[#3a5528]/80 hover:bg-[#0f2301]/50'">
                        <span>{{ item.name }}</span>
                        <div v-if="isSelected(item)"
                            class="w-4 h-4 bg-[#0f2301] rounded text-white flex items-center justify-center">
                            <Check class="w-3 h-3" />
                        </div>
                        <div v-else class="w-4 h-4 border border-[#8c9e78] rounded"></div>
                    </button>
                    <div v-if="items.length === 0" class="px-4 py-3 text-[#3a5528]/50 italic text-sm text-center"
                        style="font-family: 'Montserrat', sans-serif;">
                        Nenhum item disponível
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<style scoped>
.max-h-48::-webkit-scrollbar {
    width: 6px;
}

.max-h-48::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.max-h-48::-webkit-scrollbar-thumb {
    background: #0f2301;
    border-radius: 4px;
}

.max-h-48::-webkit-scrollbar-thumb:hover {
    background: #3a5528;
}
</style>
