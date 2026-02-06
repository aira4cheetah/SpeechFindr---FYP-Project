import { useState, useRef, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import { searchKeyword, isStopword } from '../utils/searchUtils'

export default function TranscriptView({
  transcript,
  currentTime,
  onTimestampClick,
  searchResults,
  onSearchResults,
  videoId,
}) {
  const [searchKeywordInput, setSearchKeywordInput] = useState('')
  const transcriptRef = useRef(null)

  const handleSearch = () => {
    if (!searchKeywordInput.trim()) {
      onSearchResults(null)
      return
    }

    // Check for stopwords
    if (isStopword(searchKeywordInput)) {
      alert('Stopwords are not allowed in keyword search. Please use meaningful keywords.')
      return
    }

    // Instant client-side search
    const results = searchKeyword(transcript, searchKeywordInput)
    onSearchResults(results)
  }

  // Auto-search as user types (instant)
  useEffect(() => {
    if (!searchKeywordInput.trim()) {
      onSearchResults(null)
      return
    }

    // Check for stopwords
    if (isStopword(searchKeywordInput)) {
      return
    }

    // Instant search
    const results = searchKeyword(transcript, searchKeywordInput)
    onSearchResults(results)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchKeywordInput, transcript])

  const handleClearSearch = () => {
    setSearchKeywordInput('')
    onSearchResults(null)
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const isSegmentHighlighted = (segment) => {
    if (!searchResults) return false
    return searchResults.segments.some(
      (s) => s.start === segment.start && s.end === segment.end
    )
  }

  const isSegmentActive = (segment) => {
    return currentTime >= segment.start && currentTime <= segment.end
  }

  const highlightKeyword = (text, keyword) => {
    if (!keyword || !searchResults) return text
    const regex = new RegExp(`(${keyword})`, 'gi')
    return text.replace(regex, '<mark class="bg-yellow-500 text-black">$1</mark>')
  }

  // Auto-scroll to active segment
  useEffect(() => {
    const activeElement = transcriptRef.current?.querySelector('.active-segment')
    if (activeElement) {
      activeElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [currentTime])

  return (
    <div className="bg-dark-blue rounded-lg border border-dark-gray h-[calc(100vh-200px)] flex flex-col">
      {/* Search Bar */}
      <div className="p-4 border-b border-dark-gray">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-gray" />
            <input
              type="text"
              value={searchKeywordInput}
              onChange={(e) => setSearchKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search keywords (instant search, stopwords not allowed)..."
              className="w-full pl-10 pr-10 py-2 bg-black border border-dark-gray rounded text-white placeholder-dark-gray focus:outline-none focus:border-blue-500"
            />
            {searchKeywordInput && (
              <button
                onClick={handleClearSearch}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-gray hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
        {searchResults && searchResults.total_count > 0 && (
          <div className="mt-2 text-sm text-dark-gray">
            Found {searchResults.total_count} match{searchResults.total_count !== 1 ? 'es' : ''} for "{searchResults.keyword}"
          </div>
        )}
        {searchKeywordInput && isStopword(searchKeywordInput) && (
          <div className="mt-2 text-sm text-yellow-500">
            Stopwords are not allowed. Please use meaningful keywords.
          </div>
        )}
      </div>

      {/* Transcript List */}
      <div ref={transcriptRef} className="flex-1 overflow-y-auto p-4 space-y-2">
        {transcript.length === 0 ? (
          <div className="text-center text-dark-gray py-8">
            No transcript available
          </div>
        ) : (
          (() => {
            // Filter segments: if searchResults exist, only show matching segments
            const segmentsToShow = searchResults
              ? transcript.filter((segment) =>
                  searchResults.segments.some(
                    (s) => s.start === segment.start && s.end === segment.end
                  )
                )
              : transcript

            if (searchResults && segmentsToShow.length === 0) {
              return (
                <div className="text-center text-dark-gray py-8">
                  No segments found matching "{searchResults.keyword}"
                </div>
              )
            }

            return segmentsToShow.map((segment, index) => {
              const isHighlighted = isSegmentHighlighted(segment)
              const isActive = isSegmentActive(segment)

              return (
                <div
                  key={index}
                  className={`p-3 rounded cursor-pointer transition ${
                    isActive
                      ? 'bg-blue-900 border border-blue-500 active-segment'
                      : isHighlighted
                      ? 'bg-yellow-900 border border-yellow-500'
                      : 'bg-black border border-dark-gray hover:bg-gray-900'
                  }`}
                  onClick={() => onTimestampClick(segment.start)}
                >
                  <div className="flex items-start gap-3">
                    <button
                      className="text-blue-400 hover:text-blue-300 font-mono text-sm whitespace-nowrap"
                      onClick={(e) => {
                        e.stopPropagation()
                        onTimestampClick(segment.start)
                      }}
                    >
                      {formatTime(segment.start)}
                    </button>
                    <p
                      className="flex-1 text-white text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{
                        __html: searchResults
                          ? highlightKeyword(segment.text, searchResults.keyword)
                          : segment.text,
                      }}
                    />
                  </div>
                </div>
              )
            })
          })()
        )}
      </div>
    </div>
  )
}

