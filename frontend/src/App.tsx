import { useEffect, useRef, useState } from 'react'
import PromptInput from './components/PromptInput'
import StageTracker, { type Stage } from './components/StageTracker'
import StagePanel from './components/StagePanel'
import { compilePrompt, CompileError, type CompileResponse } from './api'

const STAGE_DEFS: { id: string; label: string }[] = [
  { id: 'intent', label: 'intent_extraction' },
  { id: 'clarify', label: 'clarification' },
  { id: 'design', label: 'system_design' },
  { id: 'schema', label: 'schema_generation' },
  { id: 'validate', label: 'validation' },
  { id: 'execute', label: 'execution' },
  { id: 'meta', label: 'pipeline_meta' },
]

function initialStages(): Stage[] {
  return STAGE_DEFS.map((s) => ({ ...s, status: 'pending' as const }))
}

export default function App() {
  const [stages, setStages] = useState<Stage[]>(initialStages())
  const [activeId, setActiveId] = useState<string | null>(null)
  const [response, setResponse] = useState<CompileResponse | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const progressRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (progressRef.current) window.clearInterval(progressRef.current)
    }
  }, [])

  const handleSubmit = async (prompt: string) => {
    setIsRunning(true)
    setError(null)
    setResponse(null)
    setStages(initialStages())
    setActiveId(null)

    // Simulated progression while the single blocking /compile call runs —
    // the backend executes all stages server-side before returning once.
    let cursor = 0
    setStages((prev) => prev.map((s, i) => (i === 0 ? { ...s, status: 'running' } : s)))
    setActiveId(STAGE_DEFS[0].id)

    progressRef.current = window.setInterval(() => {
      cursor += 1
      if (cursor >= STAGE_DEFS.length) {
        if (progressRef.current) window.clearInterval(progressRef.current)
        return
      }
      setStages((prev) =>
        prev.map((s, i) => {
          if (i < cursor) return { ...s, status: 'done' }
          if (i === cursor) return { ...s, status: 'running' }
          return s
        })
      )
      setActiveId(STAGE_DEFS[cursor].id)
    }, 900)

    try {
      const result = await compilePrompt(prompt)
      if (progressRef.current) window.clearInterval(progressRef.current)

      const validatePassed = result.validation.passed
      const clarityLow = !result.clarification.is_clear

      setStages(
        STAGE_DEFS.map((s) => {
          if (s.id === 'validate' && !validatePassed) return { ...s, status: 'warn' }
          if (s.id === 'clarify' && clarityLow) return { ...s, status: 'warn' }
          return { ...s, status: 'done' }
        })
      )
      setResponse(result)
      setActiveId('schema')
    } catch (e) {
      if (progressRef.current) window.clearInterval(progressRef.current)
      const message = e instanceof CompileError ? e.message : 'Unexpected error contacting the compiler.'
      setError(message)
      setStages((prev) =>
        prev.map((s, i) => (i === cursor ? { ...s, status: 'error' } : i < cursor ? { ...s, status: 'done' } : s))
      )
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="flex h-screen flex-col" style={{ background: 'var(--bg-void)' }}>
      <header
        className="flex shrink-0 items-center justify-between px-5 py-3"
        style={{ borderBottom: '1px solid var(--border-line)' }}
      >
        <div className="flex items-baseline gap-3">
          <h1 className="text-[15px] font-bold tracking-tight">
            Compylr<span style={{ color: 'var(--accent-signal)' }}>AI</span>
          </h1>
          <span className="text-[11px]" style={{ color: 'var(--text-faint)' }}>
            natural language → validated, executable application schema
          </span>
        </div>
        <span className="text-[11px]" style={{ color: 'var(--text-faint)' }}>v1.0.0</span>
      </header>

      <PromptInput onSubmit={handleSubmit} isRunning={isRunning} />

      {error && (
        <div
          className="fade-in-up mx-5 mt-3 rounded-sm border px-4 py-2 text-[12.5px]"
          style={{ borderColor: 'var(--accent-error)', color: 'var(--accent-error)', background: 'rgba(251,111,111,0.06)' }}
        >
          ✗ {error}
        </div>
      )}

      <div className="flex min-h-0 flex-1">
        <aside
          className="w-[240px] shrink-0 overflow-y-auto"
          style={{ borderRight: '1px solid var(--border-line)', background: 'var(--bg-panel)' }}
        >
          <StageTracker stages={stages} activeId={activeId} onSelect={setActiveId} />
        </aside>

        <main className="min-w-0 flex-1 overflow-y-auto" style={{ background: 'var(--bg-input)' }}>
          {activeId && (
            <div
              className="sticky top-0 z-10 px-5 py-2 text-[11px] font-bold uppercase tracking-wider backdrop-blur"
              style={{ borderBottom: '1px solid var(--border-line)', background: 'rgba(13,15,18,0.9)', color: 'var(--text-dim)' }}
            >
              {STAGE_DEFS.find((s) => s.id === activeId)?.label ?? activeId}
            </div>
          )}
          <StagePanel stageId={activeId} response={response} />
        </main>
      </div>
    </div>
  )
}
