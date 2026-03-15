import request from './request'

export const uploadHomework = (data) => {
  const formData = new FormData()
  formData.append('subject', data.subject)
  formData.append('title', data.title)
  if (data.description) {
    formData.append('description', data.description)
  }
  formData.append('file', data.file)
  
  return request.post('/homework/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getMyHomework = (params) => {
  return request.get('/homework/my', { params })
}

export const getHomeworkDetail = (id) => {
  return request.get(`/homework/${id}`)
}
