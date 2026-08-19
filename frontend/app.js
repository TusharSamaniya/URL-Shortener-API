/* URL Shortener frontend logic — talks to the FastAPI backend. */

// Change this if your backend runs somewhere else.
const API_BASE_URL = "http://localhost:8000";

const $ = (id) => document.getElementById(id);

const show = (el) => el.classList.remove("hidden");
const hide = (el) => el.classList.add("hidden");

function setError(message) {
  const error = $("error");
  error.textContent = message;
  show(error);
}

// Extract a readable message from an error response, else use the fallback.
async function errorMessage(res, fallback) {
  try {
    const body = await res.json();
    const detail = Array.isArray(body.detail) ? body.detail[0].msg : body.detail;
    if (detail) return `Error: ${detail}`;
  } catch {
    /* response wasn't JSON — use fallback */
  }
  return fallback;
}

async function handleShorten(event) {
  event.preventDefault();
  hide($("error"));
  hide($("shorten-result"));

  try {
    const res = await fetch(`${API_BASE_URL}/shorten`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original_url: $("long-url").value.trim() }),
    });
    if (!res.ok) {
      throw new Error(await errorMessage(res, "Could not shorten that URL."));
    }

    const data = await res.json();
    const link = $("short-link");
    link.textContent = data.short_url;
    link.href = data.short_url;
    show($("shorten-result"));
  } catch (err) {
    setError(`Network or server problem: ${err.message}`);
  }
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText($("short-link").href);
    const btn = $("copy-btn");
    btn.textContent = "Copied!";
    setTimeout(() => (btn.textContent = "Copy"), 1500);
  } catch {
    setError("Could not copy — copy the link manually.");
  }
}

$("shorten-form").addEventListener("submit", handleShorten);
$("copy-btn").addEventListener("click", handleCopy);