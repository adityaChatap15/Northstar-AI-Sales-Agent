const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");
const analyticsBtn = document.getElementById("analytics-btn");
const analyticsModal = document.getElementById("analytics-modal");
const analyticsBody = document.getElementById("analytics-body");
const closeAnalyticsBtn = document.getElementById("close-analytics-btn");

const GREETING = "Hi! I'm the Northstar Homes AI assistant. Ask me anything " +
  "about Northstar One in Sector 79, Gurugram — in English, Hindi, or Hinglish.";

let sessionId = getOrCreateSessionId();

function getOrCreateSessionId() {
  let id = sessionStorage.getItem("northstar_session_id");

  if (!id) {
    id = createId();
    sessionStorage.setItem("northstar_session_id", id);
  }

  return id;
}

function createId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }

  return "sess-" + Date.now() + "-" + Math.random().toString(16).slice(2);
}

function addBubble(text, role) {
  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-" + role;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return bubble;
}

async function sendMessage(text) {
  addBubble(text, "user");

  const pending = addBubble("Typing...", "assistant");
  pending.classList.add("bubble-pending");

  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text })
    });

    if (!res.ok) {
      throw new Error("Request failed with status " + res.status);
    }

    const data = await res.json();

    pending.textContent = data.response;
    pending.classList.remove("bubble-pending");
  } catch (err) {
    pending.remove();
    addBubble("Something went wrong reaching the assistant. Please try again.", "error");
    console.error(err);
  } finally {
    sendBtn.disabled = false;
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const text = messageInput.value.trim();

  if (!text) {
    return;
  }

  messageInput.value = "";
  sendMessage(text);
});

newChatBtn.addEventListener("click", async () => {
  await fetch("/api/session/" + sessionId, { method: "DELETE" });

  sessionStorage.removeItem("northstar_session_id");
  sessionId = getOrCreateSessionId();

  chatWindow.innerHTML = "";
  addBubble(GREETING, "assistant");
});

analyticsBtn.addEventListener("click", async () => {
  analyticsModal.classList.remove("hidden");
  analyticsBody.textContent = "Loading...";

  try {
    const res = await fetch("/api/analytics/" + sessionId);

    if (res.status === 404) {
      analyticsBody.textContent = "No conversation yet for this session. Send a message first.";
      return;
    }

    if (!res.ok) {
      throw new Error("Request failed with status " + res.status);
    }

    const data = await res.json();
    analyticsBody.textContent = JSON.stringify(data.analytics, null, 2);
  } catch (err) {
    analyticsBody.textContent = "Could not load analytics. Please try again.";
    console.error(err);
  }
});

closeAnalyticsBtn.addEventListener("click", () => {
  analyticsModal.classList.add("hidden");
});
