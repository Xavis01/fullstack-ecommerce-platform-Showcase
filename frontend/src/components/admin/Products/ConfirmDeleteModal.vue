<script setup>
import { ref } from 'vue'
import api from '@/api'
import { useToast } from 'vue-toastification'
import { LoaderCircle } from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean,
  productId: Number,
})
const emit = defineEmits(['close', 'deleted'])

const loading = ref(false)
const toast = useToast()

async function deleteProduct() {
  loading.value = true
  try {
    await api.delete(`/admin/products/delete/${props.productId}`)
    toast.success('Produto deletado com sucesso')
    emit('deleted') // fecha e recarrega
  } catch (err) {
    toast.error('Erro ao deletar produto')
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <transition name="modal-fade">
    <div v-if="isOpen" @click="$emit('close')"
      class="fixed inset-0 z-[110] flex items-center justify-center px-4 backdrop-blur-sm bg-black/60 font-montserrat">
      <div @click.stop class="bg-white w-full max-w-md p-8 rounded-2xl shadow-2xl space-y-6 border border-[#0f2301]/10">
        <h2 class="text-xl font-light italic text-[#3a5528] text-center tracking-wide">
          Deseja realmente deletar este produto?
        </h2>
        <p class="text-sm italic text-[#3a5528]/70 text-center tracking-wide">
          (Pode ser restaurado no futuro)
        </p>
        <div class="flex justify-center gap-4">
          <button @click="emit('close')"
            class="px-6 py-3 bg-[#0f2301] text-[#fffdf2] border border-[#0f2301]/20 rounded-lg hover:bg-[#0f2301]/80 transition-all italic tracking-wide">
            Cancelar
          </button>
          <button @click="deleteProduct"
            class="px-6 py-3 bg-[#9a382d] text-[#fffdf2] rounded-lg hover:bg-[#9a382d]/90 transition-all italic tracking-wide min-w-[110px]"
            :disabled="loading">
            <span class="flex items-center justify-center gap-2">
              {{ loading ? '' : 'Confirmar' }}
              <LoaderCircle v-if="loading" class="animate-spin w-4 h-4" />
            </span>
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
