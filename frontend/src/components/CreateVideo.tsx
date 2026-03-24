import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Wand2, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Button } from './ui/Button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/Tabs'
import { RedditScraper } from './RedditScraper'
import { ManualInput } from './ManualInput'
import { BackgroundUpload } from './BackgroundUpload'
import { LogoUpload } from './LogoUpload'
import { VoiceSelector } from './VoiceSelector'
import { PhonePreview } from './PhonePreview'
import { generateVideo, type JobInfo, type ScrapedPost } from '@/api/client'
import { Badge } from './ui/Badge'
import { Label } from './ui/Label'
import { Input } from './ui/Input'

interface CreateVideoProps {
  onJobCreated: (job: JobInfo) => void
}

export function CreateVideo({ onJobCreated }: CreateVideoProps) {
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [subreddit, setSubreddit] = useState('')
  const [backgroundFilename, setBackgroundFilename] = useState<string | null>(null)
  const [backgroundOriginalName, setBackgroundOriginalName] = useState<string | null>(null)
  const [logoFilename, setLogoFilename] = useState<string | null>(null)
  const [logoOriginalName, setLogoOriginalName] = useState<string | null>(null)
  const [logoPosition, setLogoPosition] = useState('top-right')
  const [selectedVoice, setSelectedVoice] = useState('p226')
  const [speed, setSpeed] = useState(1.0)
  const [subtitleColor, setSubtitleColor] = useState('#FFFFFF')
  const [highlightColor, setHighlightColor] = useState('#FFFF00')
  const [generating, setGenerating] = useState(false)
  const [lastJob, setLastJob] = useState<JobInfo | null>(null)

  const handleScraped = useCallback((post: ScrapedPost) => {
    setTitle(post.title)
    setBody(post.selftext)
    setSubreddit(post.subreddit)
  }, [])

  const handleManualInput = useCallback((t: string, b: string) => {
    setTitle(t)
    setBody(b)
    setSubreddit('')
  }, [])

  const handleGenerate = async () => {
    if (!title.trim() || !body.trim()) return

    setGenerating(true)
    try {
      const job = await generateVideo({
        title: title.trim(),
        body: body.trim(),
        subreddit: subreddit || undefined,
        background_filename: backgroundFilename || undefined,
        logo_filename: logoFilename || undefined,
        logo_position: logoPosition,
        voice: selectedVoice,
        speed,
        subtitle_settings: {
          font_size: 48,
          text_color: subtitleColor,
          highlight_color: highlightColor,
          bg_opacity: 0.7,
        },
      })
      setLastJob(job)
      onJobCreated(job)
    } catch (err) {
      console.error('Generation failed:', err)
    } finally {
      setGenerating(false)
    }
  }

  const canGenerate = title.trim().length > 0 && body.trim().length > 0

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold gradient-text">Create Video</h2>
        <p className="text-muted-foreground mt-2">
          Generate Reddit-style narrated videos for TikTok, YouTube Shorts, and Reels
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content - Left 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          {/* Source Content */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full gradient-purple flex items-center justify-center text-xs font-bold text-white">1</span>
                Content Source
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="scrape">
                <TabsList className="w-full">
                  <TabsTrigger value="scrape" className="flex-1">Scrape Reddit</TabsTrigger>
                  <TabsTrigger value="manual" className="flex-1">Manual Input</TabsTrigger>
                </TabsList>
                <TabsContent value="scrape">
                  <RedditScraper onScraped={handleScraped} />
                </TabsContent>
                <TabsContent value="manual">
                  <ManualInput
                    title={title}
                    body={body}
                    onUpdate={handleManualInput}
                  />
                </TabsContent>
              </Tabs>

              {/* Current Script Preview */}
              {title && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 p-4 rounded-lg bg-muted/30 border border-border"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="info">Script Preview</Badge>
                    {subreddit && <Badge variant="secondary">r/{subreddit}</Badge>}
                  </div>
                  <h4 className="font-semibold text-sm mb-1">{title}</h4>
                  <p className="text-xs text-muted-foreground line-clamp-3">{body}</p>
                </motion.div>
              )}
            </CardContent>
          </Card>

          {/* Media Uploads */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full gradient-purple flex items-center justify-center text-xs font-bold text-white">2</span>
                Media Assets
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <BackgroundUpload
                  onUploaded={(filename, originalName) => {
                    setBackgroundFilename(filename)
                    setBackgroundOriginalName(originalName)
                  }}
                  currentFile={backgroundOriginalName}
                />
                <LogoUpload
                  onUploaded={(filename, originalName) => {
                    setLogoFilename(filename)
                    setLogoOriginalName(originalName)
                  }}
                  currentFile={logoOriginalName}
                  position={logoPosition}
                  onPositionChange={setLogoPosition}
                />
              </div>
            </CardContent>
          </Card>

          {/* Voice & Style Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full gradient-purple flex items-center justify-center text-xs font-bold text-white">3</span>
                Voice & Style
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <VoiceSelector
                    selectedVoice={selectedVoice}
                    onVoiceChange={setSelectedVoice}
                  />

                  <div>
                    <Label>Narration Speed</Label>
                    <div className="flex items-center gap-3 mt-2">
                      <input
                        type="range"
                        min="0.5"
                        max="2.0"
                        step="0.1"
                        value={speed}
                        onChange={e => setSpeed(parseFloat(e.target.value))}
                        className="flex-1 accent-primary"
                      />
                      <span className="text-sm font-mono text-muted-foreground w-12">
                        {speed.toFixed(1)}x
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label>Subtitle Text Color</Label>
                    <div className="flex items-center gap-2 mt-2">
                      <input
                        type="color"
                        value={subtitleColor}
                        onChange={e => setSubtitleColor(e.target.value)}
                        className="w-10 h-10 rounded border border-input cursor-pointer"
                      />
                      <Input
                        value={subtitleColor}
                        onChange={e => setSubtitleColor(e.target.value)}
                        className="flex-1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Highlight Color (Active Word)</Label>
                    <div className="flex items-center gap-2 mt-2">
                      <input
                        type="color"
                        value={highlightColor}
                        onChange={e => setHighlightColor(e.target.value)}
                        className="w-10 h-10 rounded border border-input cursor-pointer"
                      />
                      <Input
                        value={highlightColor}
                        onChange={e => setHighlightColor(e.target.value)}
                        className="flex-1"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generate Button */}
          <motion.div
            whileHover={{ scale: canGenerate ? 1.01 : 1 }}
            whileTap={{ scale: canGenerate ? 0.99 : 1 }}
          >
            <Button
              size="lg"
              className="w-full h-14 text-lg font-semibold"
              disabled={!canGenerate || generating}
              onClick={handleGenerate}
            >
              {generating ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Starting Generation...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5 mr-2" />
                  Generate Video
                </>
              )}
            </Button>
          </motion.div>

          {/* Last Job Status */}
          {lastJob && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card className="border-primary/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Job submitted</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {lastJob.title} · ID: {lastJob.id.slice(0, 8)}...
                      </p>
                    </div>
                    <Badge variant={lastJob.status === 'queued' ? 'warning' : 'info'}>
                      {lastJob.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>

        {/* Phone Preview - Right column */}
        <div className="lg:col-span-1">
          <div className="sticky top-8">
            <PhonePreview
              title={title}
              body={body}
              subreddit={subreddit}
              subtitleColor={subtitleColor}
              highlightColor={highlightColor}
              logoPosition={logoPosition}
              hasLogo={!!logoFilename}
              hasBackground={!!backgroundFilename}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
