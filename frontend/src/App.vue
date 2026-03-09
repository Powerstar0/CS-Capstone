<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { forexApi } from '@/services/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isLoginPage = computed(() => route.path === '/login')
const searchQuery = ref('')
const searchFocused = ref(false)
const showSearchDropdown = ref(false)

const showTicker = ref(true)
const isSignedIn = computed(() => authStore.isLoggedIn)

// Ticker state — seeded with static fallback so banner shows immediately
const baseCurrencies = ref([
  { pair: 'EUR/USD', price: '—', trend: 'up' },
  { pair: 'GBP/USD', price: '—', trend: 'up' },
  { pair: 'USD/JPY', price: '—', trend: 'up' },
  { pair: 'AUD/USD', price: '—', trend: 'up' },
  { pair: 'USD/CAD', price: '—', trend: 'up' },
  { pair: 'USD/CHF', price: '—', trend: 'up' },
  { pair: 'NZD/USD', price: '—', trend: 'up' },
  { pair: 'EUR/GBP', price: '—', trend: 'up' },
  { pair: 'EUR/JPY', price: '—', trend: 'up' },
  { pair: 'GBP/JPY', price: '—', trend: 'up' },
])

const tickerItems = computed(() =>
  [...baseCurrencies.value, ...baseCurrencies.value, ...baseCurrencies.value]
)

// Search functionality
const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return baseCurrencies.value.slice(0, 6)
  
  const query = searchQuery.value.toLowerCase().replace(/[/\s]/g, '')
  return baseCurrencies.value.filter(item => {
    const pairClean = item.pair.toLowerCase().replace(/[/\s]/g, '')
    return pairClean.includes(query)
  }).slice(0, 6)
})

const handleSearchFocus = () => {
  searchFocused.value = true
  showSearchDropdown.value = true
}

const handleSearchBlur = () => {
  // Delay to allow click on dropdown items
  setTimeout(() => {
    searchFocused.value = false
    showSearchDropdown.value = false
  }, 200)
}

const handleCurrencyClick = (pair) => {
  if (!isSignedIn.value) {
    router.push('/login')
    return
  }
  searchQuery.value = ''
  showSearchDropdown.value = false
  router.push({ path: '/trading', query: { pair } })
}

const getPriceChange = (item) => {
  // Calculate mock price change for display
  const price = parseFloat(item.price)
  if (isNaN(price)) return 0
  return item.trend === 'up' ? 0.25 : -0.18
}

// Generate mini chart data for each currency
const getMiniChartData = (item) => {
  const points = 12
  const basePrice = parseFloat(item.price) || 1.0
  const data = []
  
  for (let i = 0; i < points; i++) {
    const variation = (Math.random() - 0.5) * 0.01
    const trend = item.trend === 'up' ? 0.0002 * i : -0.0002 * i
    data.push(basePrice + variation + trend)
  }
  
  return data
}

const getMiniChartPath = (data) => {
  if (!data || data.length === 0) return ''
  
  const width = 80
  const height = 24
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width
    const y = height - ((value - min) / range) * height
    return `${x},${y}`
  }).join(' ')
  
  return `M ${points.split(' ').join(' L ')}`
}

// Fetch live rates and update ticker, tracking trend vs previous price
let previousPrices = {}
async function fetchTickerRates() {
  try {
    const { data } = await forexApi.getRates()
    const rates = data.rates  // { "EURUSD": 1.0823, ... }
    baseCurrencies.value = baseCurrencies.value.map(item => {
      const key = item.pair.replace('/', '')   // "EUR/USD" -> "EURUSD"
      const newPrice = rates[key]
      if (newPrice == null) return item
      const prev = previousPrices[key]
      const trend = prev == null ? item.trend : (newPrice >= prev ? 'up' : 'down')
      previousPrices[key] = newPrice
      return { pair: item.pair, price: newPrice.toFixed(4), trend }
    })
  } catch {
    // keep showing last known prices on error
  }
}

// Manual override (kept for backwards-compat with defineExpose)
const updateTickerData = (newData) => { baseCurrencies.value = newData }

const handleTradeClick = () => {
  router.push(isSignedIn.value ? '/trading' : '/login')
}

defineExpose({ updateTickerData })

