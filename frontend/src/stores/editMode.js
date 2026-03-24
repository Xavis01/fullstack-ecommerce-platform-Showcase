// stores/editMode.js
// Gerencia o modo de edição global para admins
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export const useEditModeStore = defineStore('editMode', () => {
  const isEditMode = ref(false)

  function enableEditMode() {
    isEditMode.value = true
  }

  function disableEditMode() {
    isEditMode.value = false
  }

  function toggleEditMode() {
    isEditMode.value = !isEditMode.value
  }

  return { isEditMode, enableEditMode, disableEditMode, toggleEditMode }
})
