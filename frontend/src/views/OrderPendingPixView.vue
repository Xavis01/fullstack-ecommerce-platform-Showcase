<template>
    <div
        class="min-h-screen bg-[#fffdf2] font-montserrat pt-10 pb-20 px-4 sm:px-6 lg:px-8 flex items-start justify-center">
        <div
            class="max-w-lg w-full bg-white/50 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-[#eaddcf] relative overflow-hidden h-fit">
            <div class="absolute top-0 left-0 w-full h-2 bg-[#3a5528]"></div>
            <div class="text-center mb-8">
                <div
                    class="w-16 h-16 bg-[#fffdf2 ] rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm border border-[#0f2301]/20">
                    <QrCode class="w-8 h-8 text-[#0f2301]" />
                </div>
                <h1 class="text-2xl font-['Montserrat'] font-light italic text-[#3a5528] mb-2 tracking-wide">Finalize
                    seu pagamento com Pix</h1>
                <p class="text-[#8c9e78] text-sm font-light">Escaneie o QR Code ou copie o código Pix abaixo para
                    realizar o
                    pagamento no aplicativo do seu banco.</p>
            </div>

            <div v-if="pixData" class="space-y-6">
                <!-- QR Code -->
                <div class="flex justify-center p-4 border border-[#eaddcf] rounded-xl bg-white shadow-sm">
                    <img :src="'data:image/jpeg;base64,' + pixData.point_of_interaction.transaction_data.qr_code_base64"
                        alt="QR Code Pix" class="w-48 h-48 object-contain" />
                </div>

                <!-- Copia e Cola -->
                <div class="space-y-2">
                    <label class="block text-sm font-medium italic text-[#3a5528]">Código Pix (Copia e Cola)</label>
                    <div class="flex shadow-sm rounded-md">
                        <input type="text" readonly :value="pixData.point_of_interaction.transaction_data.qr_code"
                            class="flex-1 block w-full rounded-l-md border-[#eaddcf] bg-white px-4 py-3 text-sm focus:border-[#0f2301] focus:ring-[#0f2301] font-mono text-[#3a5528] truncate" />
                        <button @click="copyCode"
                            class="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-[#eaddcf] bg-[#0f2301] px-4 py-2 text-sm font-light italic tracking-wide text-[#fffdf2] hover:bg-[#3a5528] transition-colors">
                            <Copy class="w-4 h-4" />
                            <span>Copiar</span>
                        </button>
                    </div>
                </div>

                <div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mt-6 flex gap-3 shadow-sm">
                    <p class="text-sm text-yellow-800 font-light">
                        Aguardando a confirmação do pagamento. O seu pacote será liberado assim que o valor for
                        creditado!
                    </p>
                </div>
            </div>

            <div v-else class="text-center py-10">
                <p class="text-[#8c9e78] font-light italic">Dados do PIX não encontrados. Ocorreu um erro.</p>
            </div>

            <div class="mt-8 text-center border-t pt-6 border-[#eaddcf]">
                <router-link to="/"
                    class="text-sm font-light italic tracking-wide text-[#8c9e78] hover:text-[#3a5528] transition-colors">
                    Voltar para a loja
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { QrCode, Copy } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import api from '@/api'

const toast = useToast()
const router = useRouter()
const pixData = ref(null)
const pollingInterval = ref(null)

const checkStatus = async () => {
    // Tenta pegar o ID do pedido do sessionStorage primeiro, depois do pixData
    const orderId = sessionStorage.getItem('lastOrderId') || pixData.value?.external_reference

    if (!orderId) {
        console.log("PIX DEBUG: orderId não encontrado para polling")
        return
    }

    try {
        console.log("PIX DEBUG: verificando status do pedido", orderId)
        const res = await api.get(`/user/orders/${orderId}/status`)
        console.log("PIX DEBUG: resposta", res.data)

        if (res.data.status === 'approved' || res.data.status === 'paid' || res.data.is_paid) {
            console.log("PIX DEBUG: aprovado! redirecionando...")
            if (pollingInterval.value) {
                clearInterval(pollingInterval.value)
                pollingInterval.value = null
            }
            toast.success('Pagamento aprovado!')
            router.push('/checkout/sucesso')
        }
    } catch (err) {
        console.error('Erro ao verificar status do pagamento:', err)
    }
}

onMounted(() => {
    const data = sessionStorage.getItem('pendingPix')
    const lastOrderId = sessionStorage.getItem('lastOrderId')

    console.log("PIX DEBUG: mounted. pendingPix exists:", !!data, "lastOrderId:", lastOrderId)

    if (data) {
        try {
            pixData.value = JSON.parse(data)

            // Inicia polling se tivermos o ID do pedido
            if (lastOrderId || pixData.value.external_reference) {
                pollingInterval.value = setInterval(checkStatus, 5000)
                // Faz a primeira checagem imediata
                checkStatus()
            }
        } catch (e) {
            console.error(e)
        }
    }
})

onBeforeUnmount(() => {
    if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
        pollingInterval.value = null
    }
})

const copyCode = () => {
    if (pixData.value?.point_of_interaction?.transaction_data?.qr_code) {
        navigator.clipboard.writeText(pixData.value.point_of_interaction.transaction_data.qr_code)
        toast.success('Código PIX copiado!')
    }
}
</script>
