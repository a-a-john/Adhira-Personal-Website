async function sendMessage() {
  const input = document.getElementById("chat-input");
  const chatBox = document.getElementById("chat-box");
  const userMessage = input.value;
  if (!userMessage) return;

  chatBox.innerHTML += `<p><b>You:</b> ${userMessage}</p>`;
  input.value = "";

  try {
    const res = await fetch("http://127.0.0.1:5000/api/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message: userMessage })
  });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    chatBox.innerHTML += `<p><b>Bot:</b> ${data.reply}</p>`;
  } catch (err) {
    console.error("Fetch error:", err);
    chatBox.innerHTML += `<p style="color:red;">Error: ${err.message}</p>`;
  }
}
