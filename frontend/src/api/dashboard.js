import request from './request'

export const getStudentDashboard = (studentId) => {
  return request.get(`/dashboard/student/${studentId}`)
}

export const getClassDashboard = (className) => {
  return request.get(`/dashboard/class/${className}`)
}

export const getOverview = () => {
  return request.get('/dashboard/overview')
}
