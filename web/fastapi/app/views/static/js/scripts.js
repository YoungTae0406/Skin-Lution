// test
async function sendMessage(userInput) {
    const response = await fetch('/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: 1, user_input: userInput }),
    });
    const data = await response.json();
    return data.bot_response;
}

document.getElementById("sendButton").addEventListener("click", async () => {
    const userInput = document.getElementById("userInput").value;
    const botResponse = await sendMessage(userInput);
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += `<div><strong>You:</strong> ${userInput}</div>`;
    chatBox.innerHTML += `<div><strong>Bot:</strong> ${botResponse}</div>`;
    document.getElementById("userInput").value = '';
});
