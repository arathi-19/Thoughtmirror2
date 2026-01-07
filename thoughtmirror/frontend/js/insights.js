const user_id = localStorage.getItem("user_id");

if (!user_id) {
  alert("Please login again");
  window.location.href = "login.html";
}

async function loadInsights() {
  const response = await fetch(
    `http://127.0.0.1:8000/insights/${user_id}`
  );

  const data = await response.json();

  // Summary
  document.getElementById("summaryText").innerText = data.summary;

  // Keywords
  const keywordsList = document.getElementById("keywords");
  keywordsList.innerHTML = "";

  data.keywords.forEach(word => {
    const li = document.createElement("li");
    li.innerText = word;
    keywordsList.appendChild(li);
  });

  // Simple sentiment chart
  const chart = document.getElementById("sentimentChart");
  chart.innerHTML = "";

  const bar = document.createElement("div");
  bar.className = "bar";

  if (data.score > 0.1) bar.classList.add("high");
  else if (data.score < -0.1) bar.classList.add("low");
  else bar.classList.add("medium");

  bar.style.height = `${Math.abs(data.score) * 150 + 30}px`;
  chart.appendChild(bar);
}

loadInsights();
