<template>
    <div class="rocca-datetime-picker font-montserrat">
        <!-- Input de exibição -->
        <div class="relative">
            <input type="text" :value="displayValue" @click="togglePicker" readonly :placeholder="placeholder"
                :class="inputClass"
                class="w-full px-4 py-3 border border-[#0f2301]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f2301] focus:border-[#0f2301] transition-all font-montserrat italic text-[#3a5528] cursor-pointer" />
            <button v-if="modelValue && clearable" @click.stop="clearValue" type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-[#3a5528]/50 hover:text-[#9a382d] transition-colors">
                <X class="w-5 h-5" />
            </button>
        </div>

        <!-- Picker dropdown -->
        <Teleport to="body">
            <div v-if="isOpen" class="fixed inset-0 z-[9999]" @click="closePicker">
                <div class="absolute bg-white rounded-xl shadow-2xl border border-[#0f2301]/20 p-4" :style="pickerStyle"
                    @click.stop>
                    <div class="flex gap-4">
                        <!-- Calendário -->
                        <div class="flex-1">
                            <!-- Cabeçalho do mês/ano -->
                            <div class="flex items-center justify-between mb-4">
                                <button @click="previousMonth" type="button"
                                    class="p-1 hover:bg-[#0f2301]/50 rounded transition-colors">
                                    <ChevronLeft class="w-5 h-5 text-[#3a5528]" />
                                </button>
                                <span class="font-light italic text-[#3a5528] tracking-wide">
                                    {{ monthYearDisplay }}
                                </span>
                                <button @click="nextMonth" type="button"
                                    class="p-1 hover:bg-[#0f2301]/50 rounded transition-colors">
                                    <ChevronRight class="w-5 h-5 text-[#3a5528]" />
                                </button>
                            </div>

                            <!-- Grid de dias da semana -->
                            <div class="grid grid-cols-7 gap-1 mb-2">
                                <div v-for="day in daysOfWeek" :key="day"
                                    class="text-center text-xs font-light italic text-[#3a5528]/70 py-1">
                                    {{ day }}
                                </div>
                            </div>

                            <!-- Grid de dias do mês -->
                            <div class="grid grid-cols-7 gap-1">
                                <button v-for="(day, index) in calendarDays" :key="index" @click="selectDate(day)"
                                    type="button" :disabled="!day.isCurrentMonth" :class="[
                                        'aspect-square flex items-center justify-center rounded-lg text-sm transition-all italic',
                                        day.isCurrentMonth
                                            ? 'text-[#3a5528] hover:bg-[#0f2301]/50'
                                            : 'text-[#3a5528]/20 cursor-not-allowed',
                                        day.isSelected
                                            ? 'bg-[#0f2301] text-[#fffdf2] font-medium hover:bg-[#0f2301]/90'
                                            : '',
                                        day.isToday && !day.isSelected
                                            ? 'border-2 border-[#0f2301]'
                                            : ''
                                    ]">
                                    {{ day.day }}
                                </button>
                            </div>

                            <!-- Botões de ação -->
                            <div class="flex gap-2 mt-4">
                                <button @click="clearValue" type="button"
                                    class="flex-1 py-2 px-3 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#0f2301]/80 transition-all italic text-sm tracking-wide border border-[#0f2301]/20">
                                    Limpar
                                </button>
                                <button @click="setToday" type="button"
                                    class="flex-1 py-2 px-3 bg-[#0f2301] text-[#fffdf2] rounded-lg hover:bg-[#0f2301]/90 transition-all italic text-sm tracking-wide">
                                    Hoje
                                </button>
                            </div>
                        </div>

                        <!-- Seletor de hora -->
                        <div class="w-20 border-l border-[#0f2301]/20 pl-4">
                            <div class="text-sm font-light italic text-[#3a5528] mb-2 text-center">Hora</div>
                            <div class="h-64 overflow-y-auto scroll-smooth scrollbar-thin">
                                <button v-for="hour in hours" :key="hour" @click="selectHour(hour)" type="button"
                                    :class="[
                                        'w-full py-2 text-sm italic rounded transition-all',
                                        selectedHour === hour
                                            ? 'bg-[#0f2301] text-[#fffdf2]'
                                            : 'text-[#3a5528] hover:bg-[#0f2301]/50'
                                    ]">
                                    {{ hour }}
                                </button>
                            </div>
                        </div>

                        <!-- Seletor de minutos -->
                        <div class="w-20 border-l border-[#0f2301]/20 pl-4">
                            <div class="text-sm font-light italic text-[#3a5528] mb-2 text-center">Min</div>
                            <div class="h-64 overflow-y-auto scroll-smooth scrollbar-thin">
                                <button v-for="minute in minutes" :key="minute" @click="selectMinute(minute)"
                                    type="button" :class="[
                                        'w-full py-2 text-sm italic rounded transition-all',
                                        selectedMinute === minute
                                            ? 'bg-[#0f2301] text-[#fffdf2]'
                                            : 'text-[#3a5528] hover:bg-[#0f2301]/50'
                                    ]">
                                    {{ minute }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { X, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
    modelValue: {
        type: String,
        default: ''
    },
    placeholder: {
        type: String,
        default: 'Selecione data e hora'
    },
    inputClass: {
        type: String,
        default: ''
    },
    clearable: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const inputRef = ref(null)
const pickerStyle = ref({})
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const selectedDate = ref(null)
const selectedHour = ref('00')
const selectedMinute = ref('00')

const daysOfWeek = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']

const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutes = ['00', '15', '30', '45']

// Valor formatado para exibição
const displayValue = computed(() => {
    if (!props.modelValue) return ''
    const date = new Date(props.modelValue)
    return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
})

// Display do mês/ano
const monthYearDisplay = computed(() => {
    const date = new Date(currentYear.value, currentMonth.value)
    return date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
})

// Gerar dias do calendário
const calendarDays = computed(() => {
    const days = []
    const firstDay = new Date(currentYear.value, currentMonth.value, 1)
    const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
    const prevLastDay = new Date(currentYear.value, currentMonth.value, 0)

    const firstDayOfWeek = firstDay.getDay()
    const totalDays = lastDay.getDate()

    // Dias do mês anterior
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        const day = prevLastDay.getDate() - i
        days.push({
            day,
            isCurrentMonth: false,
            isSelected: false,
            isToday: false,
            date: new Date(currentYear.value, currentMonth.value - 1, day)
        })
    }

    // Dias do mês atual
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    for (let day = 1; day <= totalDays; day++) {
        const date = new Date(currentYear.value, currentMonth.value, day)
        date.setHours(0, 0, 0, 0)

        const isToday = date.getTime() === today.getTime()
        const isSelected = selectedDate.value &&
            date.getDate() === selectedDate.value.getDate() &&
            date.getMonth() === selectedDate.value.getMonth() &&
            date.getFullYear() === selectedDate.value.getFullYear()

        days.push({
            day,
            isCurrentMonth: true,
            isSelected,
            isToday,
            date
        })
    }

    // Completar com dias do próximo mês
    const remainingDays = 42 - days.length // 6 semanas
    for (let day = 1; day <= remainingDays; day++) {
        days.push({
            day,
            isCurrentMonth: false,
            isSelected: false,
            isToday: false,
            date: new Date(currentYear.value, currentMonth.value + 1, day)
        })
    }

    return days
})

// Toggle picker
const togglePicker = (event) => {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
        calculatePosition(event.target)
    }
}

