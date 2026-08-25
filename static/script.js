const messagesDiv = document.getElementById("messages");
const input = document.getElementById("query-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender) {
    const row = document.createElement("div");
    row.className = `msg-row ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = `avatar ${sender === "user" ? "human" : "bot"}`;
    avatar.textContent = sender === "user" ? "🙂" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesDiv.appendChild(row);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return row;
}

function showTyping() {
    const row = document.createElement("div");
    row.className = "msg-row agent";
    row.id = "typing-row";

    const avatar = document.createElement("div");
    avatar.className = "avatar bot";
    avatar.textContent = "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble typing-indicator";
    bubble.innerHTML = "<span></span><span></span><span></span>";

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesDiv.appendChild(row);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeTyping() {
    const row = document.getElementById("typing-row");
    if (row) row.remove();
}

async function sendMessage() {
    const query = input.value.trim();
    if (!query) return;

    addMessage(query, "user");
    input.value = "";
    sendBtn.disabled = true;
    showTyping();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        removeTyping();

        if (!response.ok) {
            addMessage("Circuits fried. Try that again?", "agent");
            return;
        }

        const data = await response.json();
        addMessage(data.response, "agent");
    } catch (err) {
        removeTyping();
        addMessage("Couldn't reach the server. Is it awake?", "agent");
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});