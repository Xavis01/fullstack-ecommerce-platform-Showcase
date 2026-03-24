<template>
    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0"
        enter-to-class="opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div v-if="visible"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div
                class="bg-[#fffdf2] rounded-lg shadow-xl max-w-md w-full p-6 border border-[#0f2301] transform transition-all scale-100">

                <h3 class="text-xl font-bold text-[#3a5528] mb-4 font-montserrat uppercase tracking-wider text-center">
                    Tem certeza?
                </h3>

                <p class="text-gray-700 text-center mb-8">
                    Isso removerá <strong>todos</strong> os itens do seu carrinho. Essa ação não pode ser desfeita.
                </p>

                <div class="flex gap-4 justify-center">
                    <button @click="$emit('close')"
                        class="px-6 py-2 border border-[#0f2301] text-[#fffdf2] rounded bg-[#0f2301] hover:bg-[#3a5528] hover:text-[#fffdf2] transition-colors font-medium uppercase text-sm tracking-wide">
                        Cancelar
                    </button>

                    <button @click="confirm"
                        class="px-6 py-2 bg-[#9a382d] text-white rounded hover:bg-[#7a2c24] transition-colors font-medium uppercase text-sm tracking-wide flex items-center gap-2"
                        :disabled="loading">
                        <LoaderCircle v-if="loading" class="w-4 h-4 animate-spin" />
                        <span v-else>Sim, Esvaziar</span>
                    </button>
                </div>

            </div>
        </div>
    </Transition>
</template>

<script setup>
import { ref } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'

const props = defineProps({
    visible: Boolean,
    loading: Boolean
})

const emit = defineEmits(['close', 'confirm'])

const confirm = () => {
    emit('confirm')
}
</script>
