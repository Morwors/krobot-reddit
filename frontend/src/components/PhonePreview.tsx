import { Smartphone, ImageIcon } from 'lucide-react'

interface PhonePreviewProps {
  title: string
  body: string
  subreddit: string
  subtitleColor: string
  highlightColor: string
  logoPosition: string
  hasLogo: boolean
  hasBackground: boolean
}

export function PhonePreview({
  title,
  body,
  subreddit,
  subtitleColor,
  highlightColor,
  logoPosition,
  hasLogo,
  hasBackground,
}: PhonePreviewProps) {
  const words = body ? body.split(/\s+/).slice(0, 12) : ['Your', 'subtitles', 'will', 'appear', 'here']
  const highlightIdx = 2 // Simulate highlighted word

  // Logo position classes
  const logoPositionClasses: Record<string, string> = {
    'top-left': 'top-2 left-2',
    'top-right': 'top-2 right-2',
    'bottom-left': 'bottom-16 left-2',
    'bottom-right': 'bottom-16 right-2',
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <Smartphone className="w-5 h-5 text-primary" />
        <h3 className="font-semibold text-sm">Preview</h3>
        <span className="text-xs text-muted-foreground ml-auto">9:16</span>
      </div>

      {/* Phone frame */}
      <div className="mx-auto w-[240px] rounded-[24px] border-2 border-zinc-700 bg-zinc-900 p-1.5 shadow-2xl shadow-primary/10">
        {/* Notch */}
        <div className="flex justify-center mb-1">
          <div className="w-16 h-1.5 rounded-full bg-zinc-700" />
        </div>

        {/* Screen */}
        <div
          className="relative rounded-[18px] overflow-hidden"
          style={{ aspectRatio: '9/16' }}
        >
          {/* Background */}
          <div className={`absolute inset-0 ${hasBackground ? 'bg-gradient-to-b from-zinc-800 via-zinc-700 to-zinc-800' : 'bg-gradient-to-b from-[#1a1a2e] via-[#16213e] to-[#0f3460]'}`}>
            {hasBackground && (
              <div className="absolute inset-0 flex items-center justify-center opacity-20">
                <ImageIcon className="w-12 h-12 text-zinc-500" />
              </div>
            )}
          </div>

          {/* Logo placeholder */}
          {hasLogo && (
            <div className={`absolute ${logoPositionClasses[logoPosition] || 'top-2 right-2'} z-20`}>
              <div className="w-6 h-6 rounded bg-white/20 border border-white/30 flex items-center justify-center">
                <span className="text-[6px] font-bold text-white/70">LOGO</span>
              </div>
            </div>
          )}

          {/* Subreddit badge */}
          {subreddit && (
            <div className="absolute top-4 left-3 z-10">
              <span className="text-[7px] bg-purple-600/80 text-white px-1.5 py-0.5 rounded-full font-medium">
                r/{subreddit}
              </span>
            </div>
          )}

          {/* Reddit card */}
          <div className="absolute top-[15%] left-2 right-2 z-10">
            <div className="bg-[#14141e]/85 backdrop-blur-sm rounded-lg p-2.5 border border-white/5">
              {title ? (
                <>
                  <p className="text-[8px] font-bold text-white leading-tight mb-1.5 line-clamp-3">
                    {title}
                  </p>
                  <div className="w-full h-px bg-white/10 mb-1.5" />
                  <p className="text-[6px] text-zinc-300 leading-relaxed line-clamp-6">
                    {body || 'Story text will appear here...'}
                  </p>
                </>
              ) : (
                <div className="space-y-1.5 py-2">
                  <div className="h-2 bg-white/10 rounded w-3/4" />
                  <div className="h-1.5 bg-white/5 rounded w-full" />
                  <div className="h-1.5 bg-white/5 rounded w-5/6" />
                  <div className="h-1.5 bg-white/5 rounded w-2/3" />
                </div>
              )}
            </div>
          </div>

          {/* Subtitle bar */}
          <div className="absolute bottom-0 left-0 right-0 z-10">
            <div className="bg-black/70 px-2 py-2">
              <p className="text-center leading-relaxed">
                {words.map((word, i) => (
                  <span
                    key={i}
                    className="text-[7px] font-bold"
                    style={{
                      color: i === highlightIdx ? highlightColor : subtitleColor,
                    }}
                  >
                    {word}{' '}
                  </span>
                ))}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Format info */}
      <div className="mt-4 text-center space-y-1">
        <p className="text-[10px] text-muted-foreground">
          1080 × 1920 · H.264 · AAC
        </p>
        <div className="flex justify-center gap-2">
          {['TikTok', 'Shorts', 'Reels'].map(platform => (
            <span
              key={platform}
              className="text-[9px] px-1.5 py-0.5 rounded bg-muted/50 text-muted-foreground"
            >
              {platform}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
