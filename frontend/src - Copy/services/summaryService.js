import apiClient from '../api/client'

export const summaryService = {
  async summarize(videoId, keyword, segments) {
    const response = await apiClient.post('/summarize', {
      video_id: videoId,
      keyword,
      segments,
    })
    return response.data.summary
  },
}

