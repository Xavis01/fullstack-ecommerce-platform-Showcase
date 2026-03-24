<template>
    <div class="quantity-control font-montserrat inline-flex items-center gap-1">
        <button type="button" @click="decrement" :disabled="disabled || modelValue <= min"
            class="w-6 h-6 rounded flex items-center justify-center text-[#3a5528] hover:bg-[#0f2301]/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed">
            <Minus class="w-3 h-3" />
        </button>

        <input type="number" :value="modelValue" @input="handleInput" :min="min" :max="max" :disabled="disabled"
            class="w-8 text-center bg-transparent focus:outline-none text-[#3a5528] font-medium text-sm [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            :class="{ 'opacity-50': disabled }" />

        <button type="button" @click="increment" :disabled="disabled || modelValue >= max"
            class="w-6 h-6 rounded flex items-center justify-center text-[#3a5528] hover:bg-[#0f2301]/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed">
            <Plus class="w-3 h-3" />
        </button>
    </div>
</template>

<script setup>
import { Minus, Plus } from 'lucide-vue-next'

const props = defineProps({
    modelValue: {
        type: Number,
        default: 1
    },
    min: {
        type: Number,
        default: 1
    },
    max: {
        type: Number,
        default: 999
    },
    disabled: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['update:modelValue'])

const increment = () => {
    if (props.disabled || props.modelValue >= props.max) return
    emit('update:modelValue', props.modelValue + 1)
}

const decrement = () => {
    if (props.disabled || props.modelValue <= props.min) return
    emit('update:modelValue', props.modelValue - 1)
}

const handleInput = (event) => {
    let value = parseInt(event.target.value)
    if (isNaN(value)) {
        value = props.min
    }
    value = Math.max(props.min, Math.min(props.max, value))
    emit('update:modelValue', value)
}
</script>

<style scoped>
/* Remove number input spinners */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

input[type="number"] {
    -moz-appearance: textfield;
    appearance: textfield;
}
</style>