let tickerInterval = null
onMounted(() => {
  fetchTickerRates()
  tickerInterval = setInterval(fetchTickerRates, 60_000)
})
onUnmounted(() => clearInterval(tickerInterval))
</script>

<template>
  <div v-if="!isLoginPage" id="app" class="min-h-screen bg-bg-primary flex flex-col">
    <header class="bg-bg-secondary border-b border-border sticky top-0 z-50 backdrop-blur-sm bg-opacity-90 w-full">
      <nav class="w-full px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16 gap-6 max-w-full relative">
          
          <!-- Left: Logo + Search Bar -->
          <div class="flex items-center gap-6 flex-shrink-0 relative z-20">
            <RouterLink to="/" class="text-3xl font-bold font-goldman text-primary hover:opacity-80 transition">FXTrade</RouterLink>
            
            <div class="relative hidden sm:block">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search currencies"
                autocomplete="off"
                @focus="handleSearchFocus"
                @blur="handleSearchBlur"
                class="search-input w-48 focus:w-64 px-4 py-2 pl-10 bg-bg-primary border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-primary transition-all duration-300 text-sm"
              />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 transition-colors" :class="{ 'text-primary': searchFocused }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              
              <!-- Search Dropdown -->
              <div 
                v-if="showSearchDropdown && searchResults.length > 0" 
                class="search-dropdown absolute top-full left-0 mt-2 bg-black border border-gray-800 rounded-xl shadow-2xl overflow-hidden z-50 w-80"
              >
                <div class="py-2">
                  <div
                    v-for="item in searchResults"
                    :key="item.pair"
                    @click="handleCurrencyClick(item.pair)"
                    class="flex items-center justify-between px-4 py-3 hover:bg-gray-900 transition cursor-pointer group"
                  >
                    <div class="flex-1">
                      <p 
                        class="font-bold text-sm transition"
                        :class="item.trend === 'up' ? 'text-green-400' : 'text-red-400'"
                      >
                        {{ item.pair }}
                      </p>
                      <p class="text-xs text-gray-500 mt-0.5">{{ item.pair.split('/')[0] }} to {{ item.pair.split('/')[1] }}</p>
                    </div>
                    
                    <!-- Mini Chart -->
                    <div class="mx-4">
                      <svg width="80" height="24" class="mini-chart">
                        <path
                          :d="getMiniChartPath(getMiniChartData(item))"
                          fill="none"
                          :stroke="item.trend === 'up' ? '#10b981' : '#ef4444'"
                          stroke-width="1.5"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </div>
                    
                    <div class="text-right">
                      <p class="font-mono text-sm text-white">{{ item.price }}</p>
                      <p class="text-xs font-semibold" :class="item.trend === 'up' ? 'text-green-400' : 'text-red-400'">
                        {{ item.trend === 'up' ? '+' : '' }}{{ getPriceChange(item).toFixed(2) }}%
                      </p>
                    </div>
                  </div>
                </div>
                
                <div v-if="searchQuery && searchResults.length === 0" class="px-4 py-6 text-center text-gray-500 text-sm">
                  No currencies found
                </div>
              </div>
            </div>
          </div>

          <!-- Center: Currency Ticker with 3D Curved Perspective (stays fixed behind) -->
          <div v-if="showTicker" class="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 flex items-center overflow-hidden perspective-container ticker-responsive" style="max-width: 60%; min-width: 300px;">
            <div class="ticker-scroll-container">
              <div class="ticker-scroll">
                <span 
                  v-for="(item, index) in tickerItems" 
                  :key="index"
                  @click="handleCurrencyClick(item.pair)"
                  class="ticker-item cursor-pointer hover:opacity-80 transition-opacity pointer-events-auto"
                >
                  <span class="font-bold text-gray-400">{{ item.pair }}</span>
                  <span class="text-primary">{{ item.price }}</span>
                  <span :class="item.trend === 'up' ? 'text-green-500' : 'text-red-500'">
                    {{ item.trend === 'up' ? '▲' : '▼' }}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- Vignette Overlay Left (expands when search is focused) -->
          <div 
            class="ticker-vignette absolute inset-y-0 left-0 pointer-events-none z-10 transition-all duration-300"
            :class="searchFocused ? 'w-80' : 'w-56'"
            :style="{
              background: 'linear-gradient(to right, rgba(10, 10, 10, 1) 0%, rgba(10, 10, 10, 0.9) 40%, transparent 100%)'
            }"
          ></div>

          <!-- Vignette Overlay Right (fades out nav area) -->
          <div 
            class="ticker-vignette-right absolute inset-y-0 right-0 pointer-events-none z-10 w-72"
            :style="{
              background: 'linear-gradient(to left, rgba(10, 10, 10, 1) 0%, rgba(10, 10, 10, 0.9) 30%, transparent 100%)'
            }"
          ></div>

          <!-- Spacer for center (invisible, maintains layout) -->
          <div class="flex-1"></div>

          <!-- Right: Nav Links + Trade -->
          <div class="flex items-center gap-4 flex-shrink-0 relative z-20">
            <div class="hidden md:flex gap-2">
              <RouterLink to="/dashboard" class="nav-link">Dashboard</RouterLink>
              <RouterLink to="/news" class="nav-link">News</RouterLink>
              <RouterLink to="/settings" class="nav-link">Settings</RouterLink>
            </div>
            
            <button @click="handleTradeClick" class="px-6 py-2 bg-primary text-black rounded-full font-bold hover:bg-primary-dark transition-all text-sm">
              Trade
            </button>
          </div>

        </div>
      </nav>
    </header>
    
    <main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full">
      <RouterView />
    </main>
  </div>
  
  <RouterView v-else />
