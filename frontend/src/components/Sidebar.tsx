import { cn } from '@/lib/utils'
import {
  Video,
  ListOrdered,
  Settings as SettingsIcon,
  Sparkles,
  Film,
} from 'lucide-react'
import { Badge } from './ui/Badge'

type Page = 'create' | 'queue' | 'settings'

interface SidebarProps {
  currentPage: Page
  onNavigate: (page: Page) => void
  activeJobCount: number
}

const navItems = [
  { id: 'create' as Page, label: 'Create Video', icon: Sparkles },
  { id: 'queue' as Page, label: 'Queue & History', icon: ListOrdered },
  { id: 'settings' as Page, label: 'Settings', icon: SettingsIcon },
]

export function Sidebar({ currentPage, onNavigate, activeJobCount }: SidebarProps) {
  return (
    <aside className="w-64 border-r border-border bg-card/50 flex flex-col h-full">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl gradient-purple flex items-center justify-center shadow-lg shadow-primary/25">
            <Film className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg gradient-text">RedditVid</h1>
            <p className="text-xs text-muted-foreground">Video Generator</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(item => {
          const Icon = item.icon
          const isActive = currentPage === item.id
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-primary/15 text-primary border border-primary/20 shadow-sm'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
              )}
            >
              <Icon className={cn('w-5 h-5', isActive && 'text-primary')} />
              <span>{item.label}</span>
              {item.id === 'queue' && activeJobCount > 0 && (
                <Badge variant="default" className="ml-auto text-xs px-2 py-0.5 min-w-[1.25rem] flex items-center justify-center">
                  {activeJobCount}
                </Badge>
              )}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="glass rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Video className="w-4 h-4 text-primary" />
            <span className="text-xs font-medium">Output Format</span>
          </div>
          <p className="text-xs text-muted-foreground">
            1080×1920 · 9:16 · H.264
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            TikTok · Shorts · Reels
          </p>
        </div>
      </div>
    </aside>
  )
}
