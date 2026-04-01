<template>
  <div class="container mx-auto px-0 py-0 flex flex-col h-[calc(100vh-8rem)]">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <h1 class="text-2xl font-bold text-white font-goldman">Talk to ExLLM</h1>
      <div class="flex items-center gap-3">
        <button
          v-if="isAdmin"
          @click="showKeyPanel = !showKeyPanel"
          class="text-sm text-gray-400 hover:text-primary transition"
        >
          {{ showKeyPanel ? 'Hide Keys' : 'Manage Keys' }}
        </button>
        <button
          v-if="store.messages.length"
          @click="store.clearChat"
          class="text-sm text-gray-400 hover:text-primary transition"
        >
          Clear Chat
        </button>
      </div>
    </div>

    <!-- Admin Key Management Panel -->
    <div v-if="showKeyPanel" class="glass rounded-xl p-4 mb-4 flex-shrink-0">
      <h3 class="text-sm font-bold text-white mb-3">API Keys</h3>

      <!-- Existing keys -->
      <div v-if="apiKeys.length" class="space-y-2 mb-3">
        <div
          v-for="key in apiKeys"
          :key="key.id"
          class="flex items-center justify-between px-3 py-2 rounded-lg"
          :class="key.is_active ? 'bg-primary/10 border border-primary/30' : 'bg-bg-secondary border border-transparent'"
        >
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono px-2 py-0.5 rounded bg-bg-primary text-gray-400">{{ key.provider }}</span>
            <span class="text-sm text-white">{{ key.label || 'Unnamed' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="!key.is_active"
              @click="activateKey(key.id)"
              class="text-xs text-primary hover:text-primary/80 transition"
            >
              Activate
            </button>
            <span v-else class="text-xs text-primary font-bold">Active</span>
            <button
              @click="deleteKey(key.id)"
              class="text-xs text-red-400 hover:text-red-300 transition ml-2"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <p v-else class="text-gray-500 text-sm mb-3">No API keys configured.</p>

      <!-- Add new key -->
      <div class="flex gap-2">
        <select v-model="newKey.provider" class="px-3 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary">
          <option value="openai">OpenAI</option>
          <option value="gemini">Gemini</option>
        </select>
        <input
          v-model="newKey.label"
          placeholder="Label"
          class="px-3 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary w-28"
        />
        <input
          v-model="newKey.api_key"
          placeholder="API Key"
          type="password"
          class="flex-1 px-3 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary"
        />
        <button
          @click="addKey"
          :disabled="!newKey.api_key"
          class="px-4 py-2 bg-primary text-black rounded-lg text-sm font-bold hover:bg-primary-dark transition disabled:opacity-50"
        >
          Add
        </button>
      </div>
    </div>

    <!-- Messages Area -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto space-y-4 pr-2 min-h-0">
      <!-- Empty state -->
      <div v-if="!store.messages.length" class="flex flex-col items-center justify-center h-full">
        <div class="glass rounded-2xl p-8 text-center max-w-md">
          <div class="text-4xl mb-4">💱</div>
          <h2 class="text-xl font-bold text-white mb-2 font-goldman">ExLLM</h2>
          <p class="text-gray-400 text-sm mb-6">Your AI-powered forex trading assistant. Ask about market trends, trading strategies, or currency pairs.</p>
          <div class="flex flex-wrap gap-2 justify-center">
            <button
              v-for="s in suggestions"
              :key="s"
              @click="send(s)"
              class="glass glass-hover px-4 py-2 rounded-full text-sm text-gray-300 hover:text-primary transition"
            >
              {{ s }}
            </button>
          </div>
        </div>
      </div>

      <!-- Message bubbles -->
      <div
        v-for="(msg, i) in store.messages"
        :key="i"
        :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
      >
        <!-- AI label -->
        <div v-if="msg.role === 'assistant'" class="flex items-start gap-3 max-w-[80%]">
          <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary text-xs font-bold mt-1">
            Ex
          </div>
          <div class="glass rounded-2xl rounded-bl-md px-4 py-3 text-gray-200 whitespace-pre-wrap">{{ msg.content }}</div>
        </div>

        <!-- User bubble -->
        <div v-else class="max-w-[80%]">
          <div class="bg-primary text-black rounded-2xl rounded-br-md px-4 py-3 whitespace-pre-wrap">{{ msg.content }}</div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="store.loading" class="flex justify-start">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary text-xs font-bold mt-1">
            Ex
          </div>
          <div class="glass rounded-2xl rounded-bl-md px-4 py-3">
            <div class="typing-indicator flex gap-1">
              <span class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <p v-if="store.error" class="text-red-400 text-sm mt-2 flex-shrink-0">{{ store.error }}</p>

    <!-- Input Bar -->
    <div class="mt-4 flex gap-3 flex-shrink-0">
      <input
        v-model="input"
        @keyup.enter="send()"
        :disabled="store.loading"
        placeholder="Type a message..."
        class="flex-1 px-5 py-3 bg-bg-primary border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-primary transition disabled:opacity-50"
      />
      <button
        @click="send()"
        :disabled="!input.trim() || store.loading"
        class="px-6 py-3 bg-primary text-black rounded-full font-bold hover:bg-primary-dark transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useLlmStore } from '@/stores/llm'
import { preferencesApi, llmApi } from '@/services/api'

const store = useLlmStore()
const input = ref('')
const messagesContainer = ref(null)

// Admin state
const isAdmin = ref(false)
const showKeyPanel = ref(false)
const apiKeys = ref([])
const newKey = ref({ provider: 'openai', label: '', api_key: '' })

const suggestions = [
  'What affects EUR/USD?',
  'Explain pip values',
  'Current market outlook',
  'Best pairs for beginners',
]

onMounted(async () => {
  try {
    const { data } = await preferencesApi.get()
    isAdmin.value = !!data.is_admin
    if (isAdmin.value) await loadKeys()
  } catch {
    // not admin or preferences unavailable
  }
})

async function loadKeys() {
  try {
    const { data } = await llmApi.getKeys()
    apiKeys.value = data
  } catch {
    // 403 or other error
  }
}

async function addKey() {
  if (!newKey.value.api_key) return
  await llmApi.createKey(newKey.value)
  newKey.value = { provider: 'openai', label: '', api_key: '' }
  await loadKeys()
}

async function activateKey(keyId) {
  await llmApi.activateKey(keyId)
  await loadKeys()
}

async function deleteKey(keyId) {
  await llmApi.deleteKey(keyId)
  await loadKeys()
}

function send(text) {
  const msg = text || input.value.trim()
  if (!msg || store.loading) return
  input.value = ''
  store.sendMessage(msg)
}

// Auto-scroll on new messages or when loading changes
watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
)

watch(
  () => store.loading,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
)
</script>

<style scoped>
.typing-indicator span {
  animation-duration: 1s;
  animation-iteration-count: infinite;
}
</style>
