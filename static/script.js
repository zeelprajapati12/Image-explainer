document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const chatBox = document.getElementById("chatBox");
  const fileInput = document.getElementById("imageUpload");
  const promptInput = this.querySelector('input[name="prompt"]');
  const file = fileInput.files[0];
  const prompt = promptInput.value.trim();

  // ❌ If no image, show error on left
  if (!file || !file.type.startsWith("image/")) {
    const errorMsg = document.createElement("div");
    errorMsg.className = "message ai-message";
    errorMsg.textContent = "Please enter an image file.";
    chatBox.appendChild(errorMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return;
  }

  // ✅ Show user image + prompt on right side
  const imageURL = URL.createObjectURL(file);
  const userMessageDiv = document.createElement("div");
  userMessageDiv.className = "message user-image";
  userMessageDiv.innerHTML = `
    <img src="${imageURL}" alt="Uploaded Image" />
    ${prompt ? `<p class="user-prompt">${prompt}</p>` : ""}
  `;
  chatBox.appendChild(userMessageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  // ✅ Send image + prompt to backend
  const formData = new FormData();
  formData.append("image", file);
  formData.append("prompt", prompt);

  const res = await fetch("/explain", {
    method: "POST",
    body: formData,
  });

  const data = await res.json();

  const aiMessage = document.createElement("div");
  aiMessage.className = "message ai-message";
  aiMessage.textContent = data.result || data.error || "No response";
  chatBox.appendChild(aiMessage);
  chatBox.scrollTop = chatBox.scrollHeight;

  // ✅ Clear inputs
  promptInput.value = "";
  fileInput.value = "";
});
