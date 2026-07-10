import type { ReactNode } from 'react'
import JsonViewer from './JsonViewer'
import type { CompileResponse } from '../api'

interface StagePanelProps {
  stageId: string | null
  response: CompileResponse | null
}

function Pill({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'ok' | 'warn' | 'error' }) {
  const colors: Record<string, string> = {
    default: 'var(--text-dim)',
    ok: 'var(--accent-ok)',
    warn: 'var(--accent-warn)',
    error: 'var(--accent-error)',
  }
  return (
    <span
      className="rounded-sm border px-2 py-0.5 text-[11px]"
      style={{ borderColor: 'var(--border-line)', color: colors[tone] }}
    >
      {children}
    </span>
  )
}

function ListBlock({ title, items, tone = 'default' }: { title: string; items: string[]; tone?: 'default' | 'ok' | 'warn' | 'error' }) {
  if (!items || items.length === 0) return null
  return (
    <div className="px-5 py-3" style={{ borderBottom: '1px solid var(--border-line-soft)' }}>
      <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wider" style={{ color: 'var(--text-faint)' }}>
        {title} ({items.length})
      </div>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-[12.5px]" style={{ color: 'var(--text-primary)' }}>
            <span style={{ color: tone === 'default' ? 'var(--text-faint)' : `var(--accent-${tone})` }}>·</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function StagePanel({ stageId, response }: StagePanelProps) {
  if (!response || !stageId) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-center" style={{ color: 'var(--text-faint)' }}>
        <div className="text-[28px]">⌁</div>
        <div className="text-[13px]">Run a prompt to see the compiled stages here.</div>
      </div>
    )
  }

  switch (stageId) {
    case 'intent':
      return <JsonViewer data={response.intent} emptyLabel="no intent extracted" />

    case 'clarify': {
      const c = response.clarification
      return (
        <div>
          <div className="flex flex-wrap items-center gap-2 px-5 py-3" style={{ borderBottom: '1px solid var(--border-line-soft)' }}>
            <Pill tone={c.clarity_score >= 7 ? 'ok' : c.clarity_score >= 4 ? 'warn' : 'error'}>
              clarity {c.clarity_score}/10
            </Pill>
            <Pill tone={c.is_clear ? 'ok' : 'warn'}>{c.is_clear ? 'proceeding clean' : 'proceeding with caveats'}</Pill>
          </div>
          <ListBlock title="ambiguities" items={c.ambiguities} tone="warn" />
          <ListBlock title="conflicts" items={c.conflicts} tone="error" />
          <ListBlock title="assumptions made" items={c.assumptions} tone="default" />
          <ListBlock title="would clarify" items={c.clarifying_questions} tone="default" />
        </div>
      )
    }

    case 'design':
      return <JsonViewer data={response.design} emptyLabel="no design produced" />

    case 'schema':
      return <JsonViewer data={response.schema} emptyLabel="no schema produced" />

    case 'validate': {
      const v = response.validation
      return (
        <div>
          <div className="flex items-center gap-2 px-5 py-3" style={{ borderBottom: '1px solid var(--border-line-soft)' }}>
            <Pill tone={v.passed ? 'ok' : 'error'}>{v.passed ? 'PASSED' : `${v.errors.length} ERROR(S)`}</Pill>
          </div>
          {v.errors.length > 0 ? (
            <ListBlock title="validation errors" items={v.errors} tone="error" />
          ) : (
            <div className="px-5 py-6 text-[13px]" style={{ color: 'var(--text-dim)' }}>
              Schema is cross-consistent — JSON valid, types safe, API↔DB↔UI↔Auth references all resolve.
            </div>
          )}
        </div>
      )
    }

    case 'execute': {
      const e = response.execution as {
        health_check?: { executable: boolean; verdict: string; blocker_count: number }
      }
      return (
        <div>
          {e.health_check && (
            <div className="flex flex-wrap items-center gap-2 px-5 py-3" style={{ borderBottom: '1px solid var(--border-line-soft)' }}>
              <Pill tone={e.health_check.executable ? 'ok' : 'error'}>
                {e.health_check.executable ? 'EXECUTION READY' : 'NOT EXECUTABLE'}
              </Pill>
              <span className="text-[12px]" style={{ color: 'var(--text-dim)' }}>{e.health_check.verdict}</span>
            </div>
          )}
          <JsonViewer data={response.execution} emptyLabel="no execution report" />
        </div>
      )
    }

    case 'meta': {
      const m = response.meta
      return (
        <div className="grid grid-cols-2 gap-px sm:grid-cols-3" style={{ background: 'var(--border-line-soft)' }}>
          {[
            ['total latency', `${m.total_latency_ms} ms`],
            ['retry cycles', String(m.retry_count)],
            ['prompt length', `${m.prompt_length} chars`],
          ].map(([label, val]) => (
            <div key={label} className="px-5 py-4" style={{ background: 'var(--bg-panel)' }}>
              <div className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--text-faint)' }}>{label}</div>
              <div className="mt-1 text-[18px] font-bold" style={{ color: 'var(--accent-signal)' }}>{val}</div>
            </div>
          ))}
          <div className="col-span-full px-5 py-4" style={{ background: 'var(--bg-panel)' }}>
            <div className="mb-2 text-[10px] uppercase tracking-wider" style={{ color: 'var(--text-faint)' }}>stage timings</div>
            <JsonViewer data={m.stage_timings} />
          </div>
        </div>
      )
    }

    default:
      return null
  }
}
