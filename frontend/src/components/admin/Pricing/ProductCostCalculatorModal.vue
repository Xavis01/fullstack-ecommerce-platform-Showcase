<script setup>
import { ref, computed, watch } from 'vue'
import { X, Calculator } from 'lucide-vue-next'

const props = defineProps({
    isOpen: Boolean,
    initialCost: Number, // Optional, maybe pre-fill product cost?
})

const emit = defineEmits(['close', 'confirm'])

// Fields
const productCost = ref(0)
const freight = ref(0)
const print = ref(0)
const labels = ref(0.48)
const graphics = ref(1.30)
const extras = ref(1.00)

// Watch open to reset or init
watch(() => props.isOpen, (val) => {
    if (val) {
        // Reset or init logic
        // If we wanted to pass current cost, we could split it, but usually it's a fresh calculation or overwrites.
        // User didn't specify editing existing calculation, just "add product... fill cost".
        // I'll keep defaults.
        productCost.value = null
        freight.value = null
        print.value = null
        labels.value = 0.48
        graphics.value = 1.30
        extras.value = 1.00
    }
})

const total = computed(() => {
    return (
        (Number(productCost.value) || 0) +
        (Number(freight.value) || 0) +
        (Number(print.value) || 0) +
        (Number(labels.value) || 0) +
        (Number(graphics.value) || 0) +
        (Number(extras.value) || 0)
    )
})

function confirm() {
    emit('confirm', total.value)
    emit('close')
}
</script>

