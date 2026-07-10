import { useState, type KeyboardEvent } from 'react'

interface PromptInputProps {
  onSubmit: (prompt: string) => void
  isRunning: boolean
}

const EXAMPLES = [
  'Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.',
  'Create a project management tool like Trello with boards, cards, team collaboration, and user authentication.',
  'Build a restaurant booking system with table management, reservations, and SMS confirmations.',
]

export default function PromptInput({ onSubmit, isRunning }: PromptInputProps) {
  const [value, setValue] = useState('')

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || isRunning) return
    onSubmit(trimmed)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="border-b" style={{ borderColor: 'var(--border-line)', background: 'var(--bg-panel)' }}>
      <div className="flex items-start gap-3 px-5 py-4">
        <span
          className="mt-[3px] shrink-0 select-none text-[14px] font-bold"
          style={{ color: 'var(--accent-signal)' }}
        >
          compylr&gt;
        </span>
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isRunning}
          rows={2}
          placeholder="Describe the application you want compiled — e.g. 'Build a CRM with login, contacts, and role-based access.'"
          className="min-h-[28px] w-full resize-none bg-transparent text-[14px] leading-relaxed outline-none placeholder:italic disabled:opacity-50"
          style={{ color: 'var(--text-primary)' }}
        />
        {!isRunning && <span className="mt-[3px] h-[16px] w-[8px] shrink-0 cursor-blink" style={{ background: 'var(--accent-signal)' }} />}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 px-5 pb-3">
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => setValue(ex)}
              disabled={isRunning}
              className="rounded-sm border px-2 py-1 text-[11px] transition-colors disabled:opacity-40"
              style={{
                borderColor: 'var(--border-line)',
                color: 'var(--text-dim)',
                background: 'var(--bg-panel-alt)',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-signal)')}
              onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-dim)')}
            >
              example_{i + 1}.txt
            </button>
          ))}
        </div>
        <button
          onClick={submit}
          disabled={isRunning || !value.trim()}
          className="rounded-sm px-4 py-1.5 text-[12px] font-bold tracking-wide transition-opacity disabled:cursor-not-allowed disabled:opacity-30"
          style={{ background: 'var(--accent-signal)', color: '#08110f' }}
        >
          {isRunning ? 'COMPILING…' : 'RUN COMPILE  ⌘⏎'}
        </button>
      </div>
    </div>
  )
}
