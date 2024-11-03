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

// 이미지 파일을 업로드하고 analyze_skin API를 호출하여 응답을 메시지로 추가
async function handleSkinAnalysis() {
  const fileInput = document.getElementById("fileInput");

  if (fileInput.files.length === 0) {
    alert("이미지 파일을 선택해주세요.");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  // 파일을 미리보기 이미지로 message에 추가
  const reader = new FileReader();
  reader.onload = function(e) {
    addMessage(`<img src="${e.target.result}" alt="Uploaded Image" style="max-width: 200px; border-radius: 10px;" />`, "user");
  };
  reader.readAsDataURL(file);

  try {
    // API 호출
    const response = await fetch("/api/analyze-skin", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      // API 응답 메시지를 화면에 추가
      addMessage(result.best_matching_description, "bot");
    } else {
      const errorResult = await response.json();
      addMessage(`Error: ${errorResult.detail}`, "bot");
    }
  } catch (error) {
    addMessage(`Error: ${error.message}`, "bot");
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

// document.getElementById('skinTypeTest').addEventListener('change', function(event) {
//   const file = event.target.files[0];
//   if (file) {
//     const reader = new FileReader();
//     reader.onload = function(e) {
//       const preview = document.getElementById('preview');
//       preview.src = e.target.result; // 선택한 이미지의 데이터 URL을 미리보기 이미지에 설정
//       preview.style.display = 'block'; // 미리보기 이미지를 표시
//     };
//     reader.readAsDataURL(file); // 파일을 읽어 데이터 URL로 변환
//   }
// });

document.addEventListener("DOMContentLoaded", () => {
  const loginLink = document.querySelector(".login-link");
  const signupLink = document.querySelector(".signup-link");
  const profileMenu = document.querySelector(".profile-menu");

  // 로그인 후 UI 변경
  function showProfile() {
    loginLink.style.display = "none";
    signupLink.style.display = "none";
    profileMenu.style.display = "flex";
  }

  // 로그인 상태 확인 및 UI 업데이트
  if (sessionStorage.getItem("isLoggedIn") === "true") {
    showProfile();
  }

  // 로그아웃 버튼 클릭 시
  document.getElementById("logout").addEventListener("click", () => {
    sessionStorage.removeItem("isLoggedIn");
    loginLink.style.display = "inline";
    signupLink.style.display = "inline";
    profileMenu.style.display = "none";
    dropdownMenu.style.display = "none";
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const profileIcon = document.querySelector(".profile-icon");
  const dropdownMenu = document.querySelector(".dropdown-menu");

  // 프로필 아이콘 클릭 시 드롭다운 토글
  profileIcon.addEventListener("click", () => {
    dropdownMenu.style.display =
      dropdownMenu.style.display === "none" ? "block" : "none";
  });

});

// 햄버거 바 클릭 시 메뉴 토글
document.getElementById("hamburgerMenu").addEventListener("click", function() {
  const menu = document.querySelector(".hamburger-menu");
  menu.style.display = menu.style.display === "none" ? "block" : "none";
});

// 피부타입테스트 클릭 시 파일 업로드 트리거
document.getElementById("skinTypeTest").addEventListener("click", function() {
  document.getElementById("fileInput").click(); // 파일 선택 대화상자 열기
});

// 파일이 선택되었을 때 handleSkinAnalysis 함수 실행
document.getElementById("fileInput").addEventListener("change", handleSkinAnalysis);

