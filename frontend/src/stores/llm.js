import { defineStore } from 'pinia'
import { ref } from 'vue'
import { llmApi } from '@/services/api'

export const useLlmStore = defineStore('llm', () => {
  const messages = ref([])   // [{ role: 'user'|'assistant', content: string, timestamp: Date }]
  const loading  = ref(false)
  const error    = ref(null)

  async function sendMessage(content) {
    error.value = null
    messages.value.push({ role: 'user', content, timestamp: new Date() })

    loading.value = true
    try {
      const history = messages.value.map(m => ({ role: m.role, content: m.content }))
      const { data } = await llmApi.chat(history)
      messages.value.push({ role: 'assistant', content: data.reply, timestamp: new Date() })
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to get AI response.'
    } finally {
      loading.value = false
    }
  }

  function clearChat() {
    messages.value = []
    error.value = null
  }

  return { messages, loading, error, sendMessage, clearChat }
})
