<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { Search, Loader2, Pencil, Trash2 } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import CategoryModal from '@/components/admin/CategoryModal.vue'
import ConfirmDeleteCategoryModal from '@/components/admin/ConfirmDeleteCategoryModal.vue'

const toast = useToast()
const categories = ref([])
const loading = ref(false)
const searchTerm = ref('')

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingCategory = ref(null)
const categoryToDelete = ref(null)
const saving = ref(false)

const fetchCategories = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/categories/list')
        if (response.data.error) {
            if (response.data.error === 'Não existem categorias cadastradas') {
                categories.value = []
            } else {
                toast.error(response.data.error)
            }
        } else {
            categories.value = response.data
        }
    } catch (error) {
        console.error('Error fetching categories:', error)
        toast.error('Erro ao carregar categorias')
    } finally {
        loading.value = false
    }
}

const filteredCategories = computed(() => {
    if (!searchTerm.value) return categories.value
    const term = searchTerm.value.toLowerCase()
    return categories.value.filter(c => c.name?.toLowerCase().includes(term))
})

const openCreate = () => {
    editingCategory.value = null
    showModal.value = true
}

const openEdit = (category) => {
    editingCategory.value = { ...category }
    showModal.value = true
}

const openDelete = (category) => {
    if (category.product_count > 0) {
        toast.warning(`Não é possível excluir: existem ${category.product_count} produto(s) nesta categoria.`)
        return
    }
    categoryToDelete.value = category
    showDeleteModal.value = true
}

const handleSave = async (formData) => {
    saving.value = true
    try {
        if (editingCategory.value) {
            await api.put(`/admin/categories/update/${editingCategory.value.id}`, formData)
            toast.success('Categoria atualizada com sucesso!')
        } else {
            await api.post('/admin/categories/create', formData)
            toast.success('Categoria criada com sucesso!')
        }
        await fetchCategories()
        showModal.value = false
        editingCategory.value = null
    } catch (error) {
        console.error('Error saving category:', error)
        toast.error(error.response?.data?.error || 'Erro ao salvar categoria')
    } finally {
        saving.value = false
    }
}

const handleDeleted = () => {
    fetchCategories()
    showDeleteModal.value = false
    categoryToDelete.value = null
}

onMounted(() => {
    fetchCategories()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Categorias
            </h1>
            <p class="text-[#8c9e78] font-light">Visualize e gerencie as categorias de produtos da loja</p>
        </div>

        <!-- Toolbar -->
        <div class="px-10 mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <!-- Search Bar -->
            <div class="relative group w-96">
                <input v-model="searchTerm" type="text" placeholder="Pesquisar por nome..."
                    class="w-full bg-transparent border-b border-[#3a5528] py-2 pl-8 pr-4 text-[#3a5528] placeholder-[#8c9e78] focus:outline-none focus:border-[#2c3e20] transition-colors font-light" />
                <Search :size="18" class="absolute left-0 top-1/2 -translate-y-1/2 text-[#3a5528]" />
            </div>

            <!-- Create Button -->
            <button @click="openCreate"
                class="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0f2301] text-[#fffdf2] text-sm font-light italic tracking-wide hover:bg-[#3a5528] transition-all shadow-sm">
                <span class="text-base leading-none">+</span> Nova Categoria
            </button>
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
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                ID</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Nome</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Produtos</th>
                            <th
                                class="py-4 px-6 text-left font-['Montserrat'] italic font-normal text-[#3a5528] tracking-wider text-sm">
                                Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#eaddcf]">
                        <tr v-for="category in filteredCategories" :key="category.id" class="category-row">
                            <td class="py-4 px-6 text-[#3a5528] font-light text-sm">#{{ category.id }}</td>
                            <td class="py-4 px-6 text-[#3a5528] font-medium">{{ category.name }}</td>
                            <td class="py-4 px-6 text-[#6b8555] font-light">{{ category.product_count }} produto{{
                                category.product_count !== 1 ? 's' : '' }}</td>
                            <!-- Ações -->
                            <td class="py-4 px-6">
                                <div class="flex items-center gap-3">
                                    <button @click="openEdit(category)"
                                        class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                                        title="Editar">
                                        <Pencil :size="17" />
                                    </button>
                                    <button @click="openDelete(category)"
                                        class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1"
                                        title="Excluir">
                                        <Trash2 :size="17" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="filteredCategories.length === 0">
                            <td colspan="4" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhuma categoria encontrada.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <CategoryModal :is-open="showModal" :edit-data="editingCategory" :saving="saving" @close="showModal = false"
            @save="handleSave" />
        <ConfirmDeleteCategoryModal :is-open="showDeleteModal" :category="categoryToDelete"
            @close="showDeleteModal = false" @deleted="handleDeleted" />
    </div>
</template>

<style scoped>
.category-row {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

.category-row:hover {
    background-color: #f0efe9;
}
</style>
