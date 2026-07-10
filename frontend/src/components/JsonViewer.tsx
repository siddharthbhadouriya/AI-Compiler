interface JsonViewerProps {
  data: unknown
  emptyLabel?: string
}

// Minimal hand-rolled JSON syntax highlighter — line-numbered, compiler-log styled.
// Avoids pulling in react-syntax-highlighter for a payload this size.
function highlight(json: string): string {
  return json
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(\.\d+)?([eE][+-]?\d+)?)/g,
      (match) => {
        let cls = 'text-[#5eead4]' // number
        if (/^"/.test(match)) {
          cls = /:$/.test(match) ? 'text-[#7ea8ff]' : 'text-[#f5c26b]' // key vs string
        } else if (/true|false/.test(match)) {
          cls = 'text-[#fb6f6f]'
        } else if (/null/.test(match)) {
          cls = 'text-[#7a828e]'
        }
        return `<span class="${cls}">${match}</span>`
      }
    )
}

export default function JsonViewer({ data, emptyLabel = 'no output yet' }: JsonViewerProps) {
  if (data === undefined || data === null || (typeof data === 'object' && Object.keys(data as object).length === 0)) {
    return (
      <div className="flex items-center gap-2 px-4 py-6 text-[13px]" style={{ color: 'var(--text-faint)' }}>
        <span>·</span>
        <span>{emptyLabel}</span>
      </div>
    )
  }

  const json = JSON.stringify(data, null, 2)
  const lines = json.split('\n')

  return (
    <div className="overflow-auto text-[12.5px] leading-[1.6]">
      <table className="w-full border-collapse">
        <tbody>
          {lines.map((line, i) => (
            <tr key={i} className="hover:bg-white/[0.02]">
              <td
                className="select-none pr-3 pl-4 text-right align-top"
                style={{ color: 'var(--text-faint)', width: '1%', whiteSpace: 'nowrap' }}
              >
                {i + 1}
              </td>
              <td
                className="whitespace-pre pr-4"
                style={{ color: 'var(--text-primary)' }}
                dangerouslySetInnerHTML={{ __html: highlight(line) || ' ' }}
              />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
