<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'
import { X, LogOut, PackageSearch, Settings, Home, Star, Archive } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useToast } from 'vue-toastification'

const props = defineProps({
    visible: Boolean,
    userName: {
        type: String,
        default: 'Cliente'
    }
})

const emit = defineEmits(['close', 'logout', 'request-login'])
const router = useRouter()
const userStore = useUserStore()
const toast = useToast()

const navItems = [
    { label: 'Home', path: '/', icon: Home },
    { label: 'Destaques', path: null, icon: Star, action: 'destaques' },
    { label: 'Archive', path: '/archive', icon: Archive },
]

const menuItems = [
    { label: 'Meus Pedidos', path: '/meus-pedidos', icon: PackageSearch },
    { label: 'Minha Conta', path: '/minha-conta', icon: Settings },
]

const totalAnimItems = navItems.length + menuItems.length
const showItems = ref(new Array(totalAnimItems).fill(false))

const handleLogout = () => {
    emit('close')
    emit('logout')
}

const handleNavClick = (item) => {
    if (item.action === 'destaques') {
        emit('close')
        // Navigate to home then scroll to destaques
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

const handleMenuClick = (item) => {
    if (!userStore.is_logged) {
        emit('close')
        emit('request-login')
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
        showItems.value = showItems.value.map(() => false)

        Array.from({ length: totalAnimItems }).forEach((_, index) => {
            setTimeout(() => {
                showItems.value[index] = true
            }, 200 + (index * 100))
        })
    } else {
        setTimeout(() => {
            showItems.value = showItems.value.map(() => false)
        }, 500)
    }
})
</script>

<template>
    <div>
        <!-- Overlay -->
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
                class="fixed top-0 left-0 md:left-auto md:right-0 h-full w-[85vw] max-w-[320px] md:w-80 bg-[#fffdf2] z-[110] shadow-2xl p-8 md:p-10 flex flex-col">

                <!-- Header / Close -->
                <div class="flex justify-between items-center mb-8 md:mb-10">
                    <div>
                        <p class="text-sm font-light text-[#8c9e78] mb-1">Olá,</p>
                        <h2
                            class="text-lg md:text-xl font-medium font-['Montserrat'] italic text-[#3a5528] truncate max-w-[180px] md:max-w-[200px]">
                            {{ userName }}
                        </h2>
                    </div>
                    <button @click="$emit('close')"
                        class="text-[#3a5528] hover:opacity-60 transition-opacity hover:rotate-90 duration-300">
                        <X :size="28" :stroke-width="1.5" />
                    </button>
                </div>

                <div class="w-full h-px bg-[#eaddcf] mb-6 md:mb-10"></div>

                <!-- Navigation Links -->
                <nav class="flex flex-col gap-5 md:gap-6">
                    <!-- Nav items: Home, Destaques, Arquivo -->
                    <template v-for="(item, index) in navItems" :key="'nav-' + index">
                        <Transition enter-active-class="transition-all duration-700 ease-out"
                            enter-from-class="opacity-0 translate-x-12" enter-to-class="opacity-100 translate-x-0"
                            leave-active-class="transition-all duration-300 ease-in"
                            leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-12">
                            <button v-if="showItems[index]" @click="handleNavClick(item)"
                                class="flex items-center gap-4 text-base md:text-lg font-['Montserrat'] italic text-[#3a5528] font-light tracking-wide group cursor-pointer hover:opacity-70 transition-transform duration-300 hover:translate-x-2 text-left">
                                <component :is="item.icon" class="w-5 h-5 text-[#0f2301]" />
                                <span>{{ item.label }}</span>
                            </button>
                        </Transition>
                    </template>

                    <!-- Divider -->
                    <div class="w-full h-px bg-[#eaddcf]"></div>

                    <!-- Menu items: Meus Pedidos, Minha Conta -->
                    <template v-for="(item, index) in menuItems" :key="'menu-' + index">
                        <Transition enter-active-class="transition-all duration-700 ease-out"
                            enter-from-class="opacity-0 translate-x-12" enter-to-class="opacity-100 translate-x-0"
                            leave-active-class="transition-all duration-300 ease-in"
                            leave-from-class="opacity-100 translate-x-0" leave-to-class="opacity-0 translate-x-12">
                            <button v-if="showItems[navItems.length + index]" @click="handleMenuClick(item)"
                                class="flex items-center gap-4 text-base md:text-lg font-['Montserrat'] italic text-[#3a5528] font-light tracking-wide group cursor-pointer hover:opacity-70 transition-transform duration-300 hover:translate-x-2 text-left">
                                <component :is="item.icon" class="w-5 h-5 text-[#0f2301]" />
                                <span>{{ item.label }}</span>
                            </button>
                        </Transition>
                    </template>
                </nav>

                <!-- Footer / Logout -->
                <div v-if="userStore.is_logged"
                    class="mt-auto pt-6 border-t border-[#eaddcf] transition-opacity duration-700"
                    :class="showItems[totalAnimItems - 1] ? 'opacity-100' : 'opacity-0'">
                    <button @click="handleLogout"
                        class="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-[#9a382d] font-light italic tracking-wide hover:bg-red-50 transition-colors border border-transparent hover:border-red-200">
                        <LogOut :size="18" /> Sair da conta
                    </button>
                </div>
            </aside>
        </Transition>
    </div>
</template>

<style scoped>
@keyframes fadeIn {
    to {
        opacity: 1;
    }
}
</style>
