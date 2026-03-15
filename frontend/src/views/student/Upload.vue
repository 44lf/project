<template>
  <div class="upload-page">
    <h1>上传作业</h1>
    
    <el-card class="upload-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="学科" prop="subject">
          <el-select v-model="form.subject" placeholder="请选择学科">
            <el-option label="语文" value="chinese" />
            <el-option label="数学" value="math" />
            <el-option label="英语" value="english" />
            <el-option label="物理" value="physics" />
            <el-option label="化学" value="chemistry" />
            <el-option label="生物" value="biology" />
            <el-option label="历史" value="history" />
            <el-option label="地理" value="geography" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入作业标题" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            rows="3"
            placeholder="请输入作业描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="作业图片" prop="file">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".jpg,.jpeg,.png,.gif,.bmp"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 JPG、PNG、GIF、BMP 格式，文件大小不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="uploading"
            @click="handleSubmit"
          >
            提交作业
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadHomework } from '@/api/homework'
import { useRouter } from 'vue-router'

const router = useRouter()
const formRef = ref(null)
const uploading = ref(false)

const form = reactive({
  subject: '',
  title: '',
  description: '',
  file: null
})

const rules = {
  subject: [{ required: true, message: '请选择学科', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  file: [{ required: true, message: '请上传作业图片', trigger: 'change' }]
}

const handleFileChange = (file) => {
  form.file = file.raw
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  if (!form.file) {
    ElMessage.warning('请上传作业图片')
    return
  }
  
  uploading.value = true
  try {
    await uploadHomework(form)
    ElMessage.success('作业上传成功')
    router.push('/homework')
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.file = null
}
</script>

<style scoped>
.upload-page h1 {
  margin-bottom: 20px;
}

.upload-card {
  max-width: 600px;
}
</style>
