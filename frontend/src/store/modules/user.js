import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  
  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isStudent = computed(() => userInfo.value?.role === 'student')
  const isTeacher = computed(() => userInfo.value?.role === 'teacher')
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  
  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }
  
  const clearToken = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }
  
  const loginAction = async (credentials) => {
    const res = await login(credentials)
    setToken(res.access_token)
    await fetchUserInfo()
    return res
  }
  
  const fetchUserInfo = async () => {
    const res = await getUserInfo()
    userInfo.value = res
    return res
  }
  
  const logout = () => {
    clearToken()
  }
  
  return {
    token,
    userInfo,
    isLoggedIn,
    isStudent,
    isTeacher,
    isAdmin,
    setToken,
    clearToken,
    loginAction,
    fetchUserInfo,
    logout
  }
})
