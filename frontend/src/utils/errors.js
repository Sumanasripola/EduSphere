// FastAPI sends errors in two different shapes:
//   1. A simple string, e.g. { detail: "Invalid email or password" }
//   2. A validation-error array, e.g.
//      { detail: [{ loc: [...], msg: "value is not a valid email address", type: "..." }] }
// Rendering shape #2 directly as text crashes React (you can't render an
// object as a child), which is what caused the blank white page. This
// helper always returns a plain, safe-to-render string no matter which
// shape comes back.
export function extractErrorMessage(err, fallback = "Something went wrong.") {
  const detail = err?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    // Take the first validation error's message, and clean up field name if present
    const first = detail[0];
    if (first?.msg) {
      const field = Array.isArray(first.loc) ? first.loc[first.loc.length - 1] : null;
      return field ? `${field}: ${first.msg}` : first.msg;
    }
  }

  return fallback;
}
