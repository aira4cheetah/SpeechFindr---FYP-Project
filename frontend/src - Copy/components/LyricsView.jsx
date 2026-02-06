import { useEffect, useRef } from 'react'

export default function LyricsView({ lyrics = [], currentTime = 0, onSeek }) {
  const listRef = useRef(null)

  useEffect(() => {
    const activeEl = listRef.current?.querySelector('.active-lyric')
    if (activeEl) {
      //activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [currentTime])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const isActive = (segment) => {
    return currentTime >= segment.start && currentTime <= (segment.end ?? segment.start + 5)
  }

  return (

    //Secondary Transcript Section - Lyrics View
    
    /*<div className="bg-black rounded-lg border border-dark-gray mt-4 p-3 max-h-56 overflow-y-auto" ref={listRef}>
      {lyrics.length === 0 ? (
        <div className="text-dark-gray text-sm">No lyrics available</div>
      ) : (
        lyrics.map((seg, idx) => (
          <div
            key={idx}
            className={`py-2 px-2 rounded cursor-pointer transition ${isActive(seg) ? 'bg-blue-900 active-lyric' : 'hover:bg-gray-900'}`}
            onClick={() => onSeek?.(seg.start)}
          >
            <div className="flex items-center gap-3">
              <button className="text-blue-400 font-mono text-sm whitespace-nowrap" onClick={(e) => { e.stopPropagation(); onSeek?.(seg.start) }}>
                {formatTime(seg.start)}
              </button>
              <div className="text-white text-sm">{seg.text}</div>
            </div>
          </div>
        ))
      )}
    </div>*/
  null)
}
