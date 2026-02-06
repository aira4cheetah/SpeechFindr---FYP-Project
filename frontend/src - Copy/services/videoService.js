import apiClient from '../api/client'

export const videoService = {
  async fetchYouTube(url) {
    const response = await apiClient.post('/fetch_youtube', { url })
    return response.data
  },

  async uploadVideo(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/upload_video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getTranscript(videoId) {
    const response = await apiClient.get('/transcript', {
      params: { video_id: videoId },
    })
    return response.data.transcript
  },
}

