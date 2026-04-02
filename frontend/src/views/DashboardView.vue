<template>
  <div class="container mx-auto px-0 py-0">
    <!-- <h1 class="text-6xl font-bold font-goldman text-primary mb-8">Dashboard</h1>
    
    <!-- Adaptive Bento Box Layout -->
    <div class="dashboard-grid">
      <!-- Left Column: Adaptive Widgets (Holdings/Wishlist/Feed) -->
      <div class="adaptive-widgets">
        <template v-for="widgetId in sideWidgets" :key="widgetId">
          <!-- Holdings Widget -->
          <div 
            v-if="widgetId === 'holdings'"
            @dragover.prevent="handleDragOver($event, 'holdings', 'side')"
            @drop="handleDrop($event, 'holdings', 'side')"
            :class="`glass rounded-xl hover:shadow-xl widget-card flex flex-col ${
              draggedWidget === 'holdings' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between p-6 pb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'holdings', 'side')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Holdings</h2>
              </div>
            </div>
            <div class="bg-bg-primary rounded-lg mx-6 p-3 flex-1 overflow-auto">
              <div v-if="portfolioStore.loading" class="space-y-1.5">
                <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
                <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
              </div>
              <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-full text-red-400 text-sm">
                {{ portfolioStore.error }}
              </div>
              <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
                No holdings yet
              </div>
              <div v-else class="space-y-1.5">
                <div
                  v-for="holding in portfolioStore.holdings"
                  :key="holding['currency-ticker-symbol'] || holding.currency"
                  class="flex justify-between items-center px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                >
                  <div>
                    <p class="font-bold text-white text-sm group-hover:text-primary transition">{{ holding['currency-ticker-symbol'] || holding.currency }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ holding.currency || 'Currency' }}</p>
                  </div>
                  <div class="text-right">
                    <p class="font-mono text-white text-sm">{{ Number(holding.amount).toFixed(2) }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">${{ (Number(holding.amount) * 1.2).toFixed(2) }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Holdings Footer -->
            <div class="widget-footer">
              <div class="flex justify-between items-center">
                <p class="text-xs text-gray-400">{{ portfolioStore.holdings?.length || 0 }} currencies held</p>
                <button class="text-xs text-primary hover:text-primary/80 font-bold transition">
                  Manage →
                </button>
              </div>
            </div>
          </div>

          <!-- Wishlist Widget -->
          <div
            v-if="widgetId === 'wishlist'"
            @dragover.prevent="handleDragOver($event, 'wishlist', 'side')"
            @drop="handleDrop($event, 'wishlist', 'side')"
            :class="`glass rounded-xl hover:shadow-xl widget-card flex flex-col ${
              draggedWidget === 'wishlist' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between p-6 pb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'wishlist', 'side')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Wishlist</h2>
              </div>
            </div>
            <div class="bg-bg-primary rounded-lg mx-6 p-3 flex-1">
              <div class="space-y-1.5">
                <div
                  v-for="item in wishlistItems"
                  :key="item.symbol"
                  @click="goToTrading(item.symbol)"
                  class="flex justify-between items-center px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                >
                  <div>
                    <p class="font-bold text-white text-sm group-hover:text-primary transition">{{ item.symbol }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ item.name }}</p>
                  </div>
                  <div class="text-right">
                    <p class="font-mono text-white text-sm">${{ item.price.toFixed(2) }}</p>
                    <p class="text-xs font-semibold mt-0.5" :class="item.change >= 0 ? 'text-green-400' : 'text-red-400'">
                      {{ item.change >= 0 ? '+' : '' }}{{ item.change.toFixed(2) }}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Wishlist Footer -->
            <div class="widget-footer">
              <div class="flex justify-between items-center">
                <p class="text-xs text-gray-400">{{ wishlistItems.length }} assets tracked</p>
                <button class="text-xs text-primary hover:text-primary/80 font-bold transition">
                  View All →
                </button>
              </div>
            </div>
          </div>

          <!-- Feed Widget -->
          <div
            v-else-if="widgetId === 'feed'"
            @dragover.prevent="handleDragOver($event, 'feed', 'side')"
            @drop="handleDrop($event, 'feed', 'side')"
            :class="`glass rounded-xl hover:shadow-xl widget-card flex flex-col ${
              draggedWidget === 'feed' ? 'dragging-placeholder' : ''
            }`"
          >
            <div class="flex items-center justify-between p-6 pb-4">
              <div class="flex items-center gap-2">
                <div 
                  draggable="true"
                  @dragstart="handleDragStart($event, 'feed', 'side')"
                  @dragend="handleDragEnd"
                  class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
                >
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-white">Feed</h2>
              </div>
            </div>
            <div class="bg-bg-primary rounded-lg mx-6 p-3 flex-1 overflow-auto">
              <!-- Feed Items -->
              <div class="space-y-1.5">
                <div
                  v-for="item in feedItems"
                  :key="item.id"
                  class="px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
                >
                  <p class="text-sm text-white font-medium group-hover:text-primary transition">{{ item.title }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ item.time }}</p>
                </div>
              </div>
            </div>
            
            <!-- Feed Footer -->
            <div class="widget-footer">
              <div class="flex justify-between items-center">
                <p class="text-xs text-gray-400">Last updated: Just now</p>
                <button class="text-xs text-primary hover:text-primary/80 font-bold transition">
                  Refresh →
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Right Column: Portfolio + Buying Power + Holdings -->
      <div class="left-column">
        <template v-for="widgetId in mainWidgets" :key="widgetId">
          <!-- Portfolio Widget -->
          <div 
            v-if="widgetId === 'portfolio'"
            @dragover.prevent="handleDragOver($event, 'portfolio', 'main')"
            @drop="handleDrop($event, 'portfolio', 'main')"
            :class="`portfolio-widget glass p-6 rounded-xl hover:shadow-xl widget-card ${
              draggedWidget === 'portfolio' ? 'dragging-placeholder' : ''
            }`"
          >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div
                draggable="true"
                @dragstart="handleDragStart($event, 'portfolio', 'main')"
                @dragend="handleDragEnd"
                class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white">Portfolio</h2>
                <p class="text-2xl font-bold mt-0.5 text-white">
                  ${{ totalPortfolioValue.toFixed(2) }}
                </p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500 mb-1">24h Change</p>
              <p class="text-lg font-bold" :class="portfolioChange >= 0 ? 'text-green-400' : 'text-red-400'">
                {{ portfolioChange >= 0 ? '+' : '' }}{{ portfolioChange.toFixed(2) }}%
              </p>
            </div>
          </div>

          <!-- Deposit Modal -->
          <Teleport to="body">
            <div v-if="showDepositModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="closeDeposit">
              <div class="bg-bg-secondary border border-gray-700 rounded-2xl p-6 w-full max-w-sm mx-4">
                <h3 class="text-xl font-bold text-white mb-4">Deposit Funds</h3>
                <div class="space-y-4">
                  <div>
                    <label class="text-sm text-gray-400 mb-1 block">Currency</label>
                    <select v-model="depositCurrency" class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
                      <option v-for="c in currencies" :key="c.code" :value="c.code">{{ c.code }} — {{ c.name }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="text-sm text-gray-400 mb-1 block">Amount</label>
                    <input
                      v-model.number="depositAmount"
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="0.00"
                      class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                    />
                  </div>
                  <p v-if="depositError" class="text-red-400 text-sm">{{ depositError }}</p>
                  <div class="flex gap-3 pt-2">
                    <button @click="closeDeposit" class="flex-1 py-3 border border-gray-600 text-gray-400 rounded-full font-bold hover:border-gray-400 transition">
                      Cancel
                    </button>
                    <button @click="handleDeposit" :disabled="depositLoading" class="flex-1 py-3 bg-primary text-black rounded-full font-bold hover:opacity-80 transition disabled:opacity-50">
                      {{ depositLoading ? 'Depositing...' : 'Confirm' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Teleport>

          <!-- Withdraw Modal -->
          <Teleport to="body">
            <div v-if="showWithdrawModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="closeWithdraw">
              <div class="bg-bg-secondary border border-gray-700 rounded-2xl p-6 w-full max-w-sm mx-4">
                <h3 class="text-xl font-bold text-white mb-4">Withdraw Funds</h3>
                <div class="space-y-4">
                  <div>
                    <label class="text-sm text-gray-400 mb-1 block">Currency</label>
                    <select v-model="withdrawCurrency" class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary">
                      <option v-for="c in currencies" :key="c.code" :value="c.code">{{ c.code }} — {{ c.name }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="text-sm text-gray-400 mb-1 block">Amount</label>
                    <input
                      v-model.number="withdrawAmount"
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="0.00"
                      class="w-full px-4 py-3 bg-bg-primary border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
                    />
                  </div>
                  <p v-if="withdrawError" class="text-red-400 text-sm">{{ withdrawError }}</p>
                  <div class="flex gap-3 pt-2">
                    <button @click="closeWithdraw" class="flex-1 py-3 border border-gray-600 text-gray-400 rounded-full font-bold hover:border-gray-400 transition">
                      Cancel
                    </button>
                    <button @click="handleWithdraw" :disabled="withdrawLoading" class="flex-1 py-3 bg-red-600 text-white rounded-full font-bold hover:opacity-80 transition disabled:opacity-50">
                      {{ withdrawLoading ? 'Withdrawing...' : 'Confirm' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Teleport>

          <div class="bg-bg-primary rounded-lg p-4 flex-1 flex flex-col overflow-hidden" style="min-height: 350px; max-height: 350px;">
            <!-- Date Range Selector -->
            <div class="flex gap-1.5 mb-3 flex-shrink-0">
              <button
                v-for="p in periods"
                :key="p.value"
                @click="selectPeriod(p.value)"
                :class="[
                  'px-3 py-1 rounded text-xs font-bold transition-all',
                  portfolioStore.selectedPeriod === p.value
                    ? 'bg-primary text-black'
                    : 'bg-bg-secondary text-gray-400 hover:text-white hover:bg-bg-secondary/80'
                ]"
              >{{ p.label }}</button>
            </div>

            <div v-if="portfolioStore.loading && !portfolioStore.historyData" class="flex items-center justify-center h-full">
              <div class="h-48 w-full bg-bg-secondary rounded-lg animate-pulse"></div>
            </div>
            <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-full text-red-400 text-sm">
              {{ portfolioStore.error }}
            </div>
            <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
              No holdings yet. Deposit funds to get started.
            </div>
            <div v-else class="relative flex flex-col justify-center items-center h-full w-full" style="padding-right: 1rem;">
              <!-- Loading overlay -->
              <div v-if="portfolioStore.historyLoading" class="absolute inset-0 flex items-center justify-center bg-bg-primary/60 z-10 rounded-lg">
                <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              </div>
              <!-- History error -->
              <div v-if="portfolioStore.historyError" class="absolute top-0 left-0 right-0 text-center text-red-400 text-xs py-1">
                {{ portfolioStore.historyError }}
              </div>
              <!-- Portfolio Line Chart -->
              <div class="w-full h-full flex items-center justify-center">
                <Line :data="portfolioLineChartData" :options="portfolioLineChartOptions" />
              </div>
            </div>
          </div>
        </div>

        <!-- Buying Power Widget -->
        <div 
          v-if="widgetId === 'buyingPower'"
          @dragover.prevent="handleDragOver($event, 'buyingPower', 'main')"
          @drop="handleDrop($event, 'buyingPower', 'main')"
          :class="`glass p-4 rounded-xl hover:shadow-xl widget-card ${
            draggedWidget === 'buyingPower' ? 'dragging-placeholder' : ''
          }`"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                draggable="true"
                @dragstart="handleDragStart($event, 'buyingPower', 'main')"
                @dragend="handleDragEnd"
                class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <div>
                <p class="text-xs text-gray-400 mb-1">Buying Power</p>
                <p class="text-xl font-bold text-white">${{ portfolioStore.balance?.toFixed(2) || '0.00' }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <button 
                @click="showDepositModal = true"
                class="px-4 py-2 bg-gradient-to-r from-primary to-primary/80 text-black font-bold rounded-lg hover:shadow-lg hover:shadow-primary/30 transition-all text-sm"
              >
                Deposit
              </button>
              <button 
                @click="showWithdrawModal = true"
                class="px-4 py-2 bg-gradient-to-r from-gray-700 to-gray-600 text-white font-bold rounded-lg hover:shadow-lg hover:shadow-gray-500/30 transition-all text-sm"
              >
                Withdraw
              </button>
            </div>
          </div>
        </div>

        <!-- Holdings Widget (Main Column) -->
        <div 
          v-if="widgetId === 'holdingsMain'"
          @dragover.prevent="handleDragOver($event, 'holdingsMain', 'main')"
          @drop="handleDrop($event, 'holdingsMain', 'main')"
          :class="`glass p-6 rounded-xl hover:shadow-xl widget-card flex flex-col ${
            draggedWidget === 'holdingsMain' ? 'dragging-placeholder' : ''
          }`"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <div
                draggable="true"
                @dragstart="handleDragStart($event, 'holdingsMain', 'main')"
                @dragend="handleDragEnd"
                class="drag-handle cursor-grab active:cursor-grabbing p-1 hover:bg-primary/10 rounded"
              >
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <h2 class="text-xl font-bold text-white">Holdings</h2>
            </div>
          </div>
          
          <div class="bg-bg-primary rounded-lg p-4 flex-1 overflow-auto">
            <div v-if="portfolioStore.loading" class="space-y-1.5">
              <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
              <div class="h-12 bg-bg-secondary rounded-lg animate-pulse"></div>
            </div>
            <div v-else-if="portfolioStore.error" class="flex items-center justify-center h-full text-red-400 text-sm">
              {{ portfolioStore.error }}
            </div>
            <div v-else-if="portfolioStore.holdings.length === 0" class="flex items-center justify-center h-full text-gray-500 text-sm">
              No holdings yet
            </div>
            <div v-else class="space-y-1.5">
              <div
                v-for="holding in portfolioStore.holdings"
                :key="holding['currency-ticker-symbol'] || holding.currency"
                class="flex justify-between items-center px-3 py-2.5 bg-bg-secondary rounded-lg hover:border-primary border border-transparent transition-all cursor-pointer group"
              >
                <div>
                  <p class="font-bold text-white text-sm group-hover:text-primary transition">{{ holding['currency-ticker-symbol'] || holding.currency }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ holding.currency || 'Currency' }}</p>
                </div>
                <div class="text-right">
                  <p class="font-mono text-white text-sm">{{ Number(holding.amount).toFixed(2) }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">${{ (Number(holding.amount) * 1.2).toFixed(2) }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Holdings Footer -->
          <div class="widget-footer">
            <div class="flex justify-between items-center">
              <p class="text-xs text-gray-400">{{ portfolioStore.holdings?.length || 0 }} currencies held</p>
              <button class="text-xs text-primary hover:text-primary/80 font-bold transition">
                Manage →
              </button>
            </div>
          </div>
        </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePortfolioStore } from '@/stores/portfolio'
import { forexApi } from '@/services/api'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const router = useRouter()
const portfolioStore = usePortfolioStore()

// ── Currencies ───────────────────────────────────────────────────────────
const currencies = ref([])

async function fetchCurrencies() {
  try {
    const { data } = await forexApi.getCurrencies()
    currencies.value = data.currencies
  } catch {
    currencies.value = [
      { code: 'USD', name: 'US Dollar' },
      { code: 'EUR', name: 'Euro' },
      { code: 'GBP', name: 'British Pound' },
    ]
  }
}

// Date range periods for the chart selector
const periods = [
  { label: '1D', value: '1d' },
  { label: '1W', value: '1wk' },
  { label: '1M', value: '1mo' },
  { label: '3M', value: '3mo' },
  { label: '6M', value: '6mo' },
  { label: '1Y', value: '1y' },
  { label: '3Y', value: '3y' },
  { label: '5Y', value: '5y' },
]

function selectPeriod(period) {
  portfolioStore.fetchHistory(period)
}

onMounted(() => {
  fetchCurrencies()
  portfolioStore.fetchHoldings()
  portfolioStore.fetchHistory('1mo')
})

// Navigation function
const goToTrading = (symbol) => {
  router.push({ path: '/trading', query: { pair: symbol } })
}

// Format date labels based on the selected period
function formatDateLabel(dateStr, period) {
  const d = new Date(dateStr)
  switch (period) {
    case '1d':
      return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    case '1wk':
      return d.toLocaleDateString('en-US', { weekday: 'short' }) + ' ' +
        d.toLocaleTimeString('en-US', { hour: 'numeric' })
    case '1mo':
    case '3mo':
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    case '6mo':
    case '1y':
      return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
    case '3y':
    case '5y':
      return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
    default:
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }
}

// Portfolio Line Chart Data - from real yfinance historical rates
const portfolioLineChartData = computed(() => {
  const history = portfolioStore.historyData
  const period = portfolioStore.selectedPeriod

  // Empty / loading state
  if (!history || !history.data_points || history.data_points.length === 0) {
    return {
      labels: [],
      datasets: [{
        label: 'Portfolio Value (USD)',
        data: [],
        borderColor: 'rgba(255, 215, 0, 0.3)',
        backgroundColor: 'rgba(255, 215, 0, 0.05)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0
      }]
    }
  }

  const labels = history.data_points.map(dp => formatDateLabel(dp.date, period))
  const data = history.data_points.map(dp => dp.value)

  return {
    labels,
    datasets: [{
      label: 'Portfolio Value (USD)',
      data,
      borderColor: 'rgba(255, 215, 0, 1)',
      backgroundColor: 'rgba(255, 215, 0, 0.1)',
      borderWidth: 2,
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 6,
      pointBackgroundColor: 'rgba(255, 215, 0, 1)',
      pointBorderColor: '#1a1a1a',
      pointBorderWidth: 2
    }]
  }
})

const portfolioLineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255, 215, 0, 0.5)',
      borderWidth: 1,
      displayColors: false,
      callbacks: {
        label: function(context) {
          return '$' + context.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 10
        },
        maxRotation: 0,
        autoSkipPadding: 20
      }
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
        drawBorder: false
      },
      ticks: {
        color: '#6b7280',
        font: {
          size: 11
        },
        callback: function(value) {
          return '$' + (value / 1000).toFixed(1) + 'k'
        }
      }
    }
  },
  interaction: {
    intersect: false,
    mode: 'index'
  }
}

// Portfolio value from the latest history data point (in USD)
const totalPortfolioValue = computed(() => {
  const history = portfolioStore.historyData
  if (!history || !history.data_points || history.data_points.length === 0) {
    // Fallback to raw sum of holdings
    if (!portfolioStore.holdings || portfolioStore.holdings.length === 0) return 0
    return portfolioStore.holdings.reduce((sum, holding) => sum + Number(holding.amount), 0)
  }
  return history.data_points[history.data_points.length - 1].value
})

// Calculate change over the selected period (first vs last data point)
const portfolioChange = computed(() => {
  const history = portfolioStore.historyData
  if (!history || !history.data_points || history.data_points.length < 2) return 0

  const firstValue = history.data_points[0].value
  const lastValue = history.data_points[history.data_points.length - 1].value

  if (!firstValue || firstValue === 0) return 0
  return ((lastValue - firstValue) / firstValue) * 100
})

// Wishlist template data - Forex pairs
const wishlistItems = ref([
  { symbol: 'EUR/USD', name: 'Euro / US Dollar', price: 1.0876, change: 0.12 },
  { symbol: 'GBP/USD', name: 'British Pound / US Dollar', price: 1.2654, change: -0.08 },
  { symbol: 'USD/JPY', name: 'US Dollar / Japanese Yen', price: 149.87, change: 0.34 },
  { symbol: 'AUD/USD', name: 'Australian Dollar / US Dollar', price: 0.6523, change: -0.15 }
])

// Feed template data - Forex related
const feedItems = ref([
  { id: 1, title: 'EUR/USD broke resistance at 1.0850', time: '2 hours ago' },
  { id: 2, title: 'Deposited $500 USD to trading account', time: '5 hours ago' },
  { id: 3, title: 'GBP/USD reached target price of 1.2650', time: '1 day ago' },
  { id: 4, title: 'USD strengthening against major pairs', time: '2 days ago' },
  { id: 5, title: 'New forex signal: Buy EUR/USD', time: '3 days ago' }
])

// Deposit modal state
const showDepositModal = ref(false)
const depositCurrency  = ref('USD')
const depositAmount    = ref(null)
const depositLoading   = ref(false)
const depositError     = ref('')

function closeDeposit() {
  showDepositModal.value = false
  depositAmount.value    = null
  depositError.value     = ''
}

async function handleDeposit() {
  depositError.value = ''
  if (!depositAmount.value || depositAmount.value <= 0) {
    depositError.value = 'Enter a positive amount.'
    return
  }
  depositLoading.value = true
  try {
    await portfolioStore.deposit(depositCurrency.value, depositAmount.value)
    closeDeposit()
  } catch (e) {
    depositError.value = e.response?.data?.detail || 'Deposit failed.'
  } finally {
    depositLoading.value = false
  }
}

// Withdraw modal state
const showWithdrawModal = ref(false)
const withdrawCurrency  = ref('USD')
const withdrawAmount    = ref(null)
const withdrawLoading   = ref(false)
const withdrawError     = ref('')

function closeWithdraw() {
  showWithdrawModal.value = false
  withdrawAmount.value    = null
  withdrawError.value     = ''
}

async function handleWithdraw() {
  withdrawError.value = ''
  if (!withdrawAmount.value || withdrawAmount.value <= 0) {
    withdrawError.value = 'Enter a positive amount.'
    return
  }
  withdrawLoading.value = true
  try {
    await portfolioStore.withdraw(withdrawCurrency.value, withdrawAmount.value)
    closeWithdraw()
  } catch (e) {
    withdrawError.value = e.response?.data?.detail || 'Withdrawal failed.'
  } finally {
    withdrawLoading.value = false
  }
}

// Main column and side widgets can be reordered independently
const mainWidgets = ref(['portfolio', 'buyingPower', 'holdingsMain'])
const sideWidgets = ref(['holdings', 'wishlist', 'feed'])
const draggedWidget = ref(null)
const draggedColumn = ref(null)

const handleDragStart = (event, widgetId, column) => {
  draggedWidget.value = widgetId
  draggedColumn.value = column
  event.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (event, widgetId, column) => {
  event.preventDefault()
  
  // Only allow drag within the same column
  if (!draggedWidget.value || draggedColumn.value !== column) {
    return
  }
  
  if (draggedWidget.value === widgetId) return
  
  const widgets = column === 'main' ? mainWidgets : sideWidgets
  
  // Live reorder widgets
  const newOrder = [...widgets.value]
  const dragIndex = newOrder.indexOf(draggedWidget.value)
  const dropIndex = newOrder.indexOf(widgetId)
  
  if (dragIndex === -1 || dropIndex === -1) return
  
  // Remove from current position
  newOrder.splice(dragIndex, 1)
  
  // Insert at new position
  newOrder.splice(dropIndex, 0, draggedWidget.value)
  
  widgets.value = newOrder
}

const handleDrop = (event, widgetId, column) => {
  event.preventDefault()
  
  // Save to localStorage
  if (column === 'main') {
    localStorage.setItem('mainWidgetOrder', JSON.stringify(mainWidgets.value))
  } else {
    localStorage.setItem('sideWidgetOrder', JSON.stringify(sideWidgets.value))
  }
  
  draggedWidget.value = null
  draggedColumn.value = null
}

const handleDragEnd = () => {
  draggedWidget.value = null
  draggedColumn.value = null
}

// Load saved state
const savedMainOrder = localStorage.getItem('mainWidgetOrder')
if (savedMainOrder) {
  try {
    mainWidgets.value = JSON.parse(savedMainOrder)
  } catch (e) {
    console.error('Failed to load main widget order', e)
  }
}

const savedSideOrder = localStorage.getItem('sideWidgetOrder')
if (savedSideOrder) {
  try {
    sideWidgets.value = JSON.parse(savedSideOrder)
  } catch (e) {
    console.error('Failed to load side widget order', e)
  }
}
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 215, 0, 0.2);
}

/* Adaptive Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr 2fr;
    grid-template-rows: auto;
    gap: 1rem;
  }
  
  .left-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    order: 2;
  }
  
  .adaptive-widgets {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    order: 1;
  }
  
  .portfolio-widget {
    min-height: 480px;
    max-height: 480px;
    display: flex;
    flex-direction: column;
  }
  
  .adaptive-widgets > div {
    flex: 1;
    min-height: 190px;
  }
}

/* Smooth transitions */
.widget-card {
  transition: all 0.3s ease;
}

/* Placeholder for dragged widget */
.dragging-placeholder {
  opacity: 0.3;
  border: 2px dashed rgba(255, 215, 0, 0.5);
}

/* Drag handle */
.drag-handle {
  transition: all 0.2s ease;
}

.drag-handle:hover {
  transform: scale(1.1);
}

/* Widget Footers */
.portfolio-footer,
.widget-footer {
  padding: 1rem 1.5rem;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0 0 0.75rem 0.75rem;
  margin-top: auto;
}

.portfolio-widget {
  display: flex;
  flex-direction: column;
}

.portfolio-widget > div:first-child {
  flex: 1;
}
</style>
