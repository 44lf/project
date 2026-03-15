<template>
  <div class="homework-page">
    <h1>我的作业</h1>
    
    <div class="toolbar">
      <el-button type="primary" :icon="Refresh" @click="loadData" :loading="loading">
        刷新列表
      </el-button>
      <el-switch
        v-model="autoRefresh"
        active-text="自动刷新"
        inactive-text="手动刷新"
        style="margin-left: 20px;"
      />
      <span v-if="autoRefresh" class="refresh-tip">
        （每5秒自动刷新）
      </span>
    </div>
    
    <el-table :data="homeworkList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="subject" label="学科" width="100">
        <template #default="{ row }">
          <el-tag>{{ subjectMap[row.subject] || row.subject }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]" effect="dark">
            <el-icon v-if="row.status === 'processing'" class="is-loading">
              <Loading />
            </el-icon>
            {{ statusMap[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button link type="primary" @click="viewDetail(row)">
            查看详情
          </el-button>
          <el-button 
            v-if="row.status === 'completed' && row.correction" 
            link 
            type="success" 
            @click="viewCorrection(row)"
          >
            查看批改
          </el-button>
          <el-button 
            v-if="row.status === 'processing'" 
            link 
            type="warning"
            :loading="loading"
            @click="checkStatus(row)"
          >
            检查状态
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="作业详情" width="600px">
      <div v-if="currentHomework">
        <p><strong>学科：</strong>{{ subjectMap[currentHomework.subject] }}</p>
        <p><strong>标题：</strong>{{ currentHomework.title }}</p>
        <p><strong>描述：</strong>{{ currentHomework.description || '无' }}</p>
        <p><strong>状态：</strong>
          <el-tag :type="statusType[currentHomework.status]" effect="dark">
            <el-icon v-if="currentHomework.status === 'processing'" class="is-loading">
              <Loading />
            </el-icon>
            {{ statusMap[currentHomework.status] }}
          </el-tag>
          <span v-if="currentHomework.status === 'processing'" class="status-tip">
            （批改中，请稍候...）
          </span>
        </p>
        <p><strong>提交时间：</strong>{{ formatDate(currentHomework.created_at) }}</p>
        <div v-if="currentHomework.file_path">
          <strong>作业图片：</strong>
          <el-image
            :src="getImageUrl(currentHomework.file_path)"
            style="max-width: 100%; margin-top: 10px;"
            :preview-src-list="[getImageUrl(currentHomework.file_path)]"
          />
        </div>
      </div>
    </el-dialog>
    
    <!-- 批改结果对话框 -->
    <el-dialog v-model="correctionVisible" title="批改结果" width="600px">
      <div v-if="currentCorrection">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="得分">
            <span class="score">{{ currentCorrection.score }}</span>
            / 100
          </el-descriptions-item>
          <el-descriptions-item label="评语">
            {{ currentCorrection.feedback }}
          </el-descriptions-item>
          <el-descriptions-item label="OCR识别内容">
            <div class="ocr-text">{{ currentCorrection.ocr_text || '无' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="识别置信度">
            <el-progress 
              :percentage="Math.round(currentCorrection.ocr_confidence * 100)" 
              :status="currentCorrection.ocr_confidence > 0.7 ? 'success' : 'exception'"
            />
          </el-descriptions-item>
          <el-descriptions-item v-if="currentCorrection.needs_manual_review" label="审核状态">
            <el-tag type="warning">人工审核</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Refresh } from '@element-plus/icons-vue'
import { getMyHomework, getHomeworkDetail } from '@/api/homework'
import { getCorrectionByHomework } from '@/api/correction'
import dayjs from 'dayjs'

const loading = ref(false)
const homeworkList = ref([])
const detailVisible = ref(false)
const correctionVisible = ref(false)
const currentHomework = ref(null)
const currentCorrection = ref(null)
const autoRefresh = ref(false)
let refreshTimer = null

const subjectMap = {
  chinese: '语文',
  math: '数学',
  english: '英语',
  physics: '物理',
  chemistry: '化学',
  biology: '生物',
  history: '历史',
  geography: '地理'
}

const statusMap = {
  pending: '待处理',
  processing: '批改中',
  reviewing: '审核中',
  completed: '已完成',
  failed: '失败'
}

const statusType = {
  pending: 'info',
  processing: 'warning',
  reviewing: 'warning',
  completed: 'success',
  failed: 'danger'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取图片完整URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `/uploads/${path.replace('uploads/', '').replace('uploads\\', '')}`
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyHomework()
    homeworkList.value = res
  } catch (error) {
    console.error('加载作业列表失败:', error)
    ElMessage.error('加载作业列表失败')
  } finally {
    loading.value = false
  }
}

// 检查单个作业状态
const checkStatus = async (row) => {
  try {
    const res = await getHomeworkDetail(row.id)
    // 更新列表中的作业状态
    const index = homeworkList.value.findIndex(h => h.id === row.id)
    if (index !== -1) {
      homeworkList.value[index] = { ...homeworkList.value[index], ...res }
    }
    
    if (res.status === 'completed') {
      ElMessage.success('批改完成！')
    } else if (res.status === 'processing') {
      ElMessage.info('仍在批改中，请稍候...')
    } else if (res.status === 'reviewing') {
      ElMessage.info('正在人工审核中...')
    }
  } catch (error) {
    console.error('检查状态失败:', error)
    ElMessage.error('检查状态失败')
  }
}

const viewDetail = async (row) => {
  try {
    const res = await getHomeworkDetail(row.id)
    currentHomework.value = res
    detailVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  }
}

const viewCorrection = async (row) => {
  try {
    const res = await getCorrectionByHomework(row.id)
    currentCorrection.value = res
    correctionVisible.value = true
  } catch (error) {
    console.error('获取批改结果失败:', error)
    ElMessage.error('获取批改结果失败')
  }
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  refreshTimer = setInterval(() => {
    // 检查是否有processing状态的作业
    const hasProcessing = homeworkList.value.some(h => h.status === 'processing' || h.status === 'reviewing')
    if (hasProcessing) {
      loadData()
    }
  }, 5000) // 每5秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听自动刷新开关
watch(autoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
    ElMessage.success('已开启自动刷新')
  } else {
    stopAutoRefresh()
    ElMessage.info('已关闭自动刷新')
  }
})

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.homework-page h1 {
  margin-bottom: 20px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.refresh-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 14px;
}

.status-tip {
  margin-left: 10px;
  color: #e6a23c;
  font-size: 14px;
}

.score {
  font-size: 24px;
  font-weight: bold;
  color: #67C23A;
}

.ocr-text {
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}

.is-loading {
  animation: rotating 2s linear infinite;
  margin-right: 4px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