</template>

<style scoped>
.nav-link {
  @apply text-gray-400 hover:text-white px-4 py-2 rounded-full text-sm font-semibold transition-all;
}

.nav-link.router-link-active {
  @apply text-primary;
}

.search-input {
  transition: all 0.3s ease;
}

.search-input:focus {
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.1);
}

/* Search Dropdown */
.search-dropdown {
  animation: dropdownFade 0.2s ease-out;
  backdrop-filter: blur(10px);
  background: #000000;
  max-height: 400px;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

/* Hide scrollbar for Chrome, Safari and Opera */
.search-dropdown::-webkit-scrollbar {
  display: none;
}

@keyframes dropdownFade {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mini Chart Animation */
.mini-chart {
  opacity: 0.9;
  transition: opacity 0.2s;
}

.group:hover .mini-chart {
  opacity: 1;
}

/* 3D Perspective Container */
.perspective-container {
  perspective: 1000px;
  perspective-origin: center;
  display: flex;
  align-items: center;
  height: 100%;
}

/* Ticker Scroll Container with Curve Effect */
.ticker-scroll-container {
  position: relative;
  width: 100%;
  height: 40px;
  overflow: hidden;
  display: flex;
  align-items: center;
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 10%,
    black 90%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 10%,
    black 90%,
    transparent 100%
  );
}

/* Scrolling Ticker with 3D Transform */
.ticker-scroll {
  display: flex;
  gap: 2rem;
  animation: scroll-curve 40s linear infinite;
  transform-style: preserve-3d;
  will-change: transform;
}

/* Individual Ticker Items */
.ticker-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  font-family: monospace;
  font-size: 0.875rem;
  flex-shrink: 0;
  transform-style: preserve-3d;
  animation: curve-perspective 40s linear infinite;
}

/* 3D Curve Animation */
@keyframes scroll-curve {
  0% {
    transform: translateX(0) translateZ(0) rotateY(0deg);
  }
  100% {
    transform: translateX(-33.33%) translateZ(0) rotateY(0deg);
  }
}

@keyframes curve-perspective {
  0%, 100% {
    transform: translateZ(15px) rotateY(-12deg) scale(0.95);
  }
  50% {
    transform: translateZ(0px) rotateY(0deg) scale(1);
  }
}

/* Responsive ticker sizing */
.ticker-responsive {
  width: 50%;
}

@media (max-width: 1280px) {
  .ticker-responsive {
    width: 45%;
  }
}

@media (max-width: 1024px) {
  .ticker-responsive {
    width: 40%;
  }
}

@media (max-width: 768px) {
  .ticker-responsive {
    width: 35%;
    min-width: 250px;
  }
  
  .ticker-item {
    font-size: 0.75rem;
    gap: 0.375rem;
  }
}

/* Pause on hover */
.ticker-scroll-container:hover .ticker-scroll {
  animation-play-state: paused;
}

.ticker-scroll-container:hover .ticker-item {
  animation-play-state: paused;
}
</style>