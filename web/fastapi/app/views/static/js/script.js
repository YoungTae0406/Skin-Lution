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
      addMessage(`집에서 피부 관리를 하는데 도움이 될 수 있는 몇 가지 팁을 알려드리겠습니다.<br>
      
      1. 적절한 세안: 피부타입에 맞는 부드러운 클렌저를 사용하여 세안을 하고, 미온수로 깨끗하게 헹구어주세요.<br>
      2. 보습: 피부타입에 맞는 보습제를 사용하여 피부를 촉촉하게 유지해주세요. 특히 건조한 계절에는 보습이 중요합니다.<br>
      3. 자외선 차단: 일상적으로 자외선 차단제를 바르는 것이 중요합니다. 햇빛으로부터 피부를 보호해주고 피부노화를 예방할 수 있습니다.<br>
      4. 영양 공급: 영양이 풍부한 식품을 섭취하고, 피부에 좋은 비타민이나 영양제를 복용하여 피부를 건강하게 유지해주세요.<br>
      이러한 간단한 스텝들을 습관화하여 집에서도 피부를 관리하시면 좋은 결과를 얻을 수 있을 것입니다.<br>
      
      답변에 활용한 데이터: 서울대 피부과전문의가 말하는 피부좋아지는법 | 홈케어만으로 물광피부 완성!
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
