<template>
  <div class="homework-page">
    <h1>我的作业</h1>
    
    <el-table :data="homeworkList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="subject" label="学科" width="100">
        <template #default="{ row }">
          <el-tag>{{ subjectMap[row.subject] || row.subject }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]">
            {{ statusMap[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button link type="primary" @click="viewDetail(row)">
            查看详情
          </el-button>
          <el-button 
            v-if="row.correction" 
            link 
            type="success" 
            @click="viewCorrection(row)"
          >
            查看批改
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
          <el-tag :type="statusType[currentHomework.status]">
            {{ statusMap[currentHomework.status] }}
          </el-tag>
        </p>
        <p><strong>提交时间：</strong>{{ formatDate(currentHomework.created_at) }}</p>
        <div v-if="currentHomework.file_path">
          <strong>作业图片：</strong>
          <el-image
            :src="currentHomework.file_path"
            style="max-width: 100%; margin-top: 10px;"
            :preview-src-list="[currentHomework.file_path]"
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
            / {{ currentCorrection.max_score }}
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
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyHomework, getHomeworkDetail } from '@/api/homework'
import { getCorrectionByHomework } from '@/api/correction'
import dayjs from 'dayjs'

const loading = ref(false)
const homeworkList = ref([])
const detailVisible = ref(false)
const correctionVisible = ref(false)
const currentHomework = ref(null)
const currentCorrection = ref(null)

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
  processing: '处理中',
  completed: '已完成',
  failed: '失败'
}

const statusType = {
  pending: 'info',
  processing: 'warning',
  completed: 'success',
  failed: 'danger'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyHomework()
    homeworkList.value = res
  } finally {
    loading.value = false
  }
}

const viewDetail = async (row) => {
  try {
    const res = await getHomeworkDetail(row.id)
    currentHomework.value = res
    detailVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

const viewCorrection = async (row) => {
  try {
    const res = await getCorrectionByHomework(row.id)
    currentCorrection.value = res
    correctionVisible.value = true
  } catch (error) {
    console.error('获取批改结果失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.homework-page h1 {
  margin-bottom: 20px;
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
}
</style>
