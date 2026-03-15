<template>
  <div class="dashboard">
    <h1>学情分析</h1>
    
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_homework || 0 }}</div>
            <div class="stat-label">总作业数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.completed_homework || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.completion_rate || 0 }}%</div>
            <div class="stat-label">完成率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.average_score || 0 }}</div>
            <div class="stat-label">平均分</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>学科分布</span>
          </template>
          <div ref="subjectChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近7天提交趋势</span>
          </template>
          <div ref="trendChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getStudentDashboard } from '@/api/dashboard'
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()
const stats = ref({})
const subjectChart = ref(null)
const trendChart = ref(null)
let subjectChartInstance = null
let trendChartInstance = null

const loadData = async () => {
  try {
    const res = await getStudentDashboard(userStore.userInfo.id)
    stats.value = res.overview
    
    // 渲染学科分布图
    if (subjectChartInstance) {
      subjectChartInstance.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: '5%' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: res.subject_stats.map(item => ({
            name: item.subject,
            value: item.count
          }))
        }]
      })
    }
    
    // 渲染趋势图
    if (trendChartInstance) {
      trendChartInstance.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: res.recent_trend.map(item => item.date)
        },
        yAxis: { type: 'value' },
        series: [{
          data: res.recent_trend.map(item => item.count),
          type: 'line',
          smooth: true
        }]
      })
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  subjectChartInstance = echarts.init(subjectChart.value)
  trendChartInstance = echarts.init(trendChart.value)
  loadData()
  
  window.addEventListener('resize', () => {
    subjectChartInstance?.resize()
    trendChartInstance?.resize()
  })
})

onUnmounted(() => {
  subjectChartInstance?.dispose()
  trendChartInstance?.dispose()
})
</script>

<style scoped>
.dashboard h1 {
  margin-bottom: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  margin-top: 8px;
  color: #909399;
}

.charts-row {
  margin-top: 20px;
}

.chart {
  height: 300px;
}
</style>
