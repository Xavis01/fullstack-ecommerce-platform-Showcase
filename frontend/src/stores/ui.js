import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const isSplashActive = ref(false)
  // Initialize to 4 (Complete) if already seen, else 0 (Init)
  const initialStage = sessionStorage.getItem('splash_shown') === 'true' ? 4 : 0
  const introStage = ref(initialStage)
  const authModalVisible = ref(false)

  function startSplash() {
    isSplashActive.value = true
    introStage.value = 0
  }

  function setStage(stage) {
    introStage.value = stage
  }

  function finishSplash() {
    isSplashActive.value = false
    introStage.value = 4 // Complete
  }
  
  function openAuthModal() {
    authModalVisible.value = true
  }

  function closeAuthModal() {
    authModalVisible.value = false
  }

  return { 
    isSplashActive, 
    introStage, 
    authModalVisible,
    startSplash, 
    setStage, 
    finishSplash,
    openAuthModal,
    closeAuthModal
  }
})
