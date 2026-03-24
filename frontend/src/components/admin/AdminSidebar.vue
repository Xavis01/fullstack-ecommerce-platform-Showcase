<!-- src/components/admin/AdminSidebar.vue -->
<template>
    <div>
        <!-- Overlay Escuro -->
        <Transition enter-active-class="transition-opacity duration-300 ease-out" enter-from-class="opacity-0"
            enter-to-class="opacity-100" leave-active-class="transition-opacity duration-300 ease-in"
            leave-from-class="opacity-100" leave-to-class="opacity-0">
            <div v-if="visible" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[110]" @click="$emit('close')">
            </div>
        </Transition>

        <!-- Sidebar -->
        <Transition enter-active-class="transition-transform duration-500 ease-out"
            enter-from-class="-translate-x-full md:translate-x-full" enter-to-class="translate-x-0"
            leave-active-class="transition-transform duration-500 ease-in" leave-from-class="translate-x-0"
            leave-to-class="-translate-x-full md:translate-x-full">
            <aside v-if="visible"
                class="fixed top-0 left-0 md:left-auto md:right-0 h-full w-[85vw] max-w-[320px] md:w-80 bg-[#fffdf2] z-[110] shadow-2xl p-8 md:p-10 flex flex-col overflow-y-auto">
                <!-- Header / Close Button -->
                <div class="flex justify-between items-center mb-5">
                    <div>
                        <div class="flex items-baseline gap-2">
                            <p class="text-sm font-light text-[#8c9e78]">Olá,</p>
                            <h2
                                class="text-lg md:text-xl font-medium font-['Montserrat'] italic text-[#3a5528] truncate max-w-[150px] md:max-w-[200px]">
                                {{ userName }}
                            </h2>
                        </div>
                        <span
                            class="inline-block mt-1 bg-[#0f2301] text-white text-[9px] px-1.5 py-0.5 rounded-sm font-bold uppercase not-italic tracking-wider">
                            Admin
                        </span>
                    </div>
                    <button @click="$emit('close')"
                        class="text-[#3a5528] hover:opacity-60 transition-opacity hover:rotate-90 duration-300">
                        <X :size="28" :stroke-width="1.5" />
                    </button>
                </div>

                <div v-show="visible"
                    class="w-full h-[1px] min-h-[1px] shrink-0 bg-[#eaddcf] transition-opacity duration-700 delay-50"
                    :class="showItems[0] ? 'opacity-100' : 'opacity-0'"></div>

                <!-- Navigation Links (mobile only: Home, Destaques, Arquivo) -->
                <nav class="flex mt-6 md:mt-8 flex-col gap-5 md:gap-6">
                    <div class="md:hidden flex flex-col gap-5">
                        <template v-for="(item, index) in navItems" :key="'nav-' + index">
                            <Transition enter-active-class="transition-all duration-700 ease-out"
                                enter-from-class="opacity-0 translate-x-12" enter-to-class="opacity-100 translate-x-0"
                                leave-active-class="transition-all duration-300 ease-in"
                                leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-12">
                                <button v-if="showItems[index]" @click="handleNavClick(item)"
                                    class="flex items-center gap-4 text-base font-['Montserrat'] italic text-[#3a5528] font-light tracking-wide group cursor-pointer hover:opacity-70 transition-transform duration-300 hover:translate-x-2 text-left">
                                    <component :is="item.icon" class="w-5 h-5 text-[#0f2301]" />
                                    <span>{{ item.label }}</span>
                                </button>
                            </Transition>
                        </template>

                        <!-- Divider -->
                        <div v-show="visible"
                            class="w-full h-[1px] min-h-[1px] shrink-0 bg-[#eaddcf] transition-opacity duration-700 delay-300"
                            :class="showItems[0] ? 'opacity-100' : 'opacity-0'"></div>
                    </div>

                    <!-- Admin Links -->
                    <template v-for="(item, index) in adminMenuItems" :key="'admin-' + index">
                        <!-- Wrapper Transition for specific entry animation -->
                        <Transition enter-active-class="transition-all duration-700 ease-out"
                            enter-from-class="opacity-0 translate-x-12" enter-to-class="opacity-100 translate-x-0"
                            leave-active-class="transition-all duration-300 ease-in"
                            leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-12">
                            <component v-if="showItems[navItems.length + index]" :is="item.path ? 'router-link' : 'div'"
                                :to="item.path" @click="item.path ? $emit('close') : null"
                                class="text-base md:text-xl font-['Montserrat'] italic text-[#3a5528] font-light tracking-wide flex items-center justify-between group cursor-pointer hover:opacity-70 transition-transform duration-300 hover:translate-x-2"
                                :class="{ 'opacity-50 cursor-not-allowed hover:translate-x-0 hover:opacity-50': !item.path }">
                                <span>{{ item.label }}</span>
                            </component>
                        </Transition>
                    </template>

                    <!-- Divider -->
                    <div v-show="visible"
                        class="w-full h-[1px] min-h-[1px] shrink-0 bg-[#eaddcf] transition-opacity duration-700 delay-500"
                        :class="showItems[0] ? 'opacity-100' : 'opacity-0'"></div>

                    <!-- User Items for Admin -->
                    <template v-for="(item, index) in userMenuItems" :key="'user-' + index">
                        <Transition enter-active-class="transition-all duration-700 ease-out"
                            enter-from-class="opacity-0 translate-x-12" enter-to-class="opacity-100 translate-x-0"
                            leave-active-class="transition-all duration-300 ease-in"
                            leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-12">
                            <router-link v-if="showItems[navItems.length + adminMenuItems.length + index]"
                                :to="item.path" @click="$emit('close')"
                                class="flex items-center gap-4 text-base md:text-lg font-['Montserrat'] italic text-[#3a5528] font-light tracking-wide group cursor-pointer hover:opacity-70 transition-transform duration-300 hover:translate-x-2">
                                <component :is="item.icon" class="w-5 h-5 text-[#0f2301]" />
                                <span>{{ item.label }}</span>
                            </router-link>
                        </Transition>
                    </template>
                </nav>

                <!-- Footer / Logout -->
                <div class="mt-auto pt-6 border-t border-[#eaddcf] transition-opacity duration-700"
                    :class="showItems[totalItems - 1] ? 'opacity-100' : 'opacity-0'">
                    <button @click="handleLogout"
                        class="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-[#9a382d] font-light italic tracking-wide hover:bg-red-50 transition-colors border border-transparent hover:border-red-200">
                        <LogOut :size="18" /> Sair da conta
                    </button>
                </div>
            </aside>
        </Transition>
    </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'
