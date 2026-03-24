import { useState } from 'react'
import { Search, Loader2, ExternalLink, ArrowUp, MessageSquare } from 'lucide-react'
import { Input } from './ui/Input'
import { Button } from './ui/Button'
import { Badge } from './ui/Badge'
import { scrapeReddit, type ScrapedPost } from '@/api/client'

interface RedditScraperProps {
  onScraped: (post: ScrapedPost) => void
}

export function RedditScraper({ onScraped }: RedditScraperProps) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [scraped, setScraped] = useState<ScrapedPost | null>(null)

  const handleScrape = async () => {
    if (!url.trim()) return

    setLoading(true)
    setError(null)

    try {
      const post = await scrapeReddit(url.trim())
      setScraped(post)
      onScraped(post)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scraping failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4 pt-4">
      <div className="flex gap-2">
        <Input
          placeholder="https://reddit.com/r/AmItheAsshole/comments/..."
          value={url}
          onChange={e => setUrl(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleScrape()}
          className="flex-1"
        />
        <Button
          onClick={handleScrape}
          disabled={!url.trim() || loading}
          className="min-w-[100px]"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <Search className="w-4 h-4 mr-2" />
              Scrape
            </>
          )}
        </Button>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
          {error}
        </div>
      )}

      {scraped && (
        <div className="p-4 rounded-lg bg-muted/30 border border-border space-y-3 animate-fade-in">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="default">r/{scraped.subreddit}</Badge>
            <Badge variant="secondary" className="flex items-center gap-1">
              <ArrowUp className="w-3 h-3" />
              {scraped.score.toLocaleString()}
            </Badge>
            <Badge variant="secondary" className="flex items-center gap-1">
              <MessageSquare className="w-3 h-3" />
              {scraped.num_comments.toLocaleString()}
            </Badge>
            <span className="text-xs text-muted-foreground ml-auto">
              u/{scraped.author}
            </span>
          </div>

          <h4 className="font-semibold text-sm leading-snug">{scraped.title}</h4>

          {scraped.selftext && (
            <p className="text-sm text-muted-foreground leading-relaxed max-h-48 overflow-y-auto">
              {scraped.selftext}
            </p>
          )}

          <div className="flex items-center justify-between pt-2 border-t border-border">
            <a
              href={scraped.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary hover:underline flex items-center gap-1"
            >
              <ExternalLink className="w-3 h-3" />
              View on Reddit
            </a>
            <span className="text-xs text-muted-foreground">
              {scraped.selftext.split(' ').length} words
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
