import { useState } from 'react'
import { FileText, Loader2 } from 'lucide-react'
import { summaryService } from '../services/summaryService'

export default function SummaryView({
  summary,
  onSummaryGenerated,
  videoId,
  keyword,
  segments,
}) {
  const [isGenerating, setIsGenerating] = useState(false)

  const handleSummarize = async () => {
    if (!keyword || segments.length === 0) {
      alert('Please search for a keyword first to generate a summary')
      return
    }

    setIsGenerating(true)
    try {
      const generatedSummary = await summaryService.summarize(
        videoId,
        keyword,
        segments
      )
      onSummaryGenerated(generatedSummary)
    } catch (error) {
      if (error.response?.status === 400) {
        alert('Stopwords are not allowed. Please use meaningful keywords.')
      } else {
        alert(`Error: ${error.response?.data?.detail || error.message}`)
      }
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="bg-dark-blue rounded-lg border border-dark-gray p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Summary
        </h2>
        <button
          onClick={handleSummarize}
          disabled={isGenerating || !keyword || segments.length === 0}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generating...
            </>
          ) : (
            'Summarize'
          )}
        </button>
      </div>

      {summary ? (
        <div className="bg-black rounded p-4 border border-dark-gray">
          <p className="text-white text-sm leading-relaxed whitespace-pre-wrap">
            {summary}
          </p>
        </div>
      ) : (
        <div className="bg-black rounded p-4 border border-dark-gray text-center text-dark-gray">
          {keyword && segments.length > 0
            ? 'Click "Summarize" to generate a summary of the search results'
            : 'Search for a keyword first, then click "Summarize"'}
        </div>
      )}
    </div>
  )
}

