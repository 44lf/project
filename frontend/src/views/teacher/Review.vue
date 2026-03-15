<template>
  <div class="review-page">
    <h1>人工审核</h1>
    
    <el-alert
      v-if="pendingCount > 0"
      :title="`有 ${pendingCount} 个作业需要人工审核`"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <el-alert
      v-else
      title="暂无需要人工审核的作业"
      type="success"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;"
    />
    
    <el-table :data="correctionList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="homework.subject" label="学科" width="100">
        <template #default="{ row }">
          <el-tag>{{ subjectMap[row.homework?.subject] || row.homework?.subject }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="homework.title" label="作业标题" />
      <el-table-column prop="ocr_confidence" label="OCR置信度" width="120">
        <template #default="{ row }">
          <el-progress 
            :percentage="Math.round(row.ocr_confidence * 100)" 
            :status="row.ocr_confidence > 0.7 ? 'success' : 'exception'"
          />
        </template>
      </el-table-column>
      <el-table-column prop="ocr_text" label="识别内容" show-overflow-tooltip />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleReview(row)">
            审核
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 审核对话框 -->
    <el-dialog v-model="reviewVisible" title="人工审核" width="700px">
      <div v-if="currentCorrection">
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>作业图片</h4>
            <el-image
              v-if="currentCorrection.homework?.file_path"
              :src="getImageUrl(currentCorrection.homework.file_path)"
              style="width: 100%; max-height: 300px;"
              :preview-src-list="[getImageUrl(currentCorrection.homework.file_path)]"
            />
          </el-col>
          <el-col :span="12">
            <h4>OCR识别结果</h4>
            <div class="ocr-result">
              <p><strong>置信度：</strong>{{ Math.round(currentCorrection.ocr_confidence * 100) }}%</p>
              <p><strong>识别内容：</strong></p>
              <div class="ocr-text">{{ currentCorrection.ocr_text || '无' }}</div>
            </div>
          </el-col>
        </el-row>
        
        <el-divider />
        
        <h4>审核评分</h4>
        <el-form :model="reviewForm" label-width="80px">
          <el-form-item label="得分">
            <el-slider v-model="reviewForm.score" :max="100" show-input />
          </el-form-item>
          <el-form-item label="评语">
            <el-input
              v-model="reviewForm.feedback"
              type="textarea"
              rows="3"
              placeholder="请输入评语"
            />
          </el-form-item>
          <el-form-item label="审核备注">
            <el-input
              v-model="reviewForm.review_notes"
              type="textarea"
              rows="2"
              placeholder="内部审核备注（学生不可见）"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReview">
          提交审核
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCorrections, submitReview } from '@/api/correction'

const loading = ref(false)
const submitting = ref(false)
const correctionList = ref([])
const pendingCount = ref(0)
const reviewVisible = ref(false)
const currentCorrection = ref(null)

const reviewForm = ref({
  score: 80,
  feedback: '',
  review_notes: ''
})

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

// 获取图片完整URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `/uploads/${path.replace('uploads/', '').replace('uploads\\', '')}`
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCorrections()
    // 过滤出需要人工审核的
    correctionList.value = res.filter(item => item.needs_manual_review === 1 || item.status === 'pending_review')
    pendingCount.value = correctionList.value.length
  } catch (error) {
    console.error('加载审核列表失败:', error)
    ElMessage.error('加载审核列表失败')
  } finally {
    loading.value = false
  }
}

const handleReview = (row) => {
  currentCorrection.value = row
  reviewForm.value = {
    score: row.score || 80,
    feedback: row.feedback || '',
    review_notes: ''
  }
  reviewVisible.value = true
}

const submitReview = async () => {
  if (!currentCorrection.value) {
    ElMessage.error('未选择批改记录')
    return
  }
  
  submitting.value = true
  try {
    // 调用审核API: POST /api/v1/reviews/{correction_id}/review
    await submitReview(currentCorrection.value.id, {
      score: reviewForm.value.score,
      feedback: reviewForm.value.feedback,
      review_notes: reviewForm.value.review_notes
    })
    
    ElMessage.success('审核提交成功')
    reviewVisible.value = false
    // 刷新列表
    await loadData()
  } catch (error) {
    console.error('提交审核失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.review-page h1 {
  margin-bottom: 20px;
}

.ocr-result {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.ocr-text {
  max-height: 150px;
  overflow-y: auto;
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  margin-top: 8px;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style>
