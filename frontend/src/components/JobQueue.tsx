import { motion } from 'framer-motion'
import {
  Download,
  Trash2,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Film,
  AlertCircle,
} from 'lucide-react'
import { Card, CardContent } from './ui/Card'
import { Button } from './ui/Button'
import { Badge } from './ui/Badge'
import { Progress } from './ui/Progress'
import { getDownloadUrl, type JobInfo } from '@/api/client'

interface JobQueueProps {
  jobs: JobInfo[]
  loading: boolean
  error: string | null
  fetchJobs: () => void
  removeJob: (id: string) => void
}

const statusConfig = {
  queued: { icon: Clock, color: 'warning' as const, label: 'Queued' },
  processing: { icon: Loader2, color: 'info' as const, label: 'Processing' },
  done: { icon: CheckCircle2, color: 'success' as const, label: 'Done' },
  failed: { icon: XCircle, color: 'destructive' as const, label: 'Failed' },
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
}

function formatTime(isoString: string): string {
  try {
    const date = new Date(isoString)
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoString
  }
}

export function JobQueue({ jobs, loading, error, fetchJobs, removeJob }: JobQueueProps) {
  const handleDelete = async (id: string) => {
    if (confirm('Delete this job and its video?')) {
      try {
        await removeJob(id)
      } catch {
        // handled in hook
      }
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold gradient-text">Queue & History</h2>
          <p className="text-muted-foreground mt-2">
            {jobs.length} job{jobs.length !== 1 ? 's' : ''} total
          </p>
        </div>
        <Button variant="outline" onClick={fetchJobs} size="sm">
          Refresh
        </Button>
      </div>

      {loading && jobs.length === 0 && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive mb-6">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {!loading && jobs.length === 0 && (
        <div className="text-center py-20">
          <Film className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
          <h3 className="text-lg font-semibold text-muted-foreground">No videos yet</h3>
          <p className="text-sm text-muted-foreground/60 mt-1">
            Create your first video to see it here
          </p>
        </div>
      )}

      <div className="space-y-3">
        {jobs.map((job, index) => {
          const config = statusConfig[job.status] || statusConfig.queued
          const StatusIcon = config.icon

          return (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className={`transition-all duration-200 hover:border-primary/20 ${
                job.status === 'processing' ? 'border-primary/30 shadow-lg shadow-primary/5' : ''
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    {/* Status icon */}
                    <div className={`mt-0.5 p-2 rounded-lg ${
                      job.status === 'done' ? 'bg-green-500/10' :
                      job.status === 'failed' ? 'bg-destructive/10' :
                      job.status === 'processing' ? 'bg-primary/10' :
                      'bg-muted/50'
                    }`}>
                      <StatusIcon className={`w-5 h-5 ${
                        job.status === 'done' ? 'text-green-500' :
                        job.status === 'failed' ? 'text-destructive' :
                        job.status === 'processing' ? 'text-primary animate-spin' :
                        'text-muted-foreground'
                      }`} />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm truncate">{job.title}</h4>
                        <Badge variant={config.color} className="text-xs flex-shrink-0">
                          {config.label}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>{formatTime(job.created_at)}</span>
                        {job.duration && <span>{formatDuration(job.duration)}</span>}
                        <span className="font-mono">{job.id.slice(0, 8)}</span>
                      </div>

                      {/* Progress bar */}
                      {job.status === 'processing' && (
                        <div className="mt-2">
                          <Progress value={job.progress * 100} className="h-1.5" />
                          <p className="text-[10px] text-muted-foreground mt-1">
                            {Math.round(job.progress * 100)}% complete
                          </p>
                        </div>
                      )}

                      {/* Error message */}
                      {job.status === 'failed' && job.error && (
                        <p className="text-xs text-destructive mt-2 line-clamp-2">
                          {job.error}
                        </p>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      {job.status === 'done' && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-8 px-3"
                          onClick={() => window.open(getDownloadUrl(job.id), '_blank')}
                        >
                          <Download className="w-3.5 h-3.5 mr-1.5" />
                          Download
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                        onClick={() => handleDelete(job.id)}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