// Calcular posição do picker com lógica responsiva inteligente
const calculatePosition = (inputElement) => {
    const rect = inputElement.getBoundingClientRect()

    // Dimensões do picker
    const pickerWidth = 450
    const pickerHeight = 430

    // Espaços disponíveis em todas as direções
    const spaceBelow = window.innerHeight - rect.bottom
    const spaceAbove = rect.top
    const spaceRight = window.innerWidth - rect.right
    const spaceLeft = rect.left

    // Margens de segurança
    const margin = 16

    let left = rect.left
    let top = rect.bottom + 8

    // 1. Verificar posição horizontal (direita/esquerda do input)
    if (spaceRight < pickerWidth + margin) {
        // Se não cabe à direita, tentar à esquerda
        if (spaceLeft >= pickerWidth + margin) {
            left = rect.right - pickerWidth
        } else {
            // Se não cabe em nenhum lado, centralizar ou alinhar com margem
            left = Math.max(margin, Math.min(window.innerWidth - pickerWidth - margin, rect.left))
        }
    }

    // 2. Verificar posição vertical (abaixo/acima do input)
    if (spaceBelow < pickerHeight + margin) {
        // Se não cabe abaixo, tentar acima
        if (spaceAbove >= pickerHeight + margin) {
            top = rect.top - pickerHeight - 8
        } else {
            // Se não cabe nem acima nem abaixo, priorizar visibilidade
            // Posicionar o picker o mais próximo possível sem cortar
            if (spaceBelow > spaceAbove) {
                // Mais espaço abaixo - alinhar com fundo da tela
                top = Math.max(margin, window.innerHeight - pickerHeight - margin)
            } else {
                // Mais espaço acima - alinhar com topo da tela
                top = margin
            }
        }
    }

    pickerStyle.value = {
        left: `${left}px`,
        top: `${top}px`
    }
}

