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
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_message: messageText }),
      });

      const result = await response.json();

      if (response.ok) {
        // 하나의 메시지로 결합하여 출력
        const fullMessage = `
          ${result.ai_message}

          문서 제목: ${result.document_title}
          문서 메타데이터: ${result.document_metadata}
        `;
        addMessage(fullMessage, "bot");
      } else {
        addMessage(`Error: ${result.error}\nOutput: ${result.detail}`, "bot");
      }
    } catch (error) {
      addMessage("error!", "bot");
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

document.getElementById('uploadButton').addEventListener('click', function() {
  document.getElementById('fileInput').click();
});

document.getElementById('fileInput').addEventListener('change', function(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      const preview = document.getElementById('preview');
      preview.src = e.target.result; // 선택한 이미지의 데이터 URL을 미리보기 이미지에 설정
      preview.style.display = 'block'; // 미리보기 이미지를 표시
    };
    reader.readAsDataURL(file); // 파일을 읽어 데이터 URL로 변환
  }
});