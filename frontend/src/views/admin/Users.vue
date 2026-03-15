<template>
  <div class="users-page">
    <h1>用户管理</h1>
    
    <el-row class="toolbar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>添加用户
      </el-button>
    </el-row>
    
    <el-table :data="userList" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="full_name" label="姓名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="roleType[row.role]">{{ roleMap[row.role] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="grade" label="年级" width="100" />
      <el-table-column prop="class_name" label="班级" width="100" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="年级" v-if="form.role === 'student'">
          <el-input v-model="form.grade" placeholder="如：一年级" />
        </el-form-item>
        <el-form-item label="班级" v-if="form.role === 'student'">
          <el-input v-model="form.class_name" placeholder="如：一班" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const userList = ref([])
const formRef = ref(null)

const form = ref({
  username: '',
  password: '',
  full_name: '',
  email: '',
  role: 'student',
  grade: '',
  class_name: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const roleMap = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

const roleType = {
  student: '',
  teacher: 'success',
  admin: 'danger'
}

// 模拟数据
const mockUsers = [
  { id: 1, username: 'student1', full_name: '张三', email: 'student1@test.com', role: 'student', grade: '一年级', class_name: '一班', is_active: true },
  { id: 2, username: 'student2', full_name: '李四', email: 'student2@test.com', role: 'student', grade: '一年级', class_name: '一班', is_active: true },
  { id: 3, username: 'teacher1', full_name: '王老师', email: 'teacher1@test.com', role: 'teacher', grade: null, class_name: null, is_active: true },
  { id: 4, username: 'admin', full_name: '管理员', email: 'admin@test.com', role: 'admin', grade: null, class_name: null, is_active: true }
]

const loadData = async () => {
  loading.value = true
  try {
    // 实际项目中应该调用API
    // const res = await getUsers()
    // userList.value = res
    userList.value = mockUsers
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    username: '',
    password: '',
    full_name: '',
    email: '',
    role: 'student',
    grade: '',
    class_name: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.full_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadData()
  })
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    // 实际项目中应该调用API
    // if (isEdit.value) {
    //   await updateUser(form.value.id, form.value)
    // } else {
    //   await createUser(form.value)
    // }
    ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.users-page h1 {
  margin-bottom: 20px;
}

.toolbar {
  margin-bottom: 20px;
}
</style>
