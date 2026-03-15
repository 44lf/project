import request from './request'

export const login = (data) => {
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  return request.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getUserInfo = () => {
  return request.get('/auth/me')
}
