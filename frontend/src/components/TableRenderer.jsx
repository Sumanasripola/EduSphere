export default function TableRenderer({ headers, rows }) {
  return (
    <div className="mt-4 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

      {/* HEADER */}
      <div className="grid bg-gray-50 border-b border-gray-200 px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide"
           style={{ gridTemplateColumns: `repeat(${headers.length}, minmax(0, 1fr))` }}>
        {headers.map((h, i) => (
          <div key={i}>{h}</div>
        ))}
      </div>

      {/* ROWS */}
      {rows.map((row, idx) => (
        <div
          key={idx}
          className="grid px-4 py-3 text-sm text-gray-700 border-b last:border-none hover:bg-gray-50 transition"
          style={{ gridTemplateColumns: `repeat(${headers.length}, minmax(0, 1fr))` }}
        >
          {row.map((cell, i) => (
            <div key={i} className="truncate">
              {cell}
            </div>
          ))}
        </div>
      ))}

    </div>
  );
}