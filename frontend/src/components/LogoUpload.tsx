import { useState, useCallback } from 'react'
import { ImageIcon, CheckCircle2 } from 'lucide-react'
import { uploadLogo } from '@/api/client'
import { cn } from '@/lib/utils'

interface LogoUploadProps {
  onUploaded: (filename: string, originalName: string) => void
  currentFile: string | null
  position: string
  onPositionChange: (position: string) => void
}

const positions = [
  { id: 'top-left', label: 'TL' },
  { id: 'top-right', label: 'TR' },
  { id: 'bottom-left', label: 'BL' },
  { id: 'bottom-right', label: 'BR' },
]

export function LogoUpload({ onUploaded, currentFile, position, onPositionChange }: LogoUploadProps) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file (PNG, JPG, WebP)')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const result = await uploadLogo(file)
      onUploaded(result.filename, result.original_name)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [onUploaded])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }, [handleFile])

  return (
    <div>
      <label className="text-sm font-medium mb-2 block">Logo / Watermark</label>
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200
          ${dragging
            ? 'border-primary bg-primary/5 scale-[1.02]'
            : currentFile
              ? 'border-green-500/30 bg-green-500/5'
              : 'border-border hover:border-primary/50 hover:bg-muted/30'
          }
          ${uploading ? 'opacity-60 pointer-events-none' : ''}
        `}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('logo-upload')?.click()}
      >
        <input
          id="logo-upload"
          type="file"
          accept="image/*,.png,.jpg,.jpeg,.webp,.svg"
          className="hidden"
          onChange={handleInputChange}
        />

        {uploading ? (
          <div className="space-y-2">
            <div className="w-8 h-8 mx-auto border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-muted-foreground">Uploading...</p>
          </div>
        ) : currentFile ? (
          <div className="space-y-2">
            <CheckCircle2 className="w-8 h-8 mx-auto text-green-500" />
            <p className="text-sm font-medium text-green-400">{currentFile}</p>
            <p className="text-xs text-muted-foreground">Click or drop to replace</p>
          </div>
        ) : (
          <div className="space-y-2">
            <ImageIcon className="w-8 h-8 mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Drop logo here or <span className="text-primary">browse</span>
            </p>
            <p className="text-xs text-muted-foreground/60">
              PNG, JPG, WebP · Transparent recommended
            </p>
          </div>
        )}
      </div>

      {/* Position Selector */}
      <div className="mt-3">
        <label className="text-xs text-muted-foreground mb-2 block">Logo Position</label>
        <div className="grid grid-cols-2 gap-1.5 w-24">
          {positions.map(pos => (
            <button
              key={pos.id}
              onClick={(e) => { e.stopPropagation(); onPositionChange(pos.id) }}
              className={cn(
                'h-8 rounded text-xs font-mono transition-all duration-150',
                position === pos.id
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'bg-muted/50 text-muted-foreground hover:bg-muted'
              )}
            >
              {pos.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p className="text-xs text-destructive mt-2">{error}</p>
      )}
    </div>
  )
}
