export type StageStatus = 'pending' | 'running' | 'done' | 'error' | 'warn'

export interface Stage {
  id: string
  label: string
  status: StageStatus
}

function Glyph({ status }: { status: StageStatus }) {
  switch (status) {
    case 'done':
      return <span style={{ color: 'var(--accent-ok)' }}>✓</span>
    case 'error':
      return <span style={{ color: 'var(--accent-error)' }}>✗</span>
    case 'warn':
      return <span style={{ color: 'var(--accent-warn)' }}>!</span>
    case 'running':
      return (
        <span className="spin-glyph" style={{ color: 'var(--accent-signal)' }}>
          ◐
        </span>
      )
    default:
      return <span style={{ color: 'var(--text-faint)' }}>○</span>
  }
}

interface StageTrackerProps {
  stages: Stage[]
  activeId: string | null
  onSelect: (id: string) => void
}

export default function StageTracker({ stages, activeId, onSelect }: StageTrackerProps) {
  return (
    <div className="flex flex-col">
      <div
        className="px-4 py-2 text-[10px] font-bold uppercase tracking-[0.15em]"
        style={{ color: 'var(--text-faint)', borderBottom: '1px solid var(--border-line)' }}
      >
        build log
      </div>
      <div className="flex flex-col py-1">
        {stages.map((stage, i) => {
          const isActive = stage.id === activeId
          const disabled = stage.status === 'pending'
          return (
            <button
              key={stage.id}
              onClick={() => !disabled && onSelect(stage.id)}
              disabled={disabled}
              className="group flex items-center gap-2.5 px-4 py-2 text-left text-[12.5px] transition-colors disabled:cursor-not-allowed"
              style={{
                background: isActive ? 'var(--bg-panel-alt)' : 'transparent',
                borderLeft: `2px solid ${isActive ? 'var(--accent-signal)' : 'transparent'}`,
              }}
            >
              <span
                className="w-4 shrink-0 select-none text-right text-[10px]"
                style={{ color: 'var(--text-faint)' }}
              >
                {String(i + 1).padStart(2, '0')}
              </span>
              <span className="w-4 shrink-0 text-center">
                <Glyph status={stage.status} />
              </span>
              <span
                style={{
                  color: disabled ? 'var(--text-faint)' : isActive ? 'var(--text-primary)' : 'var(--text-dim)',
                }}
              >
                {stage.label}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
