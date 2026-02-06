import { useState } from 'react'
import VideoInput from './components/VideoInput'
import VideoPlayer from './components/VideoPlayer'
import TranscriptView from './components/TranscriptView'
import SummaryView from './components/SummaryView'
import LyricsView from './components/LyricsView'

function App() {
  const [videoData, setVideoData] = useState(null)
  const [transcript, setTranscript] = useState([])
  const [currentTime, setCurrentTime] = useState(0)
  const [searchResults, setSearchResults] = useState(null)
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('')

  return (
    <div className="min-h-screen bg-black text-dark-gray">
      <div className="container mx-auto px-4 py-6">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">SpeechFindr</h1>
          <p className="text-dark-gray">Fast Speech Search & Summarization</p>
        </header>

        <VideoInput
          onVideoLoaded={setVideoData}
          onTranscriptLoaded={setTranscript}
          setLoading={setLoading}
          setLoadingMessage={setLoadingMessage}
        />

        {loading && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-dark-blue p-8 rounded-lg border border-dark-gray">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-white text-lg">{loadingMessage}</p>
            </div>
          </div>
        )}

        {videoData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            {/* Left Column: Video Player + Summary */}
            <div className="lg:col-span-1 space-y-6">
              <VideoPlayer
                videoData={videoData}
                currentTime={currentTime}
                onTimeUpdate={setCurrentTime}
              />
              <LyricsView
                lyrics={transcript}
                currentTime={currentTime}
                onSeek={setCurrentTime}
              />
              <SummaryView
                summary={summary}
                onSummaryGenerated={setSummary}
                videoId={videoData.video_id}
                keyword={searchResults?.keyword || ''}
                segments={searchResults?.segments || []}
              />
            </div>

            {/* Right Column: Transcript */}
            <div className="lg:col-span-2">
              <TranscriptView
                transcript={transcript}
                currentTime={currentTime}
                onTimestampClick={setCurrentTime}
                searchResults={searchResults}
                onSearchResults={setSearchResults}
                videoId={videoData.video_id}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

