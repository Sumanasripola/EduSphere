import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import TableRenderer from "./TableRenderer";

const BASE_URL = "http://127.0.0.1:8000";

// ── Parse answer text into "text" | "table" segments ─────────────────────────
function parseSegments(text) {
  const lines    = (text || "").split("\n");
  const segments = [];
  let i = 0;

  while (i < lines.length) {
    if (lines[i].trim().startsWith("|")) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      const rows  = tableLines.map((l) =>
        l.trim().split("|").slice(1, -1).map((c) => c.trim())
      );
      const isSep = (row) => row.every((c) => /^[-: ]+$/.test(c));
      if (rows.length >= 2 && isSep(rows[1])) {
        segments.push({ type: "table", headers: rows[0], rows: rows.slice(2) });
      } else {
        segments.push({ type: "text", content: tableLines.join("\n") });
      }
    } else {
      const textLines = [];
      while (i < lines.length && !lines[i].trim().startsWith("|")) {
        textLines.push(lines[i]);
        i++;
      }
      const content = textLines.join("\n").trim();
      if (content) segments.push({ type: "text", content });
    }
  }

  return segments;
}

// ── Markdown components ───────────────────────────────────────────────────────
const mdComponents = {
  p:      ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
  ul:     ({ children }) => <ul className="list-disc ml-4 mb-2 space-y-1">{children}</ul>,
  ol:     ({ children }) => <ol className="list-decimal ml-4 mb-2 space-y-1">{children}</ol>,
  li:     ({ children }) => <li className="text-sm">{children}</li>,
  h1:     ({ children }) => <h1 className="text-base font-bold mt-3 mb-1">{children}</h1>,
  h2:     ({ children }) => <h2 className="text-sm font-bold mt-3 mb-1">{children}</h2>,
  h3:     ({ children }) => <h3 className="text-sm font-semibold mt-2 mb-1">{children}</h3>,
  code:   ({ inline, children }) =>
    inline
      ? <code className="bg-gray-100 text-pink-600 px-1 rounded text-xs">{children}</code>
      : <pre className="bg-gray-50 rounded-lg p-3 text-xs overflow-x-auto my-2"><code>{children}</code></pre>,
};

// ── Citations section ─────────────────────────────────────────────────────────
// citations: [ { source: "bert.pdf", pages: [3, 5, 15] }, ... ]
function Citations({ citations }) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-gray-100">
      <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-2">
        Sources
      </p>
      <div className="flex flex-col gap-2">
        {citations.map((c, i) => (
          <div
            key={i}
            className="flex flex-wrap items-center gap-1.5 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2"
          >
            {/* File icon */}
            <svg className="w-3 h-3 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>

            {/* Filename */}
            <span className="text-[11px] font-semibold text-blue-700 max-w-[160px] truncate" title={c.source}>
              {c.source}
            </span>

            {/* Page pills */}
            <div className="flex flex-wrap gap-1 ml-1">
              {c.pages.map((p) => (
                <span
                  key={p}
                  className="text-[10px] bg-blue-200 text-blue-800 font-semibold rounded px-1.5 py-0.5"
                >
                  p.{p}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Single image card with download ──────────────────────────────────────────
function ImageCard({ img }) {
  const src      = `${BASE_URL}/images/${img.image_path}`;
  const filename = (img.image_path || "figure.png").split(/[\\/]/).pop();

  const handleDownload = async () => {
    try {
      const res  = await fetch(src);
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Image download failed:", err);
    }
  };

  return (
    <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm bg-white">
      {/* Image */}
      <img
        src={src}
        alt={img.caption || "Figure"}
        className="w-full object-contain"
        style={{ maxHeight: "480px" }}
        onError={(e) => { e.currentTarget.style.display = "none"; }}
      />

      {/* Footer: caption + source + download */}
      <div className="flex items-center justify-between px-3 py-2 border-t border-gray-100 bg-gray-50 gap-2">
        <p className="text-xs text-gray-400 italic truncate">
          {img.caption || "Figure"}
          {img.page   && <span className="ml-1 font-medium text-gray-500">— page {img.page}</span>}
          {img.source && <span className="ml-1">· {img.source}</span>}
        </p>

        <button
          onClick={handleDownload}
          title="Download image"
          className="flex items-center gap-1 text-[11px] text-blue-600 hover:text-blue-800 font-medium transition flex-shrink-0"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download
        </button>
      </div>
    </div>
  );
}

// ── Excel download button ─────────────────────────────────────────────────────
function ExcelDownload({ path }) {
  if (!path) return null;
  const filename = path.split(/[\\/]/).pop();
  const url      = `${BASE_URL}/generated_excels/${filename}`;

  return (
    <a
      href={url}
      download
      className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-green-500 hover:bg-green-600 text-white text-xs rounded-lg transition shadow"
    >
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Download Excel
    </a>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────
export default function MessageBubble({
  message,
  isUser,
  images    = [],
  excel     = null,
  citations = [],
}) {
  // User bubble — plain text only
  if (isUser) {
    return (
      <div className="flex w-full mb-6 animate-fadeIn justify-end">
        <div className="max-w-[65%] px-5 py-3 text-sm leading-relaxed bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl rounded-br-md shadow-md">
          {message}
        </div>
      </div>
    );
  }

  const segments = parseSegments(message);

  return (
    <div className="flex w-full mb-6 animate-fadeIn justify-start">
      <div className="max-w-[78%] px-5 py-4 text-sm leading-relaxed bg-white border border-gray-200 text-gray-800 rounded-2xl rounded-bl-md shadow-sm">

        {/* Answer text + inline tables */}
        {segments.map((seg, idx) =>
          seg.type === "table" ? (
            <TableRenderer key={idx} headers={seg.headers} rows={seg.rows} />
          ) : (
            <ReactMarkdown key={idx} remarkPlugins={[remarkGfm]} components={mdComponents}>
              {seg.content}
            </ReactMarkdown>
          )
        )}

        {/* Extracted figures */}
        {images.length > 0 && (
          <div className="mt-4 space-y-3">
            <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest">
              Related figures
            </p>
            {images.map((img, i) => (
              <ImageCard key={i} img={img} />
            ))}
          </div>
        )}

        {/* Excel download */}
        <ExcelDownload path={excel} />

        {/* ✅ Citations — always shown when present */}
        <Citations citations={citations} />

      </div>
    </div>
  );
}
