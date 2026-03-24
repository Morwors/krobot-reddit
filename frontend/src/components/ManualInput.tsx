import { Textarea } from './ui/Textarea'
import { Input } from './ui/Input'
import { Label } from './ui/Label'

interface ManualInputProps {
  title: string
  body: string
  onUpdate: (title: string, body: string) => void
}

export function ManualInput({ title, body, onUpdate }: ManualInputProps) {
  return (
    <div className="space-y-4 pt-4">
      <div>
        <Label htmlFor="manual-title">Title</Label>
        <Input
          id="manual-title"
          placeholder="AITA for telling my roommate to stop using my Netflix?"
          value={title}
          onChange={e => onUpdate(e.target.value, body)}
          className="mt-2"
        />
      </div>
      <div>
        <Label htmlFor="manual-body">Story / Script</Label>
        <Textarea
          id="manual-body"
          placeholder="Paste your Reddit post text or write a custom script here..."
          value={body}
          onChange={e => onUpdate(title, e.target.value)}
          className="mt-2 min-h-[200px] resize-y"
          rows={8}
        />
        <p className="text-xs text-muted-foreground mt-2">
          {body.split(/\s+/).filter(Boolean).length} words · ~{Math.ceil(body.split(/\s+/).filter(Boolean).length / 2.5)}s narration
        </p>
      </div>
    </div>
  )
}
