document.getElementById("sendButton").addEventListener("click", handleSend);
document.getElementById("input").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    handleSend();
  }
});

async function handleSend() {
  const input = document.getElementById("input");
  const messageText = input.value.trim();
  if (messageText) {
    addMessage(messageText, "user");
    input.value = "";

    // ChatGPT API 호출
    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_input: messageText }),
      });

      const result = await response.json();

      if (response.ok) {
        addMessage(result.bot_response, "bot");
      } else {
        addMessage(`Error: ${result.error}\nOutput: ${result.output}`, "bot");
      }
    } catch (error) {
      addMessage(`error!
      `, "bot");
    }
  }
}

function addMessage(text, sender) {
  const messagesContainer = document.getElementById("messages");
  const messageElement = document.createElement("div");
  messageElement.className = `message ${sender}`;
  messageElement.innerHTML = text.replace(/\n/g, '<br>'); // 개행 문자를 <br> 태그로 변환
  messagesContainer.appendChild(messageElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
  const inputField = document.getElementById("input");
  const sendIcon = document.getElementById("sendIcon");
  
  inputField.addEventListener("input", function () {
    if (inputField.value.trim() !== "") {
      sendIcon.src = "/static/image/black_send_icon.png";
    } else {
      sendIcon.src = "/static/image/gray_send_icon.png";
    }
  });

  inputField.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendIcon.src = "/static/image/gray_send_icon.png";
    }
  });
});
