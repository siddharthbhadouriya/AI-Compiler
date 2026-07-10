// API client for the Compylr AI backend.
// Set VITE_API_BASE_URL in a .env file when deploying (see .env.example).

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface ClarificationResult {
  clarity_score: number
  is_clear: boolean
  ambiguities: string[]
  conflicts: string[]
  assumptions: string[]
  clarifying_questions: string[]
}

export interface ValidationResult {
  passed: boolean
  errors: string[]
}

export interface CompileMeta {
  total_latency_ms: number
  stage_timings: Record<string, number | number[]>
  retry_count: number
  prompt_length: number
}

export interface CompileResponse {
  intent: Record<string, unknown>
  clarification: ClarificationResult
  design: Record<string, unknown>
  schema: Record<string, unknown>
  validation: ValidationResult
  execution: Record<string, unknown>
  meta: CompileMeta
}

export class CompileError extends Error {
  status?: number
  constructor(message: string, status?: number) {
    super(message)
    this.name = 'CompileError'
    this.status = status
  }
}

export async function compilePrompt(prompt: string): Promise<CompileResponse> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}/compile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    })
  } catch {
    throw new CompileError(
      `Could not reach the compiler backend at ${API_BASE_URL}. Is it running?`
    )
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      /* ignore parse failure */
    }
    throw new CompileError(detail, res.status)
  }

  return res.json()
}
