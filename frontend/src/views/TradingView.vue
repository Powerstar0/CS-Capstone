<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-white">Trade</h1>

    <!-- Main Trading Layout: Chart + Sidebar -->
    <div class="trading-layout">
      <!-- Left: TradingView Chart -->
      <div class="chart-section glass p-6 rounded-xl">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-white">{{ chartPair }}</h2>
            <div class="flex items-center gap-4 mt-1">
              <span class="text-2xl font-mono text-white">{{ currentPrice.toFixed(4) }}</span>
              <span :class="['text-sm font-bold', priceChange >= 0 ? 'text-green-400' : 'text-red-400']">
                {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
              </span>
            </div>
          </div>
          <div class="flex gap-2">
            <select 
              v-model="chartPair" 
              @change="updateChartPair"
              class="px-4 py-2 bg-bg-primary border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary"
            >
              <option value="EUR/USD">EUR/USD</option>
              <option value="GBP/USD">GBP/USD</option>
              <option value="USD/JPY">USD/JPY</option>
              <option value="AUD/USD">AUD/USD</option>
              <option value="USD/CAD">USD/CAD</option>
              <option value="NZD/USD">NZD/USD</option>
            </select>
          </div>
        </div>
        <div ref="chartContainer" class="chart-container"></div>
      </div>

      <!-- Right: Trading Widgets Sidebar -->
      <div class="widgets-sidebar">
        <!-- Exchange Widget -->
        <div class="glass p-4 rounded-xl">
          <h3 class="text-sm font-bold text-white mb-3">Exchange Currency</h3>

          <!-- Order Type & Buy/Sell Row -->
          <div class="mb-4">
            <label class="text-xs text-gray-400 mb-1.5 block font-medium">Order Type</label>
            <div class="flex gap-2">
              <!-- Order Type Selector -->
              <div class="relative flex-1">
                <select v-model="orderType"
                  class="w-full px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary focus:shadow-lg focus:shadow-primary/20 transition-all appearance-none cursor-pointer hover:border-gray-600 font-semibold">
                  <option value="Market">Market Order</option>
                  <option value="Limit">Limit Order</option>
                  <option value="Stop">Stop Order</option>
                  <option value="Stop-Limit">Stop-Limit Order</option>
                </select>
                <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              
              <!-- Buy/Sell Toggle -->
              <div class="flex rounded-lg border-2 border-gray-700 overflow-hidden">
                <button
                  @click="orderSide = 'buy'"
                  :class="[
                    'px-4 py-2.5 text-sm font-bold transition-all',
                    orderSide === 'buy' 
                      ? 'bg-green-600 text-white' 
                      : 'bg-bg-primary text-gray-400 hover:text-white'
                  ]"
                >
                  Buy
                </button>
                <button
                  @click="orderSide = 'sell'"
                  :class="[
                    'px-4 py-2.5 text-sm font-bold transition-all',
                    orderSide === 'sell' 
                      ? 'bg-red-600 text-white' 
                      : 'bg-bg-primary text-gray-400 hover:text-white'
                  ]"
                >
                  Sell
                </button>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1.5 italic">
              {{ orderType === 'Market' ? 'Execute immediately at current price' : 
                 orderType === 'Limit' ? 'Execute at specified price or better' :
                 orderType === 'Stop' ? 'Execute when price reaches stop level' :
                 'Execute at limit price after stop is triggered' }}
            </p>
          </div>

          <!-- Currency Pair (Locked to Chart) -->
          <div class="mb-4">
            <label class="text-xs text-gray-400 mb-1.5 block font-medium">Currency Pair</label>
            <div class="flex items-center gap-2">
              <!-- From Currency (Display Only) -->
              <div class="flex-1 px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg">
                <span class="text-white text-sm font-bold">{{ fromCurrency }}</span>
              </div>
              
              <!-- Swap Button -->
              <button @click="swapCurrencies"
                class="p-2 rounded-lg border-2 border-gray-700 text-gray-400 hover:border-primary hover:text-primary hover:bg-primary/10 transition-all">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </button>
              
              <!-- To Currency (Display Only) -->
              <div class="flex-1 px-3 py-2.5 bg-gradient-to-br from-bg-primary to-bg-secondary border-2 border-gray-700 rounded-lg">
                <span class="text-white text-sm font-bold">{{ toCurrency }}</span>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1.5">
              Balance: <span class="text-gray-300 font-semibold">{{ exchangeFromBalance.toFixed(2) }} {{ fromCurrency }}</span>
            </p>
          </div>

          <!-- Amount -->
          <div class="mb-4">
            <label class="text-xs text-gray-400 mb-1.5 block font-medium">Amount</label>
            <div class="relative">
              <input
                v-model.number="exchangeAmount"
                type="number" min="0.01" step="0.01" placeholder="0.00"
                @input="computeReceive"
                class="w-full px-3 py-2.5 bg-bg-primary border-2 border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary transition-all font-mono"
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-semibold">{{ fromCurrency }}</span>
            </div>
          </div>

          <!-- Rate & Preview -->
          <div v-if="currentRate" class="bg-bg-primary rounded-lg px-3 py-2 mb-3 space-y-1 text-xs">
            <div class="flex justify-between">
              <span class="text-gray-400">Rate</span>
              <span class="text-primary font-mono">1 {{ fromCurrency }} = {{ currentRate.toFixed(6) }} {{ toCurrency }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Spread</span>
              <span class="text-gray-300 font-mono">0.0002</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Fee</span>
              <span class="text-green-400 font-semibold">0%</span>
            </div>
            <div v-if="receiveAmount" class="flex justify-between pt-1 border-t border-gray-800">
              <span class="text-gray-400">You receive</span>
              <span class="text-green-400 font-mono font-bold">{{ receiveAmount.toFixed(6) }} {{ toCurrency }}</span>
            </div>
          </div>
          <div v-else-if="rateLoading" class="text-gray-500 text-xs mb-3">Fetching rate...</div>
          <div v-else-if="rateError" class="text-red-400 text-xs mb-3">{{ rateError }}</div>

          <p v-if="tradeError" class="text-red-400 text-xs mb-2">{{ tradeError }}</p>
          <p v-if="tradeSuccess" class="text-green-400 text-xs mb-2">{{ tradeSuccess }}</p>

          <button
            @click="executeTrade"
            :disabled="tradeLoading || !currentRate || !exchangeAmount"
            class="w-full py-2 bg-primary text-black rounded-full text-sm font-bold hover:opacity-80 transition disabled:opacity-50"
          >
            {{ tradeLoading ? 'Processing...' : 'Execute Trade' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Related News Section -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-white">Related News</h2>
        <span class="text-xs text-gray-400">{{ chartPair }}</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="article in relatedNews"
          :key="article.id"
          class="bg-bg-primary rounded-lg p-4 hover:bg-bg-primary/80 transition cursor-pointer border border-gray-800 hover:border-primary/30"
        >
          <div>
            <h3 class="text-sm font-semibold text-white mb-2 line-clamp-2">
              {{ article.headline }}
            </h3>
            <div class="flex items-center gap-2 text-xs text-gray-400">
              <span>{{ article.source }}</span>
              <span>•</span>
              <span>{{ article.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="glass p-6 rounded-xl">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-white">Transaction History</h2>
        <button @click="loadHistory" class="text-sm text-primary hover:text-primary/80 font-semibold transition">
          Refresh
        </button>
      </div>

      <div v-if="historyLoading" class="space-y-3">
        <div class="h-20 bg-bg-primary rounded-lg animate-pulse"></div>
        <div class="h-20 bg-bg-primary rounded-lg animate-pulse"></div>
        <div class="h-20 bg-bg-primary rounded-lg animate-pulse"></div>
      </div>

      <div v-else-if="transactions.length === 0" class="flex flex-col items-center justify-center py-12">
        <svg class="w-16 h-16 text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-500 text-sm">No transactions yet</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="tx in transactions"
          :key="tx.transaction_id"
          class="bg-bg-primary rounded-lg px-4 py-3 border border-gray-800 hover:border-gray-700 transition"
        >
          <!-- Top row: type + currencies + amounts -->
          <div class="flex items-center justify-between flex-wrap gap-3 mb-2">
            <div class="flex items-center gap-3">
              <span class="text-xs font-bold uppercase tracking-wider text-gray-400">
                {{ tx.type || 'OTHER' }}
              </span>
              <div class="flex items-center gap-2 text-sm">
                <span class="text-white font-semibold">{{ tx.sender_currency_ticker_symbol }}</span>
                <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <span class="text-white font-semibold">{{ tx.receiver_currency_ticker_symbol }}</span>
              </div>
            </div>
            <div class="text-sm font-mono flex items-center gap-2">
              <span class="text-gray-400">{{ formatAmount(tx['sender-amount'] ?? tx.sender_amount) }}</span>
              <span class="text-gray-600">→</span>
              <span class="text-primary font-bold">{{ formatAmount(tx['receiver-amount'] ?? tx.receiver_amount) }}</span>
            </div>
          </div>

          <!-- Bottom row: emails + date + tx id -->
          <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
            <div class="flex items-center gap-2 text-gray-500 min-w-0">
              <span class="text-gray-400 truncate">{{ tx.sender_email }}</span>
              <span class="text-gray-600">→</span>
              <span class="text-gray-400 truncate">{{ tx.receiver_email }}</span>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 text-gray-500">
              <span>{{ formatDate(tx.timestamp) }}</span>
              <span class="font-mono text-gray-600">{{ tx.transaction_id?.slice(0, 8) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { tradeApi } from '@/services/api'
import { usePortfolioStore } from '@/stores/portfolio'
import { createChart } from 'lightweight-charts'

const route = useRoute()
const portfolioStore = usePortfolioStore()

// ── Chart ─────────────────────────────────────────────────────────────────
const chartContainer = ref(null)
const chartPair = ref('EUR/USD')
const currentPrice = ref(1.0876)
const priceChange = ref(0.45)
let chart = null
let candlestickSeries = null

async function initChart() {
  if (!chartContainer.value) return
  
  // Wait for next tick to ensure DOM is fully rendered
  await nextTick()
  
  const containerWidth = chartContainer.value.clientWidth
  
  chart = createChart(chartContainer.value, {
    width: containerWidth || 800,
    height: 400,
    layout: {
      background: { color: '#0a0a0a' },
      textColor: '#9ca3af',
    },
    grid: {
      vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
      horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    crosshair: {
      mode: 1,
    },
    rightPriceScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    timeScale: {
      borderColor: 'rgba(255, 255, 255, 0.1)',
      timeVisible: true,
      secondsVisible: false,
    },
  })

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#ef4444',
    borderUpColor: '#10b981',
    borderDownColor: '#ef4444',
    wickUpColor: '#10b981',
    wickDownColor: '#ef4444',
  })

  generateChartData()
  
  // Handle resize
  window.addEventListener('resize', handleResize)
  
  // Force a resize after a short delay to ensure proper sizing
  setTimeout(() => {
    handleResize()
  }, 100)
}

function handleResize() {
  if (chart && chartContainer.value) {
    const width = chartContainer.value.clientWidth
    if (width > 0) {
      chart.applyOptions({ width })
    }
  }
}

function generateChartData() {
  if (!candlestickSeries) return
  
  // Get base price for selected pair
  const basePrices = {
    'EUR/USD': 1.0876,
    'GBP/USD': 1.2654,
    'USD/JPY': 149.87,
    'AUD/USD': 0.6523,
    'USD/CAD': 1.3456,
    'NZD/USD': 0.6123
  }
  
  const basePrice = basePrices[chartPair.value] || 1.0
  const data = []
  const now = Date.now() / 1000
  const dayInSeconds = 86400
  
  // Generate 90 days of candlestick data
  for (let i = 90; i >= 0; i--) {
    const time = now - (i * dayInSeconds)
    const open = basePrice + (Math.random() - 0.5) * 0.02
    const close = open + (Math.random() - 0.5) * 0.015
    const high = Math.max(open, close) + Math.random() * 0.01
    const low = Math.min(open, close) - Math.random() * 0.01
    
    data.push({
      time: Math.floor(time),
      open,
      high,
      low,
      close
    })
  }
  
  candlestickSeries.setData(data)
  
  // Update current price and change
  if (data.length > 0) {
    const latestCandle = data[data.length - 1]
    const previousCandle = data[data.length - 2]
    currentPrice.value = latestCandle.close
    priceChange.value = ((latestCandle.close - previousCandle.close) / previousCandle.close) * 100
  }
}

function updateChartPair() {
  generateChartData()
}

// ── Related News ──────────────────────────────────────────────────────────
const newsArticles = {
  'EUR/USD': [
    { id: 1, headline: 'ECB Signals Potential Rate Cuts as Eurozone Inflation Cools', source: 'Reuters', time: '2 hours ago' },
    { id: 2, headline: 'EUR/USD Technical Analysis: Support at 1.0850 Holds Strong', source: 'FX Street', time: '4 hours ago' },
    { id: 3, headline: 'Dollar Weakens Against Euro on Fed Rate Cut Speculation', source: 'Bloomberg', time: '6 hours ago' },
    { id: 4, headline: 'European Economic Data Beats Expectations, Euro Rallies', source: 'MarketWatch', time: '8 hours ago' },
    { id: 5, headline: 'EUR/USD Reaches Monthly High Amid Strong German PMI', source: 'Forex Factory', time: '1 day ago' },
    { id: 6, headline: 'Analysts Predict EUR/USD Could Test 1.1000 This Quarter', source: 'DailyFX', time: '1 day ago' }
  ],
  'GBP/USD': [
    { id: 1, headline: 'Bank of England Maintains Rates, Pound Strengthens', source: 'Financial Times', time: '3 hours ago' },
    { id: 2, headline: 'UK Inflation Data Surprises: GBP/USD Surges to 1.2700', source: 'Reuters', time: '5 hours ago' },
    { id: 3, headline: 'Cable Holds Above Key Support as BOE Turns Hawkish', source: 'FX Street', time: '7 hours ago' },
    { id: 4, headline: 'British Pound Benefits from Positive Employment Numbers', source: 'Bloomberg', time: '10 hours ago' },
    { id: 5, headline: 'GBP/USD Technical Outlook: Bulls Target 1.2800', source: 'DailyFX', time: '1 day ago' },
    { id: 6, headline: 'Sterling Gains on Strong UK Retail Sales Report', source: 'MarketWatch', time: '1 day ago' }
  ],
  'USD/JPY': [
    { id: 1, headline: 'Bank of Japan Maintains Ultra-Loose Policy, Yen Weakens', source: 'Nikkei Asia', time: '1 hour ago' },
    { id: 2, headline: 'USD/JPY Climbs to 150.00 as BOJ Keeps Rates Unchanged', source: 'Reuters', time: '4 hours ago' },
    { id: 3, headline: 'Japanese Yen Under Pressure Amid Yield Differential', source: 'Bloomberg', time: '6 hours ago' },
    { id: 4, headline: 'USD/JPY Technical Analysis: Resistance at 150.50', source: 'FX Street', time: '9 hours ago' },
    { id: 5, headline: 'Japan\'s Core CPI Rises, But BOJ Stays Dovish', source: 'Financial Times', time: '12 hours ago' },
    { id: 6, headline: 'Yen Intervention Rumors as USD/JPY Tests Multi-Year Highs', source: 'Forex Factory', time: '1 day ago' }
  ],
  'AUD/USD': [
    { id: 1, headline: 'Australian Dollar Rallies on Strong Employment Data', source: 'Reuters', time: '2 hours ago' },
    { id: 2, headline: 'RBA Minutes Show Hawkish Stance, AUD/USD Gains', source: 'Bloomberg', time: '5 hours ago' },
    { id: 3, headline: 'Aussie Benefits from Rising Commodity Prices', source: 'MarketWatch', time: '7 hours ago' },
    { id: 4, headline: 'AUD/USD Technical: Bulls Eye 0.6600 Resistance', source: 'DailyFX', time: '10 hours ago' },
    { id: 5, headline: 'China\'s Economic Recovery Boosts Australian Dollar', source: 'Financial Times', time: '14 hours ago' },
    { id: 6, headline: 'AUD Strengthens as Iron Ore Prices Surge', source: 'FX Street', time: '1 day ago' }
  ],
  'USD/CAD': [
    { id: 1, headline: 'Canadian Dollar Strengthens as Oil Prices Rally', source: 'Reuters', time: '3 hours ago' },
    { id: 2, headline: 'USD/CAD Falls Below 1.3400 on Crude Surge', source: 'Bloomberg', time: '5 hours ago' },
    { id: 3, headline: 'Bank of Canada Holds Rates, CAD Remains Steady', source: 'Financial Times', time: '8 hours ago' },
    { id: 4, headline: 'Loonie Benefits from Strong Canadian GDP Growth', source: 'MarketWatch', time: '11 hours ago' },
    { id: 5, headline: 'USD/CAD Technical: Support at 1.3350 Holds', source: 'FX Street', time: '15 hours ago' },
    { id: 6, headline: 'WTI Crude Tops $80, Canadian Dollar Gains', source: 'Forex Factory', time: '1 day ago' }
  ],
  'NZD/USD': [
    { id: 1, headline: 'New Zealand Dollar Surges on RBNZ Hawkish Comments', source: 'Reuters', time: '2 hours ago' },
    { id: 2, headline: 'Kiwi Reaches 6-Month High Against US Dollar', source: 'Bloomberg', time: '6 hours ago' },
    { id: 3, headline: 'NZD/USD Technical Analysis: Bulls Target 0.6200', source: 'DailyFX', time: '9 hours ago' },
    { id: 4, headline: 'New Zealand Employment Data Beats Forecasts', source: 'Financial Times', time: '12 hours ago' },
    { id: 5, headline: 'RBNZ Signals No Rate Cuts in Near Term', source: 'MarketWatch', time: '1 day ago' },
    { id: 6, headline: 'NZD Benefits from Risk-On Market Sentiment', source: 'FX Street', time: '1 day ago' }
  ]
}

const relatedNews = computed(() => {
  return newsArticles[chartPair.value] || newsArticles['EUR/USD']
})

// ── Tabs ──────────────────────────────────────────────────────────────────
const activeTab = ref('exchange')

// ── Exchange form ─────────────────────────────────────────────────────────
const orderType = ref('Market')
const orderSide = ref('buy')
const fromCurrency   = ref('USD')
const toCurrency     = ref('AUD')
const exchangeAmount = ref(null)
const currentRate    = ref(null)
const receiveAmount  = ref(null)
const rateLoading    = ref(false)
const rateError      = ref('')
const tradeLoading   = ref(false)
const tradeError     = ref('')
const tradeSuccess   = ref('')

// ── Send form ─────────────────────────────────────────────────────────────
const transferEmail    = ref('')
const transferCurrency = ref('USD')
const transferAmount   = ref(null)
const transferLoading  = ref(false)
const transferError    = ref('')
const transferSuccess  = ref('')

// ── History ───────────────────────────────────────────────────────────────
const transactions   = ref([])
const historyLoading = ref(false)

// ── Balance helpers ───────────────────────────────────────────────────────
function getBalance(currency) {
  const h = portfolioStore.holdings.find(
    h => (h['currency-ticker-symbol'] || h.currency) === currency
  )
  return h ? Number(h.amount) : 0
}
const exchangeFromBalance = computed(() => getBalance(fromCurrency.value))
const transferFromBalance = computed(() => getBalance(transferCurrency.value))

// ── Exchange logic ────────────────────────────────────────────────────────
async function fetchRate() {
  if (fromCurrency.value === toCurrency.value) {
    currentRate.value   = null
    receiveAmount.value = null
    rateError.value     = 'Cannot exchange a currency for itself.'
    return
  }
  rateError.value   = ''
  rateLoading.value = true
  try {
    const { data } = await tradeApi.getRate(fromCurrency.value, toCurrency.value)
    currentRate.value = data.rate
    computeReceive()
  } catch {
    rateError.value   = 'Could not fetch rate.'
    currentRate.value = null
  } finally {
    rateLoading.value = false
  }
}

// Sync currencies from chart pair
function syncCurrenciesFromChart() {
  const [from, to] = chartPair.value.split('/')
  fromCurrency.value = from
  toCurrency.value = to
  fetchRate()
}

// Initialize chart and watches on mount
onMounted(async () => {
  await initChart()
  await portfolioStore.fetchHoldings()
  loadHistory()
  fetchRate()
  
  // Watch for query parameter changes from wishlist navigation
  watch(() => route.query.pair, (newPair) => {
    if (newPair && newPair !== chartPair.value) {
      chartPair.value = newPair
      updateChartPair()
      syncCurrenciesFromChart()
    }
  }, { immediate: true })
  
  // Watch for chart pair changes and sync currencies
  watch(chartPair, () => {
    syncCurrenciesFromChart()
  })
})

onUnmounted(() => {
  if (chart) {
    window.removeEventListener('resize', handleResize)
  }
})

function computeReceive() {
  receiveAmount.value = (currentRate.value && exchangeAmount.value > 0)
    ? exchangeAmount.value * currentRate.value
    : null
}

function swapCurrencies() {
  // Swap the currencies
  ;[fromCurrency.value, toCurrency.value] = [toCurrency.value, fromCurrency.value]
  
  // Update chart pair to match
  chartPair.value = `${fromCurrency.value}/${toCurrency.value}`
  updateChartPair()
  
  fetchRate()
}

async function executeTrade() {
  tradeError.value   = ''
  tradeSuccess.value = ''
  if (!exchangeAmount.value || exchangeAmount.value <= 0) { tradeError.value = 'Enter a positive amount.'; return }
  if (fromCurrency.value === toCurrency.value) { tradeError.value = 'Cannot exchange a currency for itself.'; return }
  tradeLoading.value = true
  try {
    const { data } = await tradeApi.exchange(fromCurrency.value, toCurrency.value, exchangeAmount.value)
    tradeSuccess.value = `Trade complete: sent ${data.sent_amount} ${data.from_currency}, received ${data.received_amount.toFixed(6)} ${data.to_currency} at rate ${data.rate.toFixed(6)}.`
    exchangeAmount.value = null
    receiveAmount.value  = null
    await portfolioStore.fetchHoldings()
    await loadHistory()
  } catch (e) {
    tradeError.value = e.response?.data?.detail || 'Trade failed.'
  } finally {
    tradeLoading.value = false
  }
}

// ── Transfer logic ────────────────────────────────────────────────────────
async function executeTransfer() {
  transferError.value   = ''
  transferSuccess.value = ''
  if (!transferEmail.value) { transferError.value = 'Enter a recipient email.'; return }
  if (!transferAmount.value || transferAmount.value <= 0) { transferError.value = 'Enter a positive amount.'; return }
  transferLoading.value = true
  try {
    const { data } = await tradeApi.transfer(transferEmail.value, transferCurrency.value, transferAmount.value)
    transferSuccess.value = `Sent ${data.amount} ${data.currency} to ${data.to_email}.`
    transferAmount.value  = null
    transferEmail.value   = ''
    await portfolioStore.fetchHoldings()
    await loadHistory()
  } catch (e) {
    transferError.value = e.response?.data?.detail || 'Transfer failed.'
  } finally {
    transferLoading.value = false
  }
}

// ── History logic ─────────────────────────────────────────────────────────
async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await tradeApi.getHistory()
    transactions.value = data.transactions || []
  } catch {
    // silently ignore
  } finally {
    historyLoading.value = false
  }
}

// ── Display helpers ───────────────────────────────────────────────────────
function typeBadgeClass(type) {
  switch (type) {
    case 'EXCHANGE': return 'bg-primary/20 text-primary border border-primary/40'
    case 'DEPOSIT':  return 'bg-green-500/20 text-green-400 border border-green-500/40'
    case 'WITHDRAW': return 'bg-red-500/20 text-red-400 border border-red-500/40'
    default:         return 'bg-gray-700/50 text-gray-400 border border-gray-600'
  }
}

function formatAmount(val) {
  const n = Number(val)
  if (isNaN(n)) return '—'
  return n.toFixed(6)
}

function formatDate(ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onUnmounted(() => {
  if (chart) {
    window.removeEventListener('resize', handleResize)
    chart.remove()
  }
})
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.glass:hover {
  border-color: rgba(255, 215, 0, 0.1);
}

/* Trading Layout */
.trading-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .trading-layout {
    grid-template-columns: 1fr 350px;
  }
}

.chart-section {
  min-height: 500px;
}

.widgets-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-container {
  width: 100%;
  height: 400px;
  position: relative;
  overflow: hidden;
}

/* Ensure chart canvas takes full width */
.chart-container > * {
  max-width: 100%;
}
</style>
