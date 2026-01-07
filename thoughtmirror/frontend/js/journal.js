const editor = document.getElementById("editor");
const charCount = document.getElementById("charCount");
const saveBtn = document.getElementById("saveBtn");

// character counter
editor.addEventListener("input", () => {
  charCount.innerText = editor.innerText.length + " characters";
});

// save journal
saveBtn.addEventListener("click", async () => {
  const content = editor.innerHTML;
  const user_id = localStorage.getItem("user_id");

  if (!user_id) {
    alert("Please login again");
    window.location.href = "login.html";
    return;
  }

  if (content.trim() === "") {
    alert("Journal cannot be empty");
    return;
  }

  const response = await fetch("http://127.0.0.1:8000/journal", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      user_id: parseInt(user_id),
      content: content
    })
  });

  const data = await response.json();

  alert("Journal saved successfully ✨");
  editor.innerHTML = "";
  charCount.innerText = "0 characters";
});
