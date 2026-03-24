import { useState } from 'react'
import { Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Label } from './ui/Label'
import { Badge } from './ui/Badge'

export function Settings() {
  const [defaultVoice, setDefaultVoice] = useState('p226')
  const [defaultSpeed, setDefaultSpeed] = useState(1.0)
  const [subtitleColor, setSubtitleColor] = useState('#FFFFFF')
  const [highlightColor, setHighlightColor] = useState('#FFFF00')
  const [fontSize, setFontSize] = useState(48)
  const [logoPosition, setLogoPosition] = useState('top-right')
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    // Save to localStorage
    const settings = {
      defaultVoice,
      defaultSpeed,
      subtitleColor,
      highlightColor,
      fontSize,
      logoPosition,
    }
    localStorage.setItem('redditvid-settings', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold gradient-text">Settings</h2>
        <p className="text-muted-foreground mt-2">
          Configure default values for video generation
        </p>
      </div>

      <div className="space-y-6">
        {/* TTS Defaults */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">🎙️ TTS Defaults</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Default Voice</Label>
              <select
                value={defaultVoice}
                onChange={e => setDefaultVoice(e.target.value)}
                className="mt-2 w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="p226">Male - Deep British</option>
                <option value="p227">Male - British Narrator</option>
                <option value="p228">Male - Deep Baritone</option>
                <option value="p232">Male - Warm British</option>
                <option value="p247">Male - Storyteller</option>
                <option value="p251">Male - Clear Narrator</option>
                <option value="p225">Female - British</option>
                <option value="p229">Female - Warm</option>
                <option value="p236">Female - Narrator</option>
              </select>
            </div>

            <div>
              <Label>Default Speed</Label>
              <div className="flex items-center gap-3 mt-2">
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={defaultSpeed}
                  onChange={e => setDefaultSpeed(parseFloat(e.target.value))}
                  className="flex-1 accent-primary"
                />
                <span className="text-sm font-mono text-muted-foreground w-12">
                  {defaultSpeed.toFixed(1)}x
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subtitle Defaults */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">📝 Subtitle Defaults</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Text Color</Label>
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
                <Label>Highlight Color</Label>
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

            <div>
              <Label>Font Size</Label>
              <div className="flex items-center gap-3 mt-2">
                <input
                  type="range"
                  min="24"
                  max="72"
                  step="2"
                  value={fontSize}
                  onChange={e => setFontSize(parseInt(e.target.value))}
                  className="flex-1 accent-primary"
                />
                <span className="text-sm font-mono text-muted-foreground w-12">
                  {fontSize}px
                </span>
              </div>
            </div>

            {/* Subtitle Preview */}
            <div>
              <Label>Preview</Label>
              <div className="mt-2 rounded-lg overflow-hidden">
                <div className="bg-black/70 px-4 py-3 text-center">
                  <span style={{ color: subtitleColor, fontSize: `${Math.min(fontSize / 2.5, 24)}px`, fontWeight: 'bold' }}>
                    This is what{' '}
                  </span>
                  <span style={{ color: highlightColor, fontSize: `${Math.min(fontSize / 2.5, 24)}px`, fontWeight: 'bold' }}>
                    your{' '}
                  </span>
                  <span style={{ color: subtitleColor, fontSize: `${Math.min(fontSize / 2.5, 24)}px`, fontWeight: 'bold' }}>
                    subtitles look like
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Logo Defaults */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">🖼️ Logo Defaults</CardTitle>
          </CardHeader>
          <CardContent>
            <Label>Default Position</Label>
            <div className="grid grid-cols-4 gap-2 mt-2 max-w-xs">
              {[
                { id: 'top-left', label: 'Top Left' },
                { id: 'top-right', label: 'Top Right' },
                { id: 'bottom-left', label: 'Bottom Left' },
                { id: 'bottom-right', label: 'Bottom Right' },
              ].map(pos => (
                <button
                  key={pos.id}
                  onClick={() => setLogoPosition(pos.id)}
                  className={`
                    h-10 rounded-lg text-xs font-medium transition-all duration-150
                    ${logoPosition === pos.id
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'bg-muted/50 text-muted-foreground hover:bg-muted'
                    }
                  `}
                >
                  {pos.label}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">ℹ️ System</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">TTS Engine:</span>
                <Badge variant="secondary" className="ml-2">Coqui VITS</Badge>
              </div>
              <div>
                <span className="text-muted-foreground">Subtitles:</span>
                <Badge variant="secondary" className="ml-2">faster-whisper</Badge>
              </div>
              <div>
                <span className="text-muted-foreground">Video:</span>
                <Badge variant="secondary" className="ml-2">FFmpeg</Badge>
              </div>
              <div>
                <span className="text-muted-foreground">Output:</span>
                <Badge variant="secondary" className="ml-2">1080×1920 H.264</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <Button onClick={handleSave} size="lg" className="w-full h-12">
          {saved ? (
            <>✓ Saved!</>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Defaults
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
