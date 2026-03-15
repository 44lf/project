<template>
  <div class="overview-page">
    <h1>平台概览</h1>
    
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ data.users?.total_students || 0 }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ data.users?.total_teachers || 0 }}</div>
            <div class="stat-label">教师总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-col :span="24">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ data.homework?.total || 0 }}</div>
              <div class="stat-label">作业总数</div>
            </div>
          </el-card>
        </el-col>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ data.average_score || 0 }}</div>
            <div class="stat-label">平台平均分</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>作业状态分布</span>
          </template>
          <div ref="homeworkChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>批改方式分布</span>
          </template>
          <div ref="correctionChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getOverview } from '@/api/dashboard'

const data = ref({})
const homeworkChart = ref(null)
const correctionChart = ref(null)
let homeworkChartInstance = null
let correctionChartInstance = null

const loadData = async () => {
  try {
    const res = await getOverview()
    data.value = res
    
    // 作业状态分布图
    if (homeworkChartInstance) {
      homeworkChartInstance.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: '5%' },
        series: [{
          type: 'pie',
          radius: '60%',
          data: [
            { value: res.homework?.pending || 0, name: '待处理' },
            { value: res.homework?.completed || 0, name: '已完成' }
          ]
        }]
      })
    }
    
    // 批改方式分布图
    if (correctionChartInstance) {
      correctionChartInstance.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: '5%' },
        series: [{
          type: 'pie',
          radius: '60%',
          data: [
            { value: res.corrections?.auto_corrected || 0, name: '自动批改' },
            { value: res.corrections?.manual_review_needed || 0, name: '人工审核' }
          ]
        }]
      })
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  homeworkChartInstance = echarts.init(homeworkChart.value)
  correctionChartInstance = echarts.init(correctionChart.value)
  loadData()
  
  window.addEventListener('resize', () => {
    homeworkChartInstance?.resize()
    correctionChartInstance?.resize()
  })
})

onUnmounted(() => {
  homeworkChartInstance?.dispose()
  correctionChartInstance?.dispose()
})
</script>

<style scoped>
.overview-page h1 {
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
