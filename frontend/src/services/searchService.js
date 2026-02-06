import apiClient from '../api/client'

export const searchService = {
  async searchKeyword(keyword, videoId) {
    const response = await apiClient.get('/search', {
      params: {
        keyword,
        video_id: videoId,
      },
    })
    return response.data
  },
}

