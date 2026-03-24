<template>
  <footer class="w-full bg-[#fffdf2] pt-10 pb-6 px-6 md:px-12 font-montserrat">
    <div
      class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-8 md:gap-4 mb-8">

      <!-- Esquerda: Info da Empresa -->
      <div class="flex flex-col gap-1 text-[#3a5528] text-[10px] md:text-xs font-light italic text-left">
        <p>52.645.268/0001-84</p>
        <p>Jardim Camburi - Vitória, ES</p>
        <p>29092-270</p>
      </div>

      <!-- Centro: Links Principais -->
      <div class="flex flex-col md:flex-row gap-3 md:gap-8 items-start md:items-center">
        <a href="https://www.instagram.com/roccainternazionale" target="_blank" rel="noopener noreferrer"
          class="text-[#0f2301] text-[11px] hover:text-[#3a5528] hover:underline italic transition-colors">Instagram</a>
        <a href="https://wa.me/5527996657004" target="_blank" rel="noopener noreferrer"
          class="text-[#0f2301] text-[11px] hover:text-[#3a5528] hover:underline italic transition-colors">Contact
          us</a>
        <a href="mailto:sac.rocca.internazionale@gmail.com"
          class="text-[#0f2301] text-[11px] hover:text-[#3a5528] hover:underline italic transition-colors">SAC</a>
      </div>

      <!-- Direita: Políticas -->
      <div class="flex flex-col gap-3 md:gap-2 items-start md:items-end">
        <router-link to="/politica-de-troca"
          class="text-[#0f2301] text-[11px] hover:text-[#3a5528] hover:underline italic transition-colors">Troca /
          Devolução</router-link>
        <router-link to="/politica-de-privacidade"
          class="text-[#0f2301] text-[11px] hover:text-[#3a5528] hover:underline italic transition-colors">Política de
          Privacidade</router-link>
      </div>

    </div>

    <!-- Copyright (Manteve Estilo) -->
    <div class="max-w-[800px] mx-auto text-center border-t border-black/10 pt-4">
      <span class="text-[#9A382D] text-[11px] md:text-xs italic">© 2026 Rocca Internazionale -</span>
      <span class="text-[#3a5528] text-[11px] md:text-xs italic">Desenvolvido Por Lucas Xavier</span>
    </div>
  </footer>
</template>

<style scoped>
/* Removido o CSS personalizado e adicionado Tailwind direto no template para facilitar a flexibilidade de colunas na versão mobile e desktop */
</style>