/**
 * EduGenie Frontend Controller
 * Handles async form dispatches, interactive quiz checking, formatting, and live status.
 */

document.addEventListener("DOMContentLoaded", () => {
  initHealthCheck();
  initQuickChips();
  initForms();
  initNavFilters();
});

// 1. Health check to display live status
async function initHealthCheck() {
  try {
    const res = await fetch("/health");
    if (res.ok) {
      const data = await res.json();
      const statusText = document.getElementById("statusText");
      if (statusText) {
        if (data.gemini_configured) {
          statusText.textContent = "AI Ready • Gemini & Local Connected";
        } else {
          statusText.textContent = "Needs API Key • Add to .env";
          statusText.parentElement.style.color = "#f59e0b";
        }
      }
    }
  } catch (err) {
    console.warn("Health check unreachable:", err);
  }
}

// 2. Navigation quick jump / filters
function initNavFilters() {
  const navBtns = document.querySelectorAll(".nav-pill-btn");
  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      navBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-target");
      if (targetId === "all") {
        document.querySelectorAll(".feature-card").forEach((c) => (c.style.display = "block"));
      } else {
        document.querySelectorAll(".feature-card").forEach((c) => {
          c.style.display = c.id === targetId ? "block" : "none";
        });
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });
}

// 3. Quick-fill example prompt chips
function initQuickChips() {
  const chips = document.querySelectorAll(".chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const targetInputId = chip.getAttribute("data-input");
      const sampleText = chip.getAttribute("data-text");
      const input = document.getElementById(targetInputId);
      if (input) {
        input.value = sampleText;
        input.focus();
      }
    });
  });
}

// 4. Form Submissions
function initForms() {
  // Q&A Form
  const qaForm = document.getElementById("qaForm");
  if (qaForm) {
    qaForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("question");
      const val = input.value.trim();
      if (!val) return;

      const btn = qaForm.querySelector('button[type="submit"]');
      const resultBox = document.getElementById("qaResult");
      setLoading(btn, true);

      try {
        const res = await fetch(`/qa?question=${encodeURIComponent(val)}`);
        const data = await res.json();
        const content = data.answer || data.error || "No response received.";
        renderOutput(resultBox, content, "Answer");
      } catch (err) {
        renderOutput(resultBox, `⚠️ Network error: ${err.message}`, "Error");
      } finally {
        setLoading(btn, false);
      }
    });
  }

  // Explanation Form
  const explainForm = document.getElementById("explainForm");
  if (explainForm) {
    explainForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("topic");
      const val = input.value.trim();
      if (!val) return;

      const btn = explainForm.querySelector('button[type="submit"]');
      const resultBox = document.getElementById("explanationResult");
      setLoading(btn, true);

      try {
        const res = await fetch("/explain/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic: val }),
        });
        const data = await res.json();
        const content = data.explanation || data.error || "No explanation received.";
        renderOutput(resultBox, content, `Explanation for "${data.topic || val}"`);
      } catch (err) {
        renderOutput(resultBox, `⚠️ Network error: ${err.message}`, "Error");
      } finally {
        setLoading(btn, false);
      }
    });
  }

  // Summary Form
  const summaryForm = document.getElementById("summaryForm");
  if (summaryForm) {
    summaryForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("summaryText");
      const val = input.value.trim();
      if (!val) return;

      const btn = summaryForm.querySelector('button[type="submit"]');
      const resultBox = document.getElementById("summaryResult");
      setLoading(btn, true);

      try {
        const res = await fetch("/summarize/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: val }),
        });
        const data = await res.json();
        const content = data.summary || data.error || "No summary generated.";
        renderOutput(resultBox, content, "Summary");
      } catch (err) {
        renderOutput(resultBox, `⚠️ Network error: ${err.message}`, "Error");
      } finally {
        setLoading(btn, false);
      }
    });
  }

  // Quiz Form
  const quizForm = document.getElementById("quizForm");
  if (quizForm) {
    quizForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("quizText");
      const val = input.value.trim();
      if (!val) return;

      const btn = quizForm.querySelector('button[type="submit"]');
      const resultBox = document.getElementById("quizResult");
      setLoading(btn, true);

      try {
        const res = await fetch("/quiz", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: val }),
        });
        const data = await res.json();
        if (data.quiz && Array.isArray(data.quiz)) {
          renderInteractiveQuiz(resultBox, data.quiz);
        } else {
          renderOutput(resultBox, JSON.stringify(data), "Quiz Response");
        }
      } catch (err) {
        renderOutput(resultBox, `⚠️ Network error: ${err.message}`, "Error");
      } finally {
        setLoading(btn, false);
      }
    });
  }

  // Learning Recommendations Form
  const pathForm = document.getElementById("pathForm");
  if (pathForm) {
    pathForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("pathTopic");
      const val = input.value.trim();
      if (!val) return;

      const btn = pathForm.querySelector('button[type="submit"]');
      const resultBox = document.getElementById("pathResult");
      setLoading(btn, true);

      try {
        const res = await fetch(`/learn/recommendations?topic=${encodeURIComponent(val)}`);
        const data = await res.json();
        const content = data.recommendation || data.error || "No recommendations generated.";
        renderMarkdownOutput(resultBox, content, `Learning Roadmap: ${data.topic || val}`);
      } catch (err) {
        renderOutput(resultBox, `⚠️ Network error: ${err.message}`, "Error");
      } finally {
        setLoading(btn, false);
      }
    });
  }
}

