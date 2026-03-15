import request from './request'

export const getCorrections = (params) => {
  return request.get('/corrections/', { params })
}

export const getCorrectionDetail = (id) => {
  return request.get(`/corrections/${id}`)
}

export const getCorrectionByHomework = (homeworkId) => {
  return request.get(`/corrections/homework/${homeworkId}`)
}

export const retryCorrection = (id) => {
  return request.post(`/corrections/${id}/retry`)
}
