const historyList = document.getElementById("historyList");
const user_id = localStorage.getItem("user_id");

if (!user_id) {
  alert("Please login again");
  window.location.href = "login.html";
}

async function loadHistory() {
  const response = await fetch(
    `http://127.0.0.1:8000/journal/${user_id}`
  );

  const data = await response.json();

  historyList.innerHTML = "";

  if (data.length === 0) {
    historyList.innerHTML = "<p>No journal entries found.</p>";
    return;
  }

  data.forEach(entry => {
    const div = document.createElement("div");
    div.className = "entry";

    div.innerHTML = `
      <div class="entry-date">${entry.created_at}</div>
      <div class="entry-content">${entry.content}</div>
    `;

    historyList.appendChild(div);
  });
}

loadHistory();
