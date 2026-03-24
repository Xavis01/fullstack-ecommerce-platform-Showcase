<template>
    <div class="min-h-screen bg-[#fffdf2] font-['Montserrat',sans-serif] pb-16 md:pb-24">

        <!-- Header -->
        <div class="bg-[#0f2301] px-5 pt-14 pb-10 md:pt-20 md:pb-16">
            <div class="max-w-3xl mx-auto text-center">
                <span class="text-[#8c9e78] text-[10px] uppercase tracking-[0.5em] font-bold block mb-3">Rocca
                    Internazionale</span>
                <h1 class="text-2xl sm:text-3xl md:text-4xl font-light italic text-[#fffdf2] tracking-wide mb-3">
                    Política de Troca e Devolução
                </h1>
                <p class="text-[#8c9e78] font-light text-sm max-w-xl mx-auto leading-relaxed">
                    Seguimos rigorosamente as diretrizes do Código de Defesa do Consumidor para garantir a melhor
                    experiência de compra.
                </p>
            </div>
        </div>

        <!-- Divider accent -->
        <div class="h-1 bg-gradient-to-r from-[#3a5528] via-[#8c9e78] to-[#3a5528]"></div>

        <div class="max-w-3xl mx-auto px-4 sm:px-6">

            <!-- ─── SEÇÃO 1: Arrependimento ─── -->
            <section class="mt-10 mb-10 md:mt-14">
                <div class="flex items-center gap-3 mb-5">
                    <div class="w-8 h-8 rounded-full bg-[#3a5528]/10 flex items-center justify-center flex-shrink-0">
                        <RotateCcw class="w-4 h-4 text-[#3a5528]" />
                    </div>
                    <h2 class="text-lg sm:text-xl font-light italic text-[#0f2301] tracking-wide leading-tight">
                        Troca ou Devolução por Arrependimento
                    </h2>
                </div>

                <!-- Fluxo visual -->
                <div class="bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 mb-5 shadow-sm">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-[#8c9e78] mb-4">Como solicitar</p>
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <!-- Step: Meus Pedidos -->
                        <div
                            class="flex flex-col items-center justify-center text-center text-[10px] font-semibold uppercase tracking-[0.05em] text-[#3a5528] bg-[#f5f2e8] border border-[#eaddcf] rounded-xl px-3 py-2 min-w-[75px]">
                            <ShoppingBag class="w-3.5 h-3.5 text-[#3a5528] mb-1 mx-auto" />
                            <span>Meus Pedidos</span>
                        </div>
                        <ChevronRight class="w-4 h-4 text-[#8c9e78] flex-shrink-0" />
                        <!-- Step: Detalhes -->
                        <div
                            class="flex flex-col items-center justify-center text-center text-[10px] font-semibold uppercase tracking-[0.05em] text-[#3a5528] bg-[#f5f2e8] border border-[#eaddcf] rounded-xl px-3 py-2 min-w-[75px]">
                            <FileText class="w-3.5 h-3.5 text-[#3a5528] mb-1 mx-auto" />
                            <span>Detalhes do Pedido</span>
                        </div>
                        <ChevronRight class="w-4 h-4 text-[#8c9e78] flex-shrink-0" />
                        <!-- Step: Solicitar (active) -->
                        <div
                            class="flex flex-col items-center justify-center text-center text-[10px] font-semibold uppercase tracking-[0.05em] text-[#fffdf2] bg-[#0f2301] border border-[#0f2301] rounded-xl px-3 py-2 min-w-[75px]">
                            <ArrowLeftRight class="w-3.5 h-3.5 text-[#fffdf2] mb-1 mx-auto" />
                            <span>Solicitar Troca / Devolução</span>
                        </div>
                    </div>
                    <p class="text-xs text-[#8c9e78] font-light italic mt-4">
                        Nossa equipe realizará o atendimento pelo WhatsApp após o contato.
                    </p>
                </div>

                <!-- Prazo -->
                <div
                    class="flex items-start gap-4 bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 shadow-sm mb-4">
                    <div class="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Clock class="w-4 h-4 text-blue-500" />
                    </div>
                    <div class="min-w-0">
                        <h3 class="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8c9e78] mb-1.5">Prazo para
                            solicitação</h3>
                        <p class="text-sm text-[#3a5528] font-light leading-relaxed">
                            Conforme o <strong>Art. 49 do Código de Defesa do Consumidor</strong>, você tem até
                            <strong>7 (sete) dias corridos</strong> após o recebimento do produto para solicitar a
                            devolução, sem necessidade de justificativa.
                        </p>
                    </div>
                </div>

                <!-- Condições -->
                <div
                    class="flex items-start gap-4 bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 shadow-sm mb-4">
                    <div class="w-9 h-9 rounded-full bg-amber-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <CheckCircle class="w-4 h-4 text-amber-500" />
                    </div>
                    <div class="min-w-0">
                        <h3 class="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8c9e78] mb-1.5">Condições
                            para devolução</h3>
                        <ul class="text-sm text-[#3a5528] font-light leading-relaxed space-y-1 list-none">
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Produto sem sinais de uso
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Embalagem original preservada
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Etiquetas, acessórios e itens enviados no pedido inclusos
                            </li>
                        </ul>
                    </div>
                </div>

                <!-- Reembolso -->
                <div class="flex items-start gap-4 bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 shadow-sm">
                    <div class="w-9 h-9 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Banknote class="w-4 h-4 text-green-600" />
                    </div>
                    <div class="min-w-0">
                        <h3 class="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8c9e78] mb-1.5">Reembolso
                        </h3>
                        <p class="text-sm text-[#3a5528] font-light leading-relaxed mb-2">
                            Após o recebimento e análise do produto devolvido, o reembolso será realizado em até
                            <strong>5 dias úteis</strong> conforme a forma de pagamento:
                        </p>
                        <ul class="text-sm text-[#3a5528] font-light leading-relaxed space-y-1">
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Estorno no cartão de crédito
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Reembolso via PIX ou transferência bancária
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Vale-compra, caso o cliente prefira
                            </li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Divider -->
            <div class="border-t border-[#eaddcf] my-8"></div>

            <!-- ─── SEÇÃO 2: Defeito no Produto ─── -->
            <section class="mb-12">
                <div class="flex items-center gap-3 mb-5">
                    <div class="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0">
                        <AlertTriangle class="w-4 h-4 text-red-500" />
                    </div>
                    <h2 class="text-lg sm:text-xl font-light italic text-[#0f2301] tracking-wide leading-tight">
                        Troca ou Devolução por Defeito no Produto
                    </h2>
                </div>

                <!-- Fluxo visual -->
                <div class="bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 mb-5 shadow-sm">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-[#8c9e78] mb-4">Como solicitar</p>
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <!-- Step: Meus Pedidos -->
                        <div
                            class="flex flex-col items-center justify-center text-center text-[10px] font-semibold uppercase tracking-[0.05em] text-[#3a5528] bg-[#f5f2e8] border border-[#eaddcf] rounded-xl px-3 py-2 min-w-[75px]">
                            <ShoppingBag class="w-3.5 h-3.5 text-[#3a5528] mb-1 mx-auto" />
                            <span>Meus Pedidos</span>
                        </div>
                        <ChevronRight class="w-4 h-4 text-[#8c9e78] flex-shrink-0" />
                        <!-- Step: Detalhes -->
                        <div
                            class="flex flex-col items-center justify-center text-center text-[10px] font-semibold uppercase tracking-[0.05em] text-[#3a5528] bg-[#f5f2e8] border border-[#eaddcf] rounded-xl px-3 py-2 min-w-[75px]">
                            <FileText class="w-3.5 h-3.5 text-[#3a5528] mb-1 mx-auto" />
                            <span>Detalhes do Pedido</span>
                        </div>
                        <ChevronRight class="w-4 h-4 text-[#8c9e78] flex-shrink-0" />
                        <!-- Step: Solicitar (active) -->
                        <div
                            class="flex flex-col items-center justify-center text-center text-[10px] font-semibold uppercase tracking-[0.05em] text-[#fffdf2] bg-[#0f2301] border border-[#0f2301] rounded-xl px-3 py-2 min-w-[75px]">
                            <ArrowLeftRight class="w-3.5 h-3.5 text-[#fffdf2] mb-1 mx-auto" />
                            <span>Solicitar Troca / Devolução</span>
                        </div>
                    </div>
                    <p class="text-xs text-[#8c9e78] font-light italic mt-4">
                        Nossa equipe realizará o atendimento pelo WhatsApp após o contato.
                    </p>
                </div>

                <!-- Prazo legal -->
                <div
                    class="flex items-start gap-4 bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 shadow-sm mb-4">
                    <div class="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Clock class="w-4 h-4 text-blue-500" />
                    </div>
                    <div class="min-w-0">
                        <h3 class="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8c9e78] mb-1.5">Prazo legal
                            (CDC)</h3>
                        <p class="text-sm text-[#3a5528] font-light leading-relaxed">
                            O prazo para reclamação de defeito é garantido pelo Código de Defesa do Consumidor:
                        </p>
                        <ul class="text-sm text-[#3a5528] font-light leading-relaxed space-y-1 mt-2">
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                <span><strong>30 dias</strong> para produtos não duráveis</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                <span><strong>90 dias</strong> para produtos duráveis</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <!-- Avaliação -->
                <div
                    class="flex items-start gap-4 bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 shadow-sm mb-4">
                    <div class="w-9 h-9 rounded-full bg-amber-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Search class="w-4 h-4 text-amber-500" />
                    </div>
                    <div class="min-w-0">
                        <h3 class="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8c9e78] mb-1.5">Avaliação
                            do caso</h3>
                        <p class="text-sm text-[#3a5528] font-light leading-relaxed">
                            Após o contato, nossa equipe analisará o defeito relatado e indicará a melhor solução:
                        </p>
                        <ul class="text-sm text-[#3a5528] font-light leading-relaxed space-y-1 mt-2">
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Troca por produto idêntico ou equivalente
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Reembolso integral do valor pago
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="text-[#3a5528] mt-0.5">•</span>
                                Abatimento proporcional no preço
                            </li>
                        </ul>
                    </div>
                </div>

                <!-- Contato -->
                <div class="flex items-start gap-4 bg-white border border-[#eaddcf] rounded-2xl p-4 sm:p-5 shadow-sm">
                    <div class="w-9 h-9 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <MessageCircle class="w-4 h-4 text-green-600" />
                    </div>
                    <div class="min-w-0 w-full">
                        <h3 class="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8c9e78] mb-1.5">Contato do
                            SAC</h3>
                        <p class="text-sm text-[#3a5528] font-light leading-relaxed mb-3">
                            Também pode entrar em contato diretamente com nossa equipe:
                        </p>
                        <div class="flex flex-col gap-2">
                            <a href="https://wa.me/5527996657004" target="_blank" rel="noopener noreferrer"
                                class="inline-flex items-center gap-2 text-sm text-[#3a5528] font-medium hover:underline underline-offset-4 active:opacity-70">
                                <MessageCircle class="w-4 h-4 flex-shrink-0" />
                                WhatsApp: (27) 99665-7004
                            </a>
                            <a href="mailto:sac.rocca.internazionale@gmail.com"
                                class="inline-flex items-center gap-2 text-sm text-[#3a5528] font-medium hover:underline underline-offset-4 active:opacity-70 break-all">
                                <Mail class="w-4 h-4 flex-shrink-0" />
                                sac.rocca.internazionale@gmail.com
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            <!-- CTA -->
            <div class="bg-[#0f2301] rounded-2xl p-6 sm:p-8 text-center mb-8">
                <h3 class="text-lg font-light italic text-[#fffdf2] mb-2">Precisa de ajuda?</h3>
                <p class="text-[#8c9e78] text-sm font-light mb-5">Nossa equipe está pronta para te atender.</p>
                <a href="https://wa.me/5527996657004?text=Ol%C3%A1!%20Preciso%20de%20ajuda%20com%20uma%20troca%20ou%20devolu%C3%A7%C3%A3o."
                    target="_blank" rel="noopener noreferrer"
                    class="inline-flex items-center justify-center gap-2.5 w-full sm:w-auto bg-[#25D366] text-white px-8 py-3.5 rounded-xl font-medium tracking-wide hover:bg-[#1da851] active:scale-95 transition-all shadow-md text-sm">
                    <MessageCircle class="w-4 h-4" />
                    Falar com o SAC pelo WhatsApp
                </a>
            </div>

            <!-- Back link -->
            <div class="text-center pb-4">
                <router-link to="/"
                    class="text-[#8c9e78] hover:text-[#3a5528] text-sm font-light italic underline underline-offset-4 transition-colors">
                    ← Voltar para a loja
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    RotateCcw, Clock, CheckCircle, Banknote, AlertTriangle,
    Search, MessageCircle, Mail, ChevronRight, ShoppingBag,
    FileText, ArrowLeftRight
} from 'lucide-vue-next'
</script>
