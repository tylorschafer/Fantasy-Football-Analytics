<template>
  <div class="sample-charts">
    <h2>ECharts Demo</h2>

    <div class="chart-grid">
      <div class="chart-container">
        <h3>Weekly Points - Line Chart</h3>
        <VChart :option="lineChartOption" :autoresize="true" class="chart" />
      </div>

      <div class="chart-container">
        <h3>Position Scoring - Bar Chart</h3>
        <VChart :option="barChartOption" :autoresize="true" class="chart" />
      </div>

      <div class="chart-container">
        <h3>Player Radar - Radar Chart</h3>
        <VChart :option="radarChartOption" :autoresize="true" class="chart" />
      </div>

      <div class="chart-container">
        <h3>Schedule Heatmap</h3>
        <VChart :option="heatmapOption" :autoresize="true" class="chart" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { EChartsOption } from 'echarts'

const lineChartOption = ref<EChartsOption>({
  title: {
    text: 'Weekly Points Trend',
  },
  tooltip: {
    trigger: 'axis',
  },
  legend: {
    data: ['Team A', 'Team B'],
  },
  xAxis: {
    type: 'category',
    data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
  },
  yAxis: {
    type: 'value',
  },
  series: [
    {
      name: 'Team A',
      type: 'line',
      data: [120, 132, 101, 134, 90, 130],
    },
    {
      name: 'Team B',
      type: 'line',
      data: [110, 125, 145, 122, 135, 128],
    },
  ],
})

const barChartOption = ref<EChartsOption>({
  title: {
    text: 'Points by Position',
  },
  tooltip: {
    trigger: 'axis',
  },
  xAxis: {
    type: 'category',
    data: ['QB', 'RB', 'WR', 'TE', 'K', 'DEF'],
  },
  yAxis: {
    type: 'value',
  },
  series: [
    {
      name: 'Average Points',
      type: 'bar',
      data: [24, 18, 15, 12, 8, 10],
      itemStyle: {
        color: '#5470c6',
      },
    },
  ],
})

const radarChartOption = ref<EChartsOption>({
  title: {
    text: 'Player Performance Metrics',
  },
  tooltip: {},
  radar: {
    indicator: [
      { name: 'Rushing', max: 100 },
      { name: 'Receiving', max: 100 },
      { name: 'Touchdowns', max: 100 },
      { name: 'Consistency', max: 100 },
      { name: 'Matchup', max: 100 },
    ],
  },
  series: [
    {
      name: 'Player Stats',
      type: 'radar',
      data: [
        {
          value: [85, 70, 90, 80, 75],
          name: 'Christian McCaffrey',
        },
        {
          value: [65, 90, 85, 88, 82],
          name: 'Tyreek Hill',
        },
      ],
    },
  ],
})

const heatmapOption = ref<EChartsOption>({
  title: {
    text: 'Matchup Difficulty Heatmap',
  },
  tooltip: {
    position: 'top',
  },
  grid: {
    height: '50%',
    top: '15%',
  },
  xAxis: {
    type: 'category',
    data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
  },
  yAxis: {
    type: 'category',
    data: ['Team A', 'Team B', 'Team C', 'Team D'],
  },
  series: [
    {
      name: 'Difficulty',
      type: 'heatmap',
      data: [
        [0, 0, 5],
        [0, 1, 7],
        [0, 2, 3],
        [0, 3, 8],
        [1, 0, 6],
        [1, 1, 4],
        [1, 2, 9],
        [1, 3, 2],
        [2, 0, 5],
        [2, 1, 8],
        [2, 2, 4],
        [2, 3, 7],
        [3, 0, 3],
        [3, 1, 6],
        [3, 2, 8],
        [3, 3, 5],
        [4, 0, 7],
        [4, 1, 5],
        [4, 2, 6],
        [4, 3, 4],
      ],
      label: {
        show: true,
      },
    },
  ],
  visualMap: {
    min: 0,
    max: 10,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '0%',
  },
})
</script>

<style scoped>
.sample-charts {
  padding: 2rem;
}

h2 {
  margin-bottom: 2rem;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.chart-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.chart {
  width: 100%;
  height: 400px;
}
</style>
