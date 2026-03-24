<template>
    <div class="min-h-screen bg-[#fffdf2] font-montserrat pt-32 px-4 sm:px-6 lg:px-8 flex items-start justify-center">
        <div
            class="max-w-md w-full bg-white/50 backdrop-blur-sm p-8 rounded-2xl shadow-xl text-center border border-[#eaddcf] relative overflow-hidden h-fit">
            <div class="absolute top-0 left-0 w-full h-2 bg-[#0f2301]"></div>

            <div
                class="w-20 h-20 bg-[#0f2301] rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border border-[#0f2301]/20">
                <SearchX class="w-10 h-10 text-[#fffdf2]" />
            </div>

            <h1 class="text-4xl font-['Montserrat'] font-light text-[#3a5528] italic mb-2 tracking-tighter">404</h1>
            <h2 class="text-xl font-['Montserrat'] font-light text-[#0f2301] italic mb-4 tracking-wide">Página não
                encontrada</h2>

            <p class="text-[#8c9e78] font-light text-sm mb-8 leading-relaxed">
                Ops! Parece que o pacote que você está procurando não está por aqui.
                Pode ter sido removido ou o endereço digitado está incorreto.
            </p>

            <div class="space-y-3">
                <router-link to="/"
                    class="block w-full bg-[#0f2301] text-[#fffdf2] py-3 rounded-xl font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                    Voltar para o Início
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { SearchX } from 'lucide-vue-next'
</script>

<style scoped>
.font-montserrat {
    font-family: 'Montserrat', sans-serif;
}
</style>
