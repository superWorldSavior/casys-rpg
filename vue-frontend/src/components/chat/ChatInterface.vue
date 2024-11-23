<template>
  <v-card class="chat-interface" :elevation="2">
    <!-- Zone de messages -->
    <v-card-text 
      class="messages-container" 
      ref="messagesContainer" 
      @touchstart="handleTouchStart" 
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <v-slide-y-transition group>
        <div v-for="message in messages" :key="message.id" class="message-wrapper">
          <v-chip
            :class="['message', message.estUtilisateur ? 'message-utilisateur' : 'message-ai']"
            :color="message.estUtilisateur ? 'primary' : 'secondary'"
            text-color="white"
          >
            <template v-if="message.estUtilisateur">
              {{ message.contenu }}
            </template>
            <template v-else>
              <span ref="streamingText">{{ displayedText }}</span>
              <span class="typing-cursor" v-if="isStreaming">|</span>
            </template>
          </v-chip>
          <span class="message-time">{{ formatTime(message.timestamp) }}</span>
        </div>
      </v-slide-y-transition>
      <v-progress-circular
        v-if="chatStore.estEnChargement"
        indeterminate
        color="primary"
        class="loading-indicator"
      ></v-progress-circular>
    </v-card-text>

    <!-- Contrôles -->
    <v-card-actions class="controls-zone">
      <v-btn
        icon="mdi-skip-next"
        @click="skipStreaming"
        :disabled="!isStreaming"
        variant="text"
      ></v-btn>
      <v-slider
        v-model="chatStore.vitesseLecture"
        min="10"
        max="200"
        step="10"
        label="Vitesse"
        class="mx-4"
        density="compact"
        hide-details
      ></v-slider>
    </v-card-actions>

    <!-- Zone de saisie -->
    <v-card-actions class="input-zone">
      <v-text-field
        v-model="messageInput"
        placeholder="Tapez votre message..."
        append-icon="mdi-send"
        @click:append="envoyerMessage"
        @keyup.enter="envoyerMessage"
        :loading="chatStore.estEnChargement"
        :disabled="chatStore.estEnChargement || isStreaming"
        variant="outlined"
        density="comfortable"
        hide-details
      ></v-text-field>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const touchStartY = ref(0)
const touchStartTime = ref(0)
const isStreaming = ref(false)
const displayedText = ref('')
const currentMessageIndex = ref(0)
const streamingText = ref<HTMLElement | null>(null)

const messages = computed(() => chatStore.messages)
const currentMessage = computed(() => {
  const msg = messages.value[messages.value.length - 1]
  return msg && !msg.estUtilisateur ? msg.contenu : ''
})

watch(currentMessage, (newMessage) => {
  if (newMessage) {
    startStreaming(newMessage)
  }
})

const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const startStreaming = async (text: string) => {
  isStreaming.value = true
  currentMessageIndex.value = 0
  displayedText.value = ''

  const streamNextChar = async () => {
    if (currentMessageIndex.value < text.length && isStreaming.value) {
      displayedText.value += text[currentMessageIndex.value]
      currentMessageIndex.value++
      scrollToBottom()
      await new Promise(resolve => setTimeout(resolve, chatStore.vitesseLecture))
      await streamNextChar()
    } else {
      isStreaming.value = false
      displayedText.value = text
    }
  }

  await streamNextChar()
}

const skipStreaming = () => {
  isStreaming.value = false
  if (currentMessage.value) {
    displayedText.value = currentMessage.value
  }
}

const envoyerMessage = async () => {
  const message = messageInput.value.trim()
  if (message && !chatStore.estEnChargement && !isStreaming.value) {
    messageInput.value = ''
    await chatStore.envoyerMessageAI(message)
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 100)
}

// Contrôles tactiles
const handleTouchStart = (event: TouchEvent) => {
  touchStartY.value = event.touches[0].clientY
  touchStartTime.value = Date.now()
}

const handleTouchMove = (event: TouchEvent) => {
  const touchY = event.touches[0].clientY
  const deltaY = touchStartY.value - touchY
  
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop += deltaY
    touchStartY.value = touchY
  }
  
  // Ajuster la vitesse en fonction du mouvement vertical
  const deltaTime = Date.now() - touchStartTime.value
  if (deltaTime > 100 && Math.abs(deltaY) > 50) {
    const newSpeed = chatStore.vitesseLecture + (deltaY > 0 ? 10 : -10)
    chatStore.setVitesseLecture(newSpeed)
  }
  
  // Empêcher le défilement de la page
  event.preventDefault()
}

const handleTouchEnd = () => {
  touchStartTime.value = 0
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-interface {
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.messages-container {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  touch-action: pan-y;
  padding: 0.5rem;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  max-width: 85%;
}

.message-utilisateur {
  align-self: flex-end;
}

.message-ai {
  align-self: flex-start;
}

.message {
  padding: 0.5rem 0.75rem;
  border-radius: 0.75rem;
  word-break: break-word;
  margin: 0;
}

.message-time {
  font-size: 0.7rem;
  color: rgba(0, 0, 0, 0.5);
  align-self: flex-end;
  margin-right: 0.25rem;
}

.input-zone {
  padding: 0.5rem;
  border-top: 1px solid rgba(0,0,0,0.1);
}

.loading-indicator {
  align-self: center;
  margin: 0.5rem;
}

.v-text-field {
  margin: 0;
  padding: 0;
}
</style>
