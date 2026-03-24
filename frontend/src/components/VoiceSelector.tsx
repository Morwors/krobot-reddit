import { useState, useEffect } from 'react'
import { Mic } from 'lucide-react'
import { getVoices, type VoiceInfo } from '@/api/client'
import { Label } from './ui/Label'

interface VoiceSelectorProps {
  selectedVoice: string
  onVoiceChange: (voice: string) => void
}

// Fallback voices in case API is not available
const FALLBACK_VOICES: VoiceInfo[] = [
  { id: 'p226', name: 'Male - Deep British', gender: 'male', description: 'Deep, authoritative British male voice' },
  { id: 'p227', name: 'Male - British Narrator', gender: 'male', description: 'Clear British male narrator' },
  { id: 'p228', name: 'Male - Deep Baritone', gender: 'male', description: 'Deep baritone male voice' },
  { id: 'p232', name: 'Male - Warm British', gender: 'male', description: 'Warm, friendly British male' },
  { id: 'p243', name: 'Male - Standard British', gender: 'male', description: 'Standard British male voice' },
  { id: 'p245', name: 'Male - Young British', gender: 'male', description: 'Younger British male voice' },
  { id: 'p246', name: 'Male - Deep Smooth', gender: 'male', description: 'Deep, smooth male voice' },
  { id: 'p247', name: 'Male - Storyteller', gender: 'male', description: 'Engaging storyteller male voice' },
  { id: 'p251', name: 'Male - Clear Narrator', gender: 'male', description: 'Clear, professional male narrator' },
  { id: 'p252', name: 'Male - Authoritative', gender: 'male', description: 'Authoritative male voice' },
  { id: 'p225', name: 'Female - British', gender: 'female', description: 'Clear British female voice' },
  { id: 'p229', name: 'Female - Warm', gender: 'female', description: 'Warm female voice' },
  { id: 'p236', name: 'Female - Narrator', gender: 'female', description: 'Professional female narrator' },
]

export function VoiceSelector({ selectedVoice, onVoiceChange }: VoiceSelectorProps) {
  const [voices, setVoices] = useState<VoiceInfo[]>(FALLBACK_VOICES)

  useEffect(() => {
    getVoices()
      .then(data => setVoices(data.voices))
      .catch(() => setVoices(FALLBACK_VOICES))
  }, [])

  const selected = voices.find(v => v.id === selectedVoice) || voices[0]

  return (
    <div>
      <Label className="flex items-center gap-2">
        <Mic className="w-4 h-4" />
        Narrator Voice
      </Label>
      <select
        value={selectedVoice}
        onChange={e => onVoiceChange(e.target.value)}
        className="mt-2 w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition-colors cursor-pointer"
      >
        <optgroup label="Male Voices">
          {voices.filter(v => v.gender === 'male').map(voice => (
            <option key={voice.id} value={voice.id}>
              {voice.name}
            </option>
          ))}
        </optgroup>
        <optgroup label="Female Voices">
          {voices.filter(v => v.gender === 'female').map(voice => (
            <option key={voice.id} value={voice.id}>
              {voice.name}
            </option>
          ))}
        </optgroup>
      </select>
      {selected && (
        <p className="text-xs text-muted-foreground mt-1.5">{selected.description}</p>
      )}
    </div>
  )
}