const closePicker = () => {
    isOpen.value = false
}

// Navegação de mês
const previousMonth = () => {
    if (currentMonth.value === 0) {
        currentMonth.value = 11
        currentYear.value--
    } else {
        currentMonth.value--
    }
}

const nextMonth = () => {
    if (currentMonth.value === 11) {
        currentMonth.value = 0
        currentYear.value++
    } else {
        currentMonth.value++
    }
}

// Selecionar data
const selectDate = (dayObj) => {
    if (!dayObj.isCurrentMonth) return

    selectedDate.value = dayObj.date
    updateValue()
}

// Selecionar hora
const selectHour = (hour) => {
    selectedHour.value = hour
    updateValue()
}

// Selecionar minuto
const selectMinute = (minute) => {
    selectedMinute.value = minute
    updateValue()
}

// Atualizar valor
const updateValue = () => {
    if (!selectedDate.value) return

    const date = new Date(selectedDate.value)
    const hour = parseInt(selectedHour.value)
    const minute = parseInt(selectedMinute.value)
    date.setHours(hour, minute, 0, 0)

    emit('update:modelValue', date.toISOString())
}

// Limpar valor
const clearValue = () => {
    selectedDate.value = null
    selectedHour.value = '00'
    selectedMinute.value = '00'
    emit('update:modelValue', '')
    closePicker()
}

// Definir para hoje
const setToday = () => {
    const now = new Date()
    selectedDate.value = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    selectedHour.value = String(now.getHours()).padStart(2, '0')
    selectedMinute.value = String(Math.floor(now.getMinutes() / 15) * 15).padStart(2, '0')
    currentMonth.value = now.getMonth()
    currentYear.value = now.getFullYear()
    updateValue()
}

// Inicializar com valor existente
watch(() => props.modelValue, (newValue) => {
    if (newValue) {
        const date = new Date(newValue)
        selectedDate.value = new Date(date.getFullYear(), date.getMonth(), date.getDate())
        selectedHour.value = String(date.getHours()).padStart(2, '0')
        selectedMinute.value = String(date.getMinutes()).padStart(2, '0')
        currentMonth.value = date.getMonth()
        currentYear.value = date.getFullYear()
    }
}, { immediate: true })

// Fechar ao clicar ESC
const handleEscape = (e) => {
    if (e.key === 'Escape' && isOpen.value) {
        closePicker()
    }
}

onMounted(() => {
    document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
/* Custom scrollbar */
.scrollbar-thin::-webkit-scrollbar {
    width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
    background: rgba(243, 234, 195, 0.2);
    border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
    background: #0f2301;
    border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: #3a5528;
}
</style>
