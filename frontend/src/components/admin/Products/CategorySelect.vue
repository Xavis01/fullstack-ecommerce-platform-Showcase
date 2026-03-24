<script setup>
import { ref, computed, watch } from 'vue'
import { ChevronUp, ChevronDown, Loader2 } from 'lucide-vue-next'

const props = defineProps({
    modelValue: { type: [Number, String], default: '' },
    categories: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    placeholder: { type: String, default: 'Selecione' }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const container = ref(null)

const selected = computed(() => props.categories.find(c => c.id === props.modelValue) || null)

const toggle = () => {
    if (!props.loading) isOpen.value = !isOpen.value
}

const select = (cat) => {
    emit('update:modelValue', cat.id)
    isOpen.value = false
}

const handleOutsideClick = (e) => {
    if (container.value && !container.value.contains(e.target)) {
        isOpen.value = false
    }
}

watch(isOpen, (val) => {
    if (val) setTimeout(() => document.addEventListener('click', handleOutsideClick), 0)
    else document.removeEventListener('click', handleOutsideClick)
})
</script>

<template>
    <div ref="container" class="relative">
        <!-- Trigger -->
        <button type="button" @click="toggle" :disabled="loading"
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
                :class="selected ? 'text-[#3a5528]' : 'text-[#3a5528]/40'">
                {{ selected ? selected.name : placeholder }}
            </span>
            <ChevronUp v-if="isOpen" class="w-4 h-4 text-[#3a5528] shrink-0 ml-2" />
            <ChevronDown v-else class="w-4 h-4 text-[#3a5528]/50 shrink-0 ml-2" />
        </button>

        <!-- Dropdown -->
        <Transition name="dropdown-fade">
            <div v-if="isOpen && !loading"
                class="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-[#0f2301]/20 z-50 overflow-hidden max-h-48 overflow-y-auto">
                <button type="button" v-for="cat in categories" :key="cat.id" @click="select(cat)"
                    class="w-full px-4 py-2.5 text-left text-sm tracking-wide transition-colors italic"
                    style="font-family: 'Montserrat', sans-serif;" :class="modelValue === cat.id
                        ? 'bg-[#0f2301] text-[#fffdf2] font-normal'
                        : 'text-[#3a5528] hover:bg-[#0f2301]/10'">
                    {{ cat.name }}
                </button>
                <div v-if="categories.length === 0" class="px-4 py-3 text-[#3a5528]/50 italic text-sm text-center"
                    style="font-family: 'Montserrat', sans-serif;">
                    Nenhuma categoria disponível
                </div>
            </div>
        </Transition>
    </div>
</template>

<style scoped>
.dropdown-fade-enter-active {
    transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-leave-active {
    transition: opacity 0.1s ease, transform 0.1s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
    opacity: 0;
    transform: translateY(-4px);
}
</style>
