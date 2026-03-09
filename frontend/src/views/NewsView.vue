<template>
  <div class="container mx-auto px-0 py-0">
    <!-- Bento Box Grid - Top Featured Stories -->
    <div class="bento-grid mb-6">
      <NewsStoryCard
        v-for="story in featuredStories"
        :key="story.id"
        :story="story"
        :featured="true"
        :class="story.size"
      />
    </div>

    <!-- Regular News Stories Grid -->
    <div class="news-grid">
      <NewsStoryCard
        v-for="story in regularStories"
        :key="story.id"
        :story="story"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NewsStoryCard from '@/components/NewsStoryCard.vue'

// Template data for featured stories (bento box)
const featuredStories = ref([
  {
    id: 1,
    headline: 'Federal Reserve Signals Potential Rate Cuts: USD Weakens Against Major Pairs',
    date: '2024-03-09',
    image: 'https://placehold.co/800x600/1a1a1a/FFD700?text=Fed+Rate+Decision',
    size: 'large'
  },
  {
    id: 2,
    headline: 'EUR/USD Reaches New Monthly High Amid European Economic Growth',
    date: '2024-03-09',
    image: 'https://placehold.co/600x400/1a1a1a/FFD700?text=EUR+USD+Rally',
    size: 'medium'
  },
  {
    id: 3,
    headline: 'Bank of Japan Maintains Ultra-Loose Policy: JPY Continues Decline',
    date: '2024-03-08',
    image: 'https://placehold.co/600x400/1a1a1a/FFD700?text=BOJ+Policy',
    size: 'medium'
  }
])

// Template data for regular stories
const regularStories = ref([
  {
    id: 4,
    headline: 'GBP/USD Volatility Increases Following UK Inflation Data Release',
    date: '2024-03-08',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=GBP+Volatility'
  },
  {
    id: 5,
    headline: 'AUD/USD Strengthens on Positive Australian Employment Numbers',
    date: '2024-03-07',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=AUD+Employment'
  },
  {
    id: 6,
    headline: 'USD/CAD Falls as Oil Prices Surge to Three-Month Highs',
    date: '2024-03-07',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=CAD+Oil+Prices'
  },
  {
    id: 7,
    headline: 'Swiss Franc Gains Safe-Haven Status Amid Global Uncertainty',
    date: '2024-03-06',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=CHF+Safe+Haven'
  },
  {
    id: 8,
    headline: 'EUR/GBP Technical Analysis: Key Support Level at 0.8500 Holds',
    date: '2024-03-06',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=EUR+GBP+Technical'
  },
  {
    id: 9,
    headline: 'Chinese Yuan Stabilizes After PBOC Intervention in Currency Markets',
    date: '2024-03-05',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=CNY+Stabilization'
  },
  {
    id: 10,
    headline: 'NZD/USD Reaches 6-Month High on RBNZ Hawkish Stance',
    date: '2024-03-05',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=NZD+Rally'
  },
  {
    id: 11,
    headline: 'Dollar Index (DXY) Shows Signs of Reversal at Key Technical Level',
    date: '2024-03-04',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=DXY+Analysis'
  },
  {
    id: 12,
    headline: 'Emerging Market Currencies Rally as Risk Appetite Returns',
    date: '2024-03-04',
    image: 'https://placehold.co/400x300/1a1a1a/FFD700?text=EM+Currencies'
  }
])
</script>

<style scoped>
/* Bento Box Grid for Featured Stories */
.bento-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 250px);
  }

  .large {
    grid-column: 1;
    grid-row: span 2;
  }

  .medium:nth-child(2) {
    grid-column: 2;
    grid-row: 1;
  }

  .medium:nth-child(3) {
    grid-column: 2;
    grid-row: 2;
  }
}

@media (min-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 280px);
  }

  .large {
    grid-column: 1 / 3;
    grid-row: span 2;
  }

  .medium:nth-child(2) {
    grid-column: 3;
    grid-row: 1;
  }

  .medium:nth-child(3) {
    grid-column: 3;
    grid-row: 2;
  }
}

/* Regular News Grid */
.news-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .news-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .news-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
