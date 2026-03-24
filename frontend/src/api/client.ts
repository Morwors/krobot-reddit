const API_BASE = '/api'

export interface ScrapedPost {
  title: string
  selftext: string
  subreddit: string
  author: string
  score: number
  num_comments: number
  url: string
}

export interface SubtitleSettings {
  font_size: number
  text_color: string
  highlight_color: string
  bg_opacity: number
}

export interface GenerateRequest {
  title: string
  body: string
  subreddit?: string
  background_filename?: string
  logo_filename?: string
  logo_position: string
  voice: string
  speed: number
  subtitle_settings?: SubtitleSettings
}

export interface JobInfo {
  id: string
  title: string
  status: 'queued' | 'processing' | 'done' | 'failed'
  progress: number
  created_at: string
  completed_at?: string
  error?: string
  output_filename?: string
  duration?: number
}

export interface UploadResponse {
  filename: string
  original_name: string
  size: number
}

export interface VoiceInfo {
  id: string
  name: string
  gender: string
  description: string
}

// ── API Functions ──────────────────────────────────────────────────

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...(options?.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `Request failed: ${res.status}`)
  }

  return res.json()
}

export async function scrapeReddit(url: string): Promise<ScrapedPost> {
  return request<ScrapedPost>('/scrape', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}

export async function generateVideo(data: GenerateRequest): Promise<JobInfo> {
  return request<JobInfo>('/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getJobs(): Promise<{ jobs: JobInfo[] }> {
  return request<{ jobs: JobInfo[] }>('/jobs')
}

export async function getJob(id: string): Promise<JobInfo> {
  return request<JobInfo>(`/jobs/${id}`)
}

export async function deleteJob(id: string): Promise<void> {
  return request<void>(`/jobs/${id}`, { method: 'DELETE' })
}

export function getDownloadUrl(id: string): string {
  return `${API_BASE}/jobs/${id}/download`
}

export async function uploadBackground(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  return request<UploadResponse>('/upload/background', {
    method: 'POST',
    body: formData,
  })
}

export async function uploadLogo(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  return request<UploadResponse>('/upload/logo', {
    method: 'POST',
    body: formData,
  })
}

export async function getVoices(): Promise<{ voices: VoiceInfo[] }> {
  return request<{ voices: VoiceInfo[] }>('/voices')
}
