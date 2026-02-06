import { useState } from 'react'
import { Upload, Link as LinkIcon } from 'lucide-react'
import { videoService } from '../services/videoService'

export default function VideoInput({
  onVideoLoaded,
  onTranscriptLoaded,
  setLoading,
  setLoadingMessage,
}) {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [inputMode, setInputMode] = useState('youtube')

  const handleYouTubeSubmit = async (e) => {
    e.preventDefault()
    if (!youtubeUrl.trim()) return

    setLoading(true)
    setLoadingMessage('Fetching YouTube video...')

    try {
      const videoData = await videoService.fetchYouTube(youtubeUrl)
      onVideoLoaded(videoData)

      setLoadingMessage('Transcribing audio...')
      const transcript = await videoService.getTranscript(videoData.video_id)
      onTranscriptLoaded(transcript)
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
      setLoadingMessage('')
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)
    setLoadingMessage('Uploading video...')

    try {
      const videoData = await videoService.uploadVideo(file)
      // Include the local file so the player can play immediately via object URL
      onVideoLoaded({ ...videoData, localFile: file })

      setLoadingMessage('Transcribing audio...')
      const transcript = await videoService.getTranscript(videoData.video_id)
      onTranscriptLoaded(transcript)
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
      setLoadingMessage('')
    }
  }

  return (
    <div className="bg-dark-blue p-6 rounded-lg border border-dark-gray">
      <div className="flex gap-4 mb-4">
        <button
          onClick={() => setInputMode('youtube')}
          className={`px-4 py-2 rounded ${
            inputMode === 'youtube'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-dark-gray hover:bg-gray-700'
          }`}
        >
          <LinkIcon className="inline-block w-4 h-4 mr-2" />
          YouTube Link
        </button>
        <button
          onClick={() => setInputMode('upload')}
          className={`px-4 py-2 rounded ${
            inputMode === 'upload'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-dark-gray hover:bg-gray-700'
          }`}
        >
          <Upload className="inline-block w-4 h-4 mr-2" />
          Upload Video
        </button>
      </div>

      {inputMode === 'youtube' ? (
        <form onSubmit={handleYouTubeSubmit} className="flex gap-2">
          <input
            type="text"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="Enter YouTube URL..."
            className="flex-1 px-4 py-2 bg-black border border-dark-gray rounded text-white placeholder-dark-gray focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Process
          </button>
        </form>
      ) : (
        <div>
          <label className="block mb-2 text-dark-gray">Select video file:</label>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileUpload}
            className="block w-full text-sm text-dark-gray file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
          />
        </div>
      )}
    </div>
  )
}

