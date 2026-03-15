import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/common/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/common/Layout.vue'),
    redirect: '/dashboard',
    children: [
      // 学生路由
      {
        path: 'dashboard',
        name: 'StudentDashboard',
        component: () => import('@/views/student/Dashboard.vue'),
        meta: { title: '学情分析', icon: 'DataLine' }
      },
      {
        path: 'homework',
        name: 'Homework',
        component: () => import('@/views/student/Homework.vue'),
        meta: { title: '我的作业', icon: 'Document' }
      },
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('@/views/student/Upload.vue'),
        meta: { title: '上传作业', icon: 'Upload' }
      },
      // 教师路由
      {
        path: 'review',
        name: 'Review',
        component: () => import('@/views/teacher/Review.vue'),
        meta: { title: '人工审核', icon: 'Edit', roles: ['teacher', 'admin'] }
      },
      {
        path: 'class-dashboard',
        name: 'ClassDashboard',
        component: () => import('@/views/teacher/ClassDashboard.vue'),
        meta: { title: '班级学情', icon: 'School', roles: ['teacher', 'admin'] }
      },
      // 管理员路由
      {
        path: 'overview',
        name: 'Overview',
        component: () => import('@/views/admin/Overview.vue'),
        meta: { title: '平台概览', icon: 'Histogram', roles: ['admin'] }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/common/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.public) {
    next()
    return
  }
  
  if (!userStore.token) {
    next('/login')
    return
  }
  
  // 检查角色权限
  if (to.meta.roles && !to.meta.roles.includes(userStore.userInfo?.role)) {
    next('/')
    return
  }
  
  next()
})

export default router
