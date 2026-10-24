const boot = JSON.parse(document.getElementById("boot").textContent);
const promptBox = document.getElementById("prompt");
const form = document.getElementById("composer");
const sendButton = document.getElementById("send");
const examples = document.getElementById("examples");
const result = document.getElementById("result");
const answers = document.getElementById("answers");
const notice = document.getElementById("notice");
const report = document.getElementById("report");
const reportBody = document.getElementById("report-body");

let pair = boot.pair;
let exampleText = "";
let exampleTitle = "";
let busy = false;

function renderTabs() {
  const bar = document.getElementById("tabs");
  bar.replaceChildren();
  Object.entries(boot.pairs).forEach(function (entry) {
    const name = entry[0];
    const spec = entry[1];
    const button = document.createElement("button");
    button.type = "button";
    button.className = "pair-tab" + (name === pair ? " is-active" : "");
    button.textContent = spec.label;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", name === pair ? "true" : "false");
    if (boot.wired) {
      button.addEventListener("click", function () {
        selectPair(name);
      });
    }
    bar.appendChild(button);
  });
}

function fitPrompt() {
  promptBox.style.height = "56px";
  promptBox.style.height = Math.min(promptBox.scrollHeight, 160) + "px";
}

function selectPair(name) {
  pair = name;
  exampleText = "";
  exampleTitle = "";
  promptBox.value = "";
  fitPrompt();
  renderTabs();
  renderExamples();
  clearResult();
}

function renderExamples() {
  examples.replaceChildren();
  const spec = boot.pairs[pair];
  if (!spec) {
    return;
  }
  spec.examples.forEach(function (example) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chip";
    button.textContent = example.label;
    button.addEventListener("click", function () {
      if (busy) {
        return;
      }
      promptBox.value = example.text;
      exampleText = example.text;
      exampleTitle = example.title || "";
      fitPrompt();
    });
    examples.appendChild(button);
  });
}

function fillReport() {
  reportBody.replaceChildren();
  const rows = (boot.metrics && boot.metrics[pair]) || [];
  rows.forEach(function (row) {
    const tr = document.createElement("tr");
    ["name", "base", "compressed"].forEach(function (key) {
      const cell = document.createElement("td");
      cell.textContent = row[key];
      tr.appendChild(cell);
    });
    reportBody.appendChild(tr);
  });
  report.hidden = rows.length === 0;
}

function clearResult() {
  result.hidden = true;
  answers.hidden = true;
  notice.hidden = true;
  report.hidden = true;
  notice.textContent = "";
  document.querySelectorAll(".answer-text").forEach(function (node) {
    node.textContent = "";
  });
}

function showThinking() {
  result.hidden = false;
  answers.hidden = false;
  notice.hidden = true;
  notice.textContent = "";
  report.hidden = true;
  document.querySelectorAll(".answer-text").forEach(function (node) {
    node.textContent = "";
  });
  document.querySelectorAll(".thinking").forEach(function (node) {
    node.hidden = false;
  });
  document.querySelectorAll(".answer-label, .answer-text").forEach(function (node) {
    node.hidden = true;
  });
}

function setBusy(value) {
  busy = value;
  promptBox.disabled = value;
  sendButton.disabled = value;
  document.querySelectorAll(".chip, .pair-tab").forEach(function (node) {
    node.disabled = value;
  });
}

function showAnswers(base, compressed) {
  result.hidden = false;
  answers.hidden = false;
  notice.hidden = true;
  document.querySelectorAll(".thinking").forEach(function (node) {
    node.hidden = true;
  });
  document.querySelectorAll(".answer-label, .answer-text").forEach(function (node) {
    node.hidden = false;
  });
  document.querySelector("#base-answer .answer-text").textContent = base || "—";
  document.querySelector("#compressed-answer .answer-text").textContent = compressed || "—";
  fillReport();
}

function showNotice(message, withReport) {
  result.hidden = false;
  answers.hidden = true;
  document.querySelectorAll(".thinking").forEach(function (node) {
    node.hidden = true;
  });
  notice.hidden = false;
  notice.textContent = message;
  if (withReport) {
    fillReport();
  } else {
    report.hidden = true;
  }
}

promptBox.addEventListener("input", function () {
  if (promptBox.value !== exampleText) {
    exampleTitle = "";
  }
  fitPrompt();
});

form.addEventListener("submit", function (event) {
  event.preventDefault();
  const text = promptBox.value.trim();
  if (!boot.wired) {
    showNotice("This page is not connected yet.", false);
    return;
  }
  if (!text || busy) {
    if (!text) {
      showNotice("Enter a prompt first.", false);
    }
    return;
  }
  setBusy(true);
  showThinking();
  const title = promptBox.value === exampleText ? exampleTitle : "";
  fetch("/api/infer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pair: pair, text: text, title: title }),
  })
    .then(function (response) {
      return response.json().then(function (payload) {
        return { ok: response.ok, payload: payload };
      });
    })
    .then(function (result) {
      const payload = result.payload || {};
      if (!result.ok || payload.error) {
        showNotice(payload.error || "The model could not answer.", true);
        return;
      }
      showAnswers(payload.base, payload.compressed);
    })
    .catch(function () {
      showNotice("The model could not answer.", true);
    })
    .finally(function () {
      setBusy(false);
    });
});

promptBox.addEventListener("keydown", function (event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

renderTabs();
renderExamples();
