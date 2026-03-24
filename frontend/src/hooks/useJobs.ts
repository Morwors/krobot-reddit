import { useState, useEffect, useCallback, useRef } from 'react'
import { getJobs, getJob, deleteJob as apiDeleteJob, type JobInfo } from '@/api/client'

export function useJobs(pollInterval = 3000) {
  const [jobs, setJobs] = useState<JobInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval>>()

  const fetchJobs = useCallback(async () => {
    try {
      const data = await getJobs()
      setJobs(data.jobs)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch jobs')
    } finally {
      setLoading(false)
    }
  }, [])

  const pollJob = useCallback(async (jobId: string) => {
    try {
      const job = await getJob(jobId)
      setJobs(prev => {
        const idx = prev.findIndex(j => j.id === jobId)
        if (idx >= 0) {
          const updated = [...prev]
          updated[idx] = job
          return updated
        }
        return [job, ...prev]
      })
      return job
    } catch {
      return null
    }
  }, [])

  const removeJob = useCallback(async (jobId: string) => {
    await apiDeleteJob(jobId)
    setJobs(prev => prev.filter(j => j.id !== jobId))
  }, [])

  const addJob = useCallback((job: JobInfo) => {
    setJobs(prev => [job, ...prev])
  }, [])

  useEffect(() => {
    fetchJobs()

    intervalRef.current = setInterval(() => {
      // Only poll if there are active jobs
      setJobs(prevJobs => {
        const activeJobs = prevJobs.filter(
          j => j.status === 'queued' || j.status === 'processing'
        )
        if (activeJobs.length > 0) {
          fetchJobs()
        }
        return prevJobs
      })
    }, pollInterval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [fetchJobs, pollInterval])

  return { jobs, loading, error, fetchJobs, pollJob, removeJob, addJob }
}
