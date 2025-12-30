<template>
  <div class="demo-view">
    <h1>Component Library Demo</h1>
    <p>This page demonstrates PrimeVue components and ECharts integration with tree-shaking.</p>

    <div class="demo-sections">
      <SamplePrimeVue />
      <SampleCharts />
    </div>
  </div>
</template>

<script setup lang="ts">
import SamplePrimeVue from '../components/SamplePrimeVue.vue'
import SampleCharts from '../components/SampleCharts.vue'
</script>

<style scoped>
.demo-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

p {
  color: #666;
  margin-bottom: 2rem;
}

.demo-sections {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}
</style>
