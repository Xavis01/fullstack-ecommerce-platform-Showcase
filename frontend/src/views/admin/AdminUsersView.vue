<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/api'
import { Search, Loader2, Pencil, Trash2, UserPlus } from 'lucide-vue-next'
import UserCreateModal from '@/components/admin/Users/UserCreateModal.vue'
import UserEditModal from '@/components/admin/Users/UserEditModal.vue'
import UserDeleteModal from '@/components/admin/Users/UserDeleteModal.vue'

const users = ref([])
const loading = ref(false)
const searchTerm = ref('')
const activeTab = ref('clientes')

// Modal state
const showCreate = ref(false)
const showEdit = ref(false)
const showDelete = ref(false)
const selectedUser = ref(null)

const headers = [
    { label: 'ID', key: 'id' },
    { label: 'Nome', key: 'name' },
    { label: 'Email', key: 'email' },
    { label: 'Criado em', key: 'created_at' },
    { label: 'Ações', key: 'actions' },
]

const fetchUsers = async () => {
    loading.value = true
    try {
        const isAdmin = activeTab.value === 'admins' ? 1 : 0
        const response = await axios.get(`/admin/users/list?is_admin=${isAdmin}`)
        users.value = response.data
    } catch (error) {
        console.error('Erro ao buscar usuários:', error)
    } finally {
        loading.value = false
    }
}

const setTab = (tab) => {
    activeTab.value = tab
    searchTerm.value = ''
    fetchUsers()
}

const openEdit = (user) => {
    selectedUser.value = user
    showEdit.value = true
}

const openDelete = (user) => {
    selectedUser.value = user
    showDelete.value = true
}

const filteredUsers = computed(() => {
    if (!searchTerm.value) return users.value
    const term = searchTerm.value.toLowerCase()
    return users.value.filter(user =>
        user.name?.toLowerCase().includes(term) ||
        user.email?.toLowerCase().includes(term)
    )
})

const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date)
}

onMounted(() => {
    fetchUsers()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pb-20">
        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Usuários
            </h1>
            <p class="text-[#8c9e78] font-light">Gerencie os usuários cadastrados no sistema</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <!-- Search Bar -->
            <div class="relative group w-96">
                <input v-model="searchTerm" type="text" placeholder="Pesquisar por nome ou email..."
                    class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
                <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
            </div>

            <!-- Filter Tabs + Create Button -->
            <div class="flex gap-2 items-center">
                <button @click="setTab('clientes')" :class="[
                    'px-5 py-2 rounded-lg text-sm font-light italic tracking-wide transition-all',
                    activeTab === 'clientes'
                        ? 'bg-[#0f2301] text-[#fffdf2] shadow-sm'
                        : 'border border-[#0f2301]/40 text-[#3a5528] hover:bg-[#0f2301]/50'
                ]">
                    Clientes
                </button>
                <button @click="setTab('admins')" :class="[
                    'px-5 py-2 rounded-lg text-sm font-light italic tracking-wide transition-all',
                    activeTab === 'admins'
                        ? 'bg-[#0f2301] text-[#fffdf2] shadow-sm'
                        : 'border border-[#0f2301]/40 text-[#3a5528] hover:bg-[#0f2301]/50'
                ]">
                    Administradores
                </button>

                <!-- Divider -->
                <div class="w-px h-6 bg-[#0f2301]/20 mx-1"></div>

                <!-- Create Button -->
                <button @click="showCreate = true"
                    class="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                    <UserPlus :size="16" />
                    <span>Novo Usuário</span>
                </button>
            </div>
        </div>

        <!-- Table -->
        <div class="px-10">
            <div v-if="loading" class="flex justify-center py-20">
                <Loader2 class="animate-spin text-[#3a5528]" :size="40" />
            </div>

            <div v-else
                class="bg-white/50 backdrop-blur-sm rounded-lg overflow-hidden shadow-sm border border-[#eaddcf]">
                <table class="w-full">
                    <thead class="bg-[#e4e3db] border-b border-[#eaddcf]">
                        <tr>
                            <th v-for="header in headers" :key="header.key"
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                {{ header.label }}
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#eaddcf]">
                        <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
                            <td class="py-4 px-6 text-[#3a5528] font-light text-sm">#{{ user.id }}</td>
                            <td class="py-4 px-6 text-[#3a5528] font-medium">{{ user.name }}</td>
                            <td class="py-4 px-6 text-[#6b8555] font-light">{{ user.email }}</td>
                            <td class="py-4 px-6 text-[#6b8555] font-light text-sm">{{ formatDate(user.created_at) }}
                            </td>
                            <!-- Ações -->
                            <td class="py-4 px-6">
                                <div class="flex items-center gap-3">
                                    <button @click="openEdit(user)"
                                        class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                                        title="Editar">
                                        <Pencil :size="17" />
                                    </button>
                                    <button @click="openDelete(user)"
                                        class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1"
                                        title="Excluir">
                                        <Trash2 :size="17" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="filteredUsers.length === 0">
                            <td colspan="5" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhum usuário encontrado.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <UserCreateModal :isOpen="showCreate" @close="showCreate = false" @created="fetchUsers" />

        <UserEditModal :isOpen="showEdit" :user="selectedUser" @close="showEdit = false" @updated="fetchUsers" />

        <UserDeleteModal :isOpen="showDelete" :user="selectedUser" @close="showDelete = false" @deleted="fetchUsers" />
    </div>
</template>

<style scoped>
.user-row {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

.user-row:hover {
    background-color: #f0efe9;
}
</style>
