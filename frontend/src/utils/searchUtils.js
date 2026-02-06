// Stopwords list (same as backend)
const STOPWORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
  'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
  'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
  'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
  'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
  'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more',
  'very', 'after', 'words', 'long', 'than', 'first', 'been', 'call',
  'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get',
  'come', 'made', 'may', 'part', 'i', 'you', 'we', 'she', 'my',
  'me', 'him', 'his', 'her', 'our', 'your', 'their', 'its', 'us',
  'them', 'myself', 'yourself', 'himself', 'herself', 'ourselves',
  'yourselves', 'themselves', 'what', 'which', 'who', 'whom',
  'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
  'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
  'did', 'doing', 'will', 'would', 'shall', 'should', 'may', 'might',
  'must', 'can', 'could', 'ought', 'need', 'dare'
])

export function isStopword(keyword) {
  const keywordLower = keyword.toLowerCase().trim()
  return STOPWORDS.has(keywordLower) || keywordLower.length < 2
}

export function searchKeyword(transcript, keyword) {
  if (!transcript || !keyword) {
    return {
      keyword: keyword || '',
      matches: [],
      segments: [],
      total_count: 0
    }
  }

  const keywordLower = keyword.toLowerCase()
  const matches = []
  const segments = []
  const seenSegments = new Set()

  for (const segment of transcript) {
    const textLower = segment.text.toLowerCase()
    if (textLower.includes(keywordLower)) {
      // Find all occurrences in this segment
      let startPos = 0
      let matchCount = 0
      while (true) {
        const pos = textLower.indexOf(keywordLower, startPos)
        if (pos === -1) break
        
        matches.push({
          start: segment.start,
          end: segment.end,
          text: segment.text,
          match_position: pos
        })
        matchCount++
        startPos = pos + 1
      }

      // Add segment if not already added
      const segmentKey = `${segment.start}-${segment.end}`
      if (!seenSegments.has(segmentKey)) {
        segments.push({
          start: segment.start,
          end: segment.end,
          text: segment.text
        })
        seenSegments.add(segmentKey)
      }
    }
  }

  return {
    keyword,
    matches,
    segments,
    total_count: matches.length
  }
}