import { X, PackageSearch, Settings, LogOut, Home, Star, Archive } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const props = defineProps({
    visible: Boolean,
    userName: {
        type: String,
        default: 'Administrador'
    }
})

const emit = defineEmits(['close', 'logout'])
const router = useRouter()
const toast = useToast()

const navItems = [
    { label: 'Home', path: '/', icon: Home },
    { label: 'Destaques', path: null, icon: Star, action: 'destaques' },
    { label: 'Archive', path: '/archive', icon: Archive },
]

const adminMenuItems = [
    { label: 'Gerenciar Produtos', path: '/admin/produtos' },
    { label: 'Categorias', path: '/admin/categorias' },
    { label: 'Coleções', path: '/admin/colecoes' },
    { label: 'Descontos', path: null },
    { label: 'Cupons', path: '/admin/cupons' },
    { label: 'Pedidos', path: '/admin/pedidos' },
    { label: 'Frete', path: '/admin/frete' },
    { label: 'Usuários', path: '/admin/usuarios' },
    { label: 'Precificação', path: '/admin/precificacao' },
    { label: 'Venda Rápida', path: '/admin/venda-rapida' },
]

const userMenuItems = [
    { label: 'Meus Pedidos', path: '/meus-pedidos', icon: PackageSearch },
    { label: 'Minha Conta', path: '/minha-conta', icon: Settings },
]

const totalItems = navItems.length + adminMenuItems.length + userMenuItems.length
const showItems = ref(new Array(totalItems).fill(false))

const handleLogout = () => {
    emit('close')
    emit('logout')
}

const handleNavClick = (item) => {
    if (item.action === 'destaques') {
        emit('close')
        const currentPath = router.currentRoute.value.path
        if (currentPath !== '/') {
            router.push('/').then(() => {
                setTimeout(() => {
                    const el = document.getElementById('destaques')
                    if (el) el.scrollIntoView({ behavior: 'smooth' })
                }, 400)
            })
        } else {
            const el = document.getElementById('destaques')
            if (el) el.scrollIntoView({ behavior: 'smooth' })
        }
        return
    }
    if (item.path) {
        router.push(item.path)
        emit('close')
    }
}

watch(() => props.visible, (newVal) => {
    if (newVal) {
        toast.clear()
        // Ensure all hidden initially
        showItems.value = showItems.value.map(() => false)

        // Staggered sequence
        Array.from({ length: totalItems }).forEach((_, index) => {
            setTimeout(() => {
                showItems.value[index] = true
            }, 200 + (index * 100)) // Wait for sidebar (500ms) then cascade
        })
    } else {
        // Reset on close
        setTimeout(() => {
            showItems.value = showItems.value.map(() => false)
        }, 500)
    }
})
</script>

<style scoped>
@keyframes fadeIn {
    to {
        opacity: 1;
    }
}
</style>
