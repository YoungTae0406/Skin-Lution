// script.js
document.getElementById('sendButton').addEventListener('click', handleSend);
document.getElementById('input').addEventListener('keypress', function (e) {
    
  if (e.key === 'Enter') {
    handleSend();
  }
});

async function handleSend() {
  const input = document.getElementById('input');
  const messageText = input.value.trim();
  if (messageText) {
    addMessage(messageText, 'user');
    input.value = '';
    
    // ChatGPT API 호출
    try {
      const response = await fetch('http://127.0.0.1:5000/run-python', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: messageText })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        addMessage(result.output, 'bot');
      } else {
        addMessage(`Error: ${result.error}\nOutput: ${result.output}`, 'bot');
      }
    } catch (error) {
      addMessage(`Error: ${error}`, 'bot');
    }
  }
}

function addMessage(text, sender) {
  const messagesContainer = document.getElementById('messages');
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', sender);
  messageElement.textContent = text;
  messagesContainer.appendChild(messageElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight; // 스크롤을 맨 아래로
}


function changeSendIcon() {
    var input = document.getElementById('input');
    var sendIcon = document.getElementById('sendIcon');

    if (input.value.trim() === "") {
        sendIcon.src = "./gray_send_icon.png"; // 입력이 없을 때 회색 이미지로 변경
    } else {
        sendIcon.src = "./black_send_icon.png"; // 입력이 있을 때 파란색 이미지로 변경
    }
}

document.getElementById('input').addEventListener('input', changeSendIcon);



script.js
script.js
script.js
script.js
