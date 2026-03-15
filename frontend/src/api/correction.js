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

/**
 * 提交人工审核
 * @param {number} correctionId - 批改记录ID
 * @param {object} data - 审核数据 { score, feedback, review_notes }
 * @returns {Promise}
 */
export const submitReview = (correctionId, data) => {
  return request.post(`/reviews/${correctionId}/review`, data)
}
