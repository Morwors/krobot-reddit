import { useState, useCallback } from 'react'
import { Upload, Film, X, CheckCircle2 } from 'lucide-react'
import { uploadBackground } from '@/api/client'

interface BackgroundUploadProps {
  onUploaded: (filename: string, originalName: string) => void
  currentFile: string | null
}

export function BackgroundUpload({ onUploaded, currentFile }: BackgroundUploadProps) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(async (file: File) => {
    if (!file.type.startsWith('video/') && !file.name.match(/\.(mp4|webm|mov|avi|mkv)$/i)) {
      setError('Please upload a video file (MP4, WebM, MOV, AVI, MKV)')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const result = await uploadBackground(file)
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
      <label className="text-sm font-medium mb-2 block">Background Video</label>
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
        onClick={() => document.getElementById('bg-upload')?.click()}
      >
        <input
          id="bg-upload"
          type="file"
          accept="video/*,.mp4,.webm,.mov,.avi,.mkv"
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
            <Film className="w-8 h-8 mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Drop video here or <span className="text-primary">browse</span>
            </p>
            <p className="text-xs text-muted-foreground/60">
              MP4, WebM, MOV · Gameplay, subway surfers, etc.
            </p>
          </div>
        )}
      </div>

      {error && (
        <p className="text-xs text-destructive mt-2">{error}</p>
      )}
    </div>
  )
}