// 5. Output rendering with Markdown support and Copy button
function renderOutput(container, text, title) {
  container.className = "output-container has-content";
  const formattedHtml = formatMarkdown(text);
  container.innerHTML = `
    <div class="output-header">
      <div class="output-title">📄 ${escapeHtml(title)}</div>
      <button class="btn-copy" onclick="copyRawContent(this)" data-raw="${encodeURIComponent(text)}">📋 Copy</button>
    </div>
    <div class="output-content formatted-markdown">${formattedHtml}</div>
  `;
}

// 6. Markdown-styled Output rendering
function renderMarkdownOutput(container, markdownText, title) {
  container.className = "output-container has-content";
  const formattedHtml = formatMarkdown(markdownText);
  container.innerHTML = `
    <div class="output-header">
      <div class="output-title">🗺️ ${escapeHtml(title)}</div>
      <button class="btn-copy" onclick="copyRawContent(this)" data-raw="${encodeURIComponent(markdownText)}">📋 Copy Roadmap</button>
    </div>
    <div class="output-content formatted-markdown">${formattedHtml}</div>
  `;
}

// 7. Interactive Quiz Engine
function renderInteractiveQuiz(container, questions) {
  container.className = "output-container has-content";

  // Check if error item returned
  if (questions.length === 1 && questions[0].error) {
    container.innerHTML = `
      <div class="output-header">
        <div class="output-title">⚠️ Quiz Generation Notice</div>
      </div>
      <div class="output-content" style="color: #b91c1c;">${escapeHtml(questions[0].error)}</div>
    `;
    return;
  }

  let html = `
    <div class="output-header">
      <div class="output-title">🎯 Interactive Quiz (${questions.length} Questions)</div>
    </div>
    <div class="quiz-wrapper">
  `;

  questions.forEach((q, qIdx) => {
    const qNum = qIdx + 1;
    const safeAns = escapeHtml(q.answer || "");
    html += `
      <div class="quiz-card" id="quiz-card-${qIdx}">
        <div class="quiz-question-header">Q${qNum}: ${escapeHtml(q.question)}</div>
        <div class="quiz-options-list">
    `;

    (q.options || []).forEach((opt, optIdx) => {
      const optId = `q${qIdx}_opt${optIdx}`;
      const safeOpt = escapeHtml(opt);
      html += `
        <label class="quiz-option-label" for="${optId}">
          <input type="radio" id="${optId}" name="question_${qIdx}" value="${safeOpt}">
          <span>${safeOpt}</span>
        </label>
      `;
    });

    html += `
        </div>
        <div class="quiz-action-bar">
          <button type="button" class="btn-check-answer" onclick="checkAnswer(${qIdx}, '${encodeURIComponent(q.answer || "")}')">Check Answer</button>
          <span class="quiz-feedback" id="feedback-${qIdx}"></span>
        </div>
      </div>
    `;
  });

  html += `
      <div class="quiz-score-summary" id="quizScoreSummary" style="display: none;"></div>
    </div>
  `;

  container.innerHTML = html;
}

