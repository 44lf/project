<template>
  <div class="class-dashboard">
    <h1>班级学情分析</h1>
    
    <el-form :inline="true" class="search-form">
      <el-form-item label="班级">
        <el-select v-model="selectedClass" placeholder="请选择班级" @change="loadData">
          <el-option label="一年级一班" value="一年级一班" />
          <el-option label="一年级二班" value="一年级二班" />
          <el-option label="二年级一班" value="二年级一班" />
          <el-option label="二年级二班" value="二年级二班" />
        </el-select>
      </el-form-item>
    </el-form>
    
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.student_count || 0 }}</div>
            <div class="stat-label">学生人数</div>
          </div>
        </el-card>
      </el-col>
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
            <div class="stat-value">{{ stats.completion_rate || 0 }}%</div>
            <div class="stat-label">完成率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.average_score || 0 }}</div>
            <div class="stat-label">班级平均分</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>学科成绩分布</span>
          </template>
          <div ref="subjectChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>优秀学生TOP10</span>
          </template>
          <el-table :data="topStudents" size="small">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="avg_score" label="平均分" width="100">
              <template #default="{ row }">
                <el-tag :type="row.avg_score >= 90 ? 'success' : row.avg_score >= 60 ? 'warning' : 'danger'">
                  {{ row.avg_score }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="homework_count" label="作业数" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getClassDashboard } from '@/api/dashboard'

const selectedClass = ref('一年级一班')
const stats = ref({})
const topStudents = ref([])
const subjectChart = ref(null)
let subjectChartInstance = null

const loadData = async () => {
  try {
    const res = await getClassDashboard(selectedClass.value)
    stats.value = res.overview
    topStudents.value = res.top_students
    
    // 渲染学科分布图
    if (subjectChartInstance) {
      subjectChartInstance.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: res.subject_stats.map(item => item.subject)
        },
        yAxis: { type: 'value', max: 100 },
        series: [{
          data: res.subject_stats.map(item => item.avg_score),
          type: 'bar',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }]
      })
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  subjectChartInstance = echarts.init(subjectChart.value)
  loadData()
  
  window.addEventListener('resize', () => {
    subjectChartInstance?.resize()
  })
})

onUnmounted(() => {
  subjectChartInstance?.dispose()
})
</script>

<style scoped>
.class-dashboard h1 {
  margin-bottom: 20px;
}

.search-form {
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
