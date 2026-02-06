import { useRef, useEffect, useState } from 'react'
import ReactPlayer from 'react-player'

export default function VideoPlayer({
  videoData,
  currentTime,
  onTimeUpdate,
}) {
  const playerRef = useRef(null)
  const isSeekingRef = useRef(false)
  const lastSeekTimeRef = useRef(0)
  const wasPlayingRef = useRef(false)

  useEffect(() => {
    // Only seek if it's a user-initiated seek (not from video playback)
    // Check if the time difference is significant (user clicked timestamp)
    if (playerRef.current && currentTime > 0) {
      const timeDiff = Math.abs(currentTime - lastSeekTimeRef.current)
      // If time difference is > 2 seconds, it's likely a user click
      if (timeDiff > 2) {
        // Check if video is currently playing
        try {
          const internalPlayer = playerRef.current.getInternalPlayer()
          if (internalPlayer) {
            wasPlayingRef.current = internalPlayer.getPlayerState() === 1 // 1 = playing
          }
        } catch (e) {
          wasPlayingRef.current = true // Assume playing if we can't check
        }
        
        isSeekingRef.current = true
        playerRef.current.seekTo(currentTime, 'seconds')
        lastSeekTimeRef.current = currentTime
        
        // Reset seeking flag and resume playback after seek
        setTimeout(() => {
          isSeekingRef.current = false
          // Resume playback if it was playing before
          if (wasPlayingRef.current) {
            try {
              const internalPlayer = playerRef.current?.getInternalPlayer()
              if (internalPlayer && internalPlayer.getPlayerState() !== 1) {
                internalPlayer.playVideo()
              }
            } catch (e) {
              // Ignore errors
            }
          }
        }, 300)
      }
    }
  }, [currentTime])

  const getVideoUrl = () => {
    if (videoData.url) return videoData.url
    // If a local file was provided (from upload), use an object URL
    if (videoData.localFile) return localObjectUrl
    if (videoData.video_id && videoData.video_id.startsWith('upload_')) {
      // For uploaded videos without a served URL, playback may not be available
      return null
    }
    return `https://www.youtube.com/watch?v=${videoData.video_id}`
  }

  const [localObjectUrl, setLocalObjectUrl] = useState(null)

  useEffect(() => {
    if (videoData?.localFile) {
      const url = URL.createObjectURL(videoData.localFile)
      setLocalObjectUrl(url)
      return () => {
        URL.revokeObjectURL(url)
        setLocalObjectUrl(null)
      }
    }
    return undefined
  }, [videoData])

  const videoUrl = getVideoUrl()

  if (!videoUrl) {
    return (
      <div className="bg-dark-blue rounded-lg border border-dark-gray p-8 text-center">
        <p className="text-dark-gray">Video playback not available for uploaded files</p>
      </div>
    )
  }

  return (
    <div className="bg-dark-blue rounded-lg border border-dark-gray overflow-hidden">
      <div className="aspect-video bg-black">
        <ReactPlayer
          ref={playerRef}
          url={videoUrl}
          width="100%"
          height="100%"
          controls
          onProgress={(state) => {
            // Only update time if not currently seeking (to prevent pause/jump)
            if (!isSeekingRef.current) {
              onTimeUpdate(state.playedSeconds)
              lastSeekTimeRef.current = state.playedSeconds
            }
          }}
          onSeek={() => {
            // Mark as seeking when user manually seeks
            isSeekingRef.current = true
            setTimeout(() => {
              isSeekingRef.current = false
            }, 200)
          }}
          config={{
            youtube: {
              playerVars: {
                controls: 1,
                modestbranding: 1,
              },
            },
          }}
        />
      </div>
      {videoData.title && (
        <div className="p-4">
          <h3 className="text-white font-semibold">{videoData.title}</h3>
        </div>
      )}
    </div>
  )
}