// 8. Answer checker logic
window.quizStats = { total: 0, checked: {}, correctCount: 0 };

window.checkAnswer = function (qIdx, encodedAnswer) {
  const correctAnswer = decodeURIComponent(encodedAnswer).trim();
  const selectedRadio = document.querySelector(`input[name="question_${qIdx}"]:checked`);
  const feedbackEl = document.getElementById(`feedback-${qIdx}`);
  const cardEl = document.getElementById(`quiz-card-${qIdx}`);

  if (!selectedRadio) {
    feedbackEl.className = "quiz-feedback incorrect";
    feedbackEl.innerHTML = "⚠️ Please select an option first!";
    return;
  }

  const userAnswer = selectedRadio.value.trim();
  const isCorrect = userAnswer.toLowerCase() === correctAnswer.toLowerCase();

  cardEl.classList.remove("answered-correct", "answered-incorrect");

  if (isCorrect) {
    cardEl.classList.add("answered-correct");
    feedbackEl.className = "quiz-feedback correct";
    feedbackEl.innerHTML = "✅ Correct!";
    window.quizStats.checked[qIdx] = 1;
  } else {
    cardEl.classList.add("answered-incorrect");
    feedbackEl.className = "quiz-feedback incorrect";
    feedbackEl.innerHTML = `❌ Incorrect. Correct answer: <strong>${escapeHtml(correctAnswer)}</strong>`;
    window.quizStats.checked[qIdx] = 0;
  }

  // Update total tally if all questions checked
  const allCards = document.querySelectorAll(".quiz-card");
  const answeredKeys = Object.keys(window.quizStats.checked);
  if (answeredKeys.length === allCards.length) {
    const totalCorrect = Object.values(window.quizStats.checked).reduce((a, b) => a + b, 0);
    const scoreSummary = document.getElementById("quizScoreSummary");
    if (scoreSummary) {
      scoreSummary.style.display = "block";
      const pct = Math.round((totalCorrect / allCards.length) * 100);
      scoreSummary.innerHTML = `🏆 Quiz Completed! Your Score: <strong>${totalCorrect} / ${allCards.length}</strong> (${pct}%)`;
    }
  }
};

// 9. Helper Utilities
function setLoading(btn, isLoading) {
  if (isLoading) {
    btn.disabled = true;
    btn.dataset.originalText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Processing...`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.originalText || "Submit";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkdown(text) {
  if (!text) return "";

  // Clean up LaTeX formatting like $$\text{username@domain.com}$$ into code/box
  let cleaned = text.replace(/\$\$\\text\{([^}]+)\}\$\$/g, '`$1`');
  cleaned = cleaned.replace(/\$\$([^$]+)\$\$/g, '`$1`');

  if (typeof marked !== "undefined" && typeof marked.parse === "function") {
    try {
      return marked.parse(cleaned);
    } catch (err) {
      console.warn("marked.parse error, falling back:", err);
    }
  }
  return parseSimpleMarkdown(cleaned);
}

function parseSimpleMarkdown(md) {
  if (!md) return "";
  let html = escapeHtml(md);

  // Bold **text**
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Headers ## and ###
  html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
  html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
  html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");

  // Bullet points * or -
  html = html.replace(/^\s*[\*\-]\s+(.*$)/gim, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>)/gims, "<ul>$1</ul>");

  // Line breaks
  html = html.replace(/\n\n+/g, "<br><br>");
  return html;
}

window.copyContent = function (btn) {
  const container = btn.closest(".output-container");
  const contentEl = container.querySelector(".output-content");
  if (contentEl) {
    navigator.clipboard.writeText(contentEl.innerText).then(() => {
      showToast("Copied to clipboard!");
    });
  }
};

window.copyRawContent = function (btn) {
  const raw = btn.getAttribute("data-raw");
  if (raw) {
    navigator.clipboard.writeText(decodeURIComponent(raw)).then(() => {
      showToast("Roadmap copied to clipboard!");
    });
  }
};

function showToast(msg) {
  let toast = document.getElementById("toastNotice");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toastNotice";
    toast.className = "toast-notice";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 2500);
}
