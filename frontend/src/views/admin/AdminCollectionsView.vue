<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { Search, Loader2, Pencil, Trash2, PlusCircle } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'
import CollectionModal from '@/components/admin/CollectionModal.vue'
import ConfirmDeleteCollectionModal from '@/components/admin/ConfirmDeleteCollectionModal.vue'
import SelectProductsModal from '@/components/admin/SelectProductsModal.vue'

const toast = useToast()
const collections = ref([])
const loading = ref(false)
const searchTerm = ref('')

const showModal = ref(false)
const showDeleteModal = ref(false)
const showAddProductsModal = ref(false)
const editingCollection = ref(null)
const collectionToDelete = ref(null)
const collectionToAdd = ref(null)
const saving = ref(false)

const fetchCollections = async () => {
    loading.value = true
    try {
        const response = await api.get('/admin/collections/list')
        if (response.data.error) {
            toast.error(response.data.error)
        } else {
            collections.value = response.data
        }
    } catch (error) {
        console.error('Error fetching collections:', error)
        toast.error('Erro ao carregar coleções')
    } finally {
        loading.value = false
    }
}

const filteredCollections = computed(() => {
    if (!searchTerm.value) return collections.value
    const term = searchTerm.value.toLowerCase()
    return collections.value.filter(c => c.name?.toLowerCase().includes(term))
})

const openCreate = () => {
    editingCollection.value = null
    showModal.value = true
}

const openEdit = (collection) => {
    editingCollection.value = { ...collection }
    showModal.value = true
}

const openDelete = (collection) => {
    if (collection.product_count > 0) {
        toast.warning(`Não é possível excluir: existem ${collection.product_count} produto(s) nesta coleção.`)
        return
    }
    collectionToDelete.value = collection
    showDeleteModal.value = true
}

const openAddProducts = (collection) => {
    collectionToAdd.value = collection
    showAddProductsModal.value = true
}

const handleSave = async (formData) => {
    saving.value = true
    try {
        if (editingCollection.value) {
            await api.put(`/admin/collections/update/${editingCollection.value.id}`, formData)
            toast.success('Coleção atualizada com sucesso!')
        } else {
            await api.post('/admin/collections/create', formData)
            toast.success('Coleção criada com sucesso!')
        }
        await fetchCollections()
        showModal.value = false
        editingCollection.value = null
    } catch (error) {
        console.error('Error saving collection:', error)
        toast.error(error.response?.data?.error || 'Erro ao salvar coleção')
    } finally {
        saving.value = false
    }
}

const handleDeleted = () => {
    fetchCollections()
    showDeleteModal.value = false
    collectionToDelete.value = null
}

const handleAddProductsSave = async (data) => {
    saving.value = true
    try {
        const product_ids = data.selected.map(item => item.product_id)
        
        await api.post(`/admin/collections/${collectionToAdd.value.id}/add_products`, { product_ids })
        toast.success('Produtos adicionados com sucesso!')
        
        await fetchCollections()
        showAddProductsModal.value = false
        collectionToAdd.value = null
    } catch (error) {
        console.error('Error adding products:', error)
        toast.error(error.response?.data?.error || 'Erro ao adicionar produtos')
    } finally {
        saving.value = false
    }
}

onMounted(() => {
    fetchCollections()
})
</script>

<template>
    <div class="min-h-screen bg-[#fffdf2] pb-20">

        <!-- Header -->
        <div class="pt-8 px-10 mb-6">
            <h1 class="text-2xl font-['Montserrat'] font-light text-[#3a5528] italic mb-1 tracking-wide">
                Coleções
            </h1>
            <p class="text-[#8c9e78] font-light">Visualize e gerencie as coleções de produtos da loja</p>
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
                <span class="text-base leading-none">+</span> Nova Coleção
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
                        <tr v-for="collection in filteredCollections" :key="collection.id" class="collection-row">
                            <td class="py-4 px-6 text-[#3a5528] font-light text-sm">#{{ collection.id }}</td>
                            <td class="py-4 px-6 text-[#3a5528] font-medium">{{ collection.name }}</td>
                            <td class="py-4 px-6 text-[#6b8555] font-light">{{ collection.product_count }} produto{{
                                collection.product_count !== 1 ? 's' : '' }}</td>
                            <!-- Ações -->
                            <td class="py-4 px-6">
                                <div class="flex items-center gap-3">
                                    <button @click="openAddProducts(collection)"
                                        class="text-[#3a5528] hover:text-[#0f2301] hover:scale-110 transition-all p-1"
                                        title="Adicionar Produtos">
                                        <PlusCircle :size="17" />
                                    </button>
                                    <button @click="openEdit(collection)"
                                        class="text-[#0f2301] hover:text-[#3a5528] hover:scale-110 transition-all p-1"
                                        title="Editar">
                                        <Pencil :size="17" />
                                    </button>
                                    <button @click="openDelete(collection)"
                                        class="text-[#9a382d] hover:text-red-700 hover:scale-110 transition-all p-1"
                                        title="Excluir">
                                        <Trash2 :size="17" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr v-if="filteredCollections.length === 0">
                            <td colspan="4" class="py-12 text-center text-[#8c9e78] font-light italic">
                                Nenhuma coleção encontrada.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modals -->
        <CollectionModal :is-open="showModal" :edit-data="editingCollection" :saving="saving" @close="showModal = false"
            @save="handleSave" />
        <ConfirmDeleteCollectionModal :is-open="showDeleteModal" :collection="collectionToDelete"
            @close="showDeleteModal = false" @deleted="handleDeleted" />
        <SelectProductsModal :is-open="showAddProductsModal" @close="showAddProductsModal = false"
            @save="handleAddProductsSave" />
    </div>
</template>

<style scoped>
.collection-row {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

.collection-row:hover {
    background-color: #f0efe9;
}
</style>