<template>
    <transition name="modal-fade">
        <div v-if="isOpen" @click="emit('close')"
            class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[150] px-4 font-montserrat">
            <!-- Higher z-index than sidebar -->
            <div @click.stop class="bg-white p-8 rounded-xl shadow-2xl max-w-lg w-full border border-[#0f2301]/20">

                <!-- Header -->
                <div class="flex justify-between items-center mb-6 border-b border-[#0f2301]/10 pb-4">
                    <h2 class="text-xl font-light italic text-[#3a5528] flex items-center gap-2">
                        <Calculator class="w-5 h-5" />
                        Calculadora de Custo (Private Label)
                    </h2>
                    <button @click="emit('close')" class="text-[#3a5528]/50 hover:text-[#9a382d] transition-colors">
                        <X class="w-6 h-6" />
                    </button>
                </div>

                <!-- Table-like form -->
                <div class="space-y-3">

                    <!-- Headers -->
                    <div class="grid grid-cols-2 text-xs font-bold text-[#3a5528] uppercase tracking-wider mb-2">
                        <span>Matéria Prima / Serviço</span>
                        <span>Custo (R$)</span>
                    </div>

                    <!-- Row 1: Produto -->
                    <div class="grid grid-cols-2 items-center gap-4 group">
                        <label
                            class="text-sm text-[#3a5528] font-medium group-hover:text-[#0f2301] transition-colors">Custo
                            do Produto</label>
                        <div class="relative">
                            <span class="absolute left-2 top-1.5 text-[#3a5528]/50 text-xs">R$</span>
                            <input type="number" step="0.01" v-model.number="productCost"
                                class="w-full bg-[#0f2301]/20 border border-[#0f2301]/20 rounded p-1 pl-6 text-[#3a5528] focus:outline-none focus:border-[#0f2301] transition-colors text-right"
                                placeholder="0.00" autofocus />
                        </div>
                    </div>

                    <!-- Row 2: Frete -->
                    <div class="grid grid-cols-2 items-center gap-4 group">
                        <label
                            class="text-sm text-[#3a5528] font-medium group-hover:text-[#0f2301] transition-colors text-nowrap">Frete
                            Private Label</label>
                        <div class="relative">
                            <span class="absolute left-2 top-1.5 text-[#3a5528]/50 text-xs">R$</span>
                            <input type="number" step="0.01" v-model.number="freight"
                                class="w-full bg-[#0f2301]/20 border border-[#0f2301]/20 rounded p-1 pl-6 text-[#3a5528] focus:outline-none focus:border-[#0f2301] transition-colors text-right"
                                placeholder="0.00" />
                        </div>
                    </div>


                    <!-- Row 3: Estampa & Foto Still -->
                    <div class="grid grid-cols-2 items-center gap-4 group">
                        <label
                            class="text-sm text-[#3a5528] font-medium group-hover:text-[#0f2301] transition-colors text-nowrap">Estampa
                            & Foto Still</label>
                        <div class="relative">
                            <span class="absolute left-2 top-1.5 text-[#3a5528]/50 text-xs">R$</span>
                            <input type="number" step="0.01" v-model.number="print"
                                class="w-full bg-[#0f2301]/20 border border-[#0f2301]/20 rounded p-1 pl-6 text-[#3a5528] focus:outline-none focus:border-[#0f2301] transition-colors text-right"
                                placeholder="0.00" />
                        </div>
                    </div>

                    <div class="h-px bg-[#0f2301]/10 my-2"></div>

                    <!-- Row 3: Etiquetas -->
                    <div class="grid grid-cols-2 items-center gap-4">
                        <label class="text-sm text-[#3a5528]/80">Etiquetas</label>
                        <div class="relative">
                            <span class="absolute left-2 top-1.5 text-[#3a5528]/30 text-xs">R$</span>
                            <input type="number" step="0.01" v-model.number="labels"
                                class="w-full bg-transparent border-b border-dashed border-[#0f2301]/20 p-1 pl-6 text-[#3a5528]/80 focus:outline-none focus:border-[#0f2301] text-right" />
                        </div>
                    </div>

                    <!-- Row 4: Grafica -->
                    <div class="grid grid-cols-2 items-center gap-4">
                        <label class="text-sm text-[#3a5528]/80">Gráfica</label>
                        <div class="relative">
                            <span class="absolute left-2 top-1.5 text-[#3a5528]/30 text-xs">R$</span>
                            <input type="number" step="0.01" v-model.number="graphics"
                                class="w-full bg-transparent border-b border-dashed border-[#0f2301]/20 p-1 pl-6 text-[#3a5528]/80 focus:outline-none focus:border-[#0f2301] text-right" />
                        </div>
                    </div>

                    <!-- Row 5: Extras -->
                    <div class="grid grid-cols-2 items-center gap-4">
                        <label class="text-sm text-[#3a5528]/80">Extras</label>
                        <div class="relative">
                            <span class="absolute left-2 top-1.5 text-[#3a5528]/30 text-xs">R$</span>
                            <input type="number" step="0.01" v-model.number="extras"
                                class="w-full bg-transparent border-b border-dashed border-[#0f2301]/20 p-1 pl-6 text-[#3a5528]/80 focus:outline-none focus:border-[#0f2301] text-right" />
                        </div>
                    </div>

                </div>

                <!-- Total -->
                <div
                    class="mt-6 p-4 bg-[#0f2301]/30 rounded-lg flex justify-between items-center border border-[#0f2301]/10">
                    <span class="font-bold text-[#3a5528] uppercase tracking-wide text-sm">Custo Total</span>
                    <span class="font-bold text-xl text-[#3a5528]">R$ {{ total.toFixed(2) }}</span>
                </div>

                <!-- Footer Actions -->
                <div class="mt-6 flex justify-end gap-3">
                    <button @click="emit('close')"
                        class="px-5 py-2 rounded-lg text-[#3a5528] bg-transparent hover:bg-[#0f2301]/10 transition-colors text-sm font-medium">
                        Cancelar
                    </button>
                    <button @click="confirm"
                        class="px-6 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] hover:bg-[#0f2301]/90 transition-colors text-sm tracking-wide font-medium shadow-md">
                        Confirmar
                    </button>
                </div>

            </div>
        </div>
    </transition>
</template>

<style scoped>
/* Transição suave e profissional para modal */
.modal-fade-enter-active {
    transition: opacity 0.3s ease, backdrop-filter 0.3s ease;
}

.modal-fade-leave-active {
    transition: opacity 0.25s ease, backdrop-filter 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.modal-fade-enter-active>div {
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}

.modal-fade-leave-active>div {
    transition: transform 0.25s cubic-bezier(0.7, 0, 0.84, 0), opacity 0.25s ease;
}

.modal-fade-enter-from>div {
    transform: translateY(-20px);
    opacity: 0;
}

.modal-fade-leave-to>div {
    transform: translateY(-10px);
    opacity: 0;
}
</style>
