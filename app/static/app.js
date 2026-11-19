// DROSAT RAG Client Application
document.addEventListener("DOMContentLoaded", () => {
  // State
  let activeSector = "all";
  let sessionId = localStorage.getItem("drosat_rag_session_id") || generateSessionId();
  localStorage.setItem("drosat_rag_session_id", sessionId);

  // DOM Elements
  const sessionDisplay = document.getElementById("sessionDisplay");
  const messagesContainer = document.getElementById("messagesContainer");
  const chatForm = document.getElementById("chatForm");
  const queryInput = document.getElementById("queryInput");
  const sendBtn = document.getElementById("sendBtn");
  const newSessionBtn = document.getElementById("newSessionBtn");
  const sectorPills = document.querySelectorAll("#sectorPills .pill");

  const uploadForm = document.getElementById("uploadForm");
  const pdfFileInput = document.getElementById("pdfFileInput");
  const uploadSector = document.getElementById("uploadSector");
  const uploadBtn = document.getElementById("uploadBtn");
  const fileLabel = document.getElementById("fileLabel");
  const dropzone = document.getElementById("dropzone");
  const uploadFeedback = document.getElementById("uploadFeedback");

  // Initialize Session Display
  updateSessionDisplay();

  // -------------------------------------------------------------
  // 1. Sector Filter Selection
  // -------------------------------------------------------------
  sectorPills.forEach(pill => {
    pill.addEventListener("click", () => {
      sectorPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeSector = pill.getAttribute("data-sector");
    });
  });

  // -------------------------------------------------------------
  // 2. Chat Interaction
  // -------------------------------------------------------------
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // Append User Message
    appendMessage("user", query);
    queryInput.value = "";
    sendBtn.disabled = true;

    // Show Typing Indicator
    const typingId = showTypingIndicator();

    try {
      const response = await fetch("/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          sector: activeSector,
          session_id: sessionId
        })
      });

      removeTypingIndicator(typingId);

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      appendMessage("assistant", data.answer, data.sources);
    } catch (err) {
      removeTypingIndicator(typingId);
      appendMessage(
        "assistant",
        "عذراً، حدث خطأ أثناء الاتصال بالخادم. يرجى التأكد من تشغيل السيرفر والمحاولة مرة أخرى."
      );
      console.error("Chat error:", err);
    } finally {
      sendBtn.disabled = false;
      queryInput.focus();
    }
  });

  // Quick Prompt Chips Delegation
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("prompt-chip")) {
      const prompt = e.target.getAttribute("data-prompt");
      const sector = e.target.getAttribute("data-sector");
      
      // Sync sector pill
      if (sector) {
        activeSector = sector;
        sectorPills.forEach(p => {
          if (p.getAttribute("data-sector") === sector) p.classList.add("active");
          else p.classList.remove("active");
        });
      }

      queryInput.value = prompt;
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // New Session
  newSessionBtn.addEventListener("click", () => {
    sessionId = generateSessionId();
    localStorage.setItem("drosat_rag_session_id", sessionId);
    updateSessionDisplay();
    
    // Clear messages and re-insert welcome
    messagesContainer.innerHTML = `
      <div class="message-wrapper assistant">
        <div class="avatar">🤖</div>
        <div class="message-bubble">
          <div class="message-text">
            تم بدء جلسة محادثة جديدة بنجاح! 🔄<br>
            اسألني أي سؤال عن كورسات دروسات، المناهج، المدرسين، السناتر، أو سياسات كاشير وفوري.
          </div>
        </div>
      </div>
    `;
  });

  // -------------------------------------------------------------
  // 3. Document Ingestion (Upload PDF)
  // -------------------------------------------------------------
  pdfFileInput.addEventListener("change", () => {
    if (pdfFileInput.files && pdfFileInput.files[0]) {
      const file = pdfFileInput.files[0];
      if (file.name.toLowerCase().endsWith(".pdf")) {
        fileLabel.textContent = `الملف المختار: ${file.name}`;
        uploadBtn.disabled = false;
      } else {
        fileLabel.textContent = "خطأ: يرجى اختيار ملف PDF فقط";
        uploadBtn.disabled = true;
      }
    }
  });

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!pdfFileInput.files || !pdfFileInput.files[0]) return;

    const file = pdfFileInput.files[0];
    const sector = uploadSector.value;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("sector", sector);

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = "<span>جاري الرفع والفهرسة في Qdrant... ⏳</span>";
    uploadFeedback.classList.add("hidden");

    try {
      const res = await fetch("/api/upload-pdf/", {
        method: "POST",
        body: formData
      });

      const result = await res.json();

      if (res.ok) {
        showFeedback(
          "success",
          `✅ نجح الرفع: تم استخراج ${result.chunks_extracted} مقطع وفهرستها في Qdrant للقطاع (${result.sector}).`
        );
        uploadForm.reset();
        fileLabel.textContent = "اسحب ملف PDF هنا أو اضغط للاختيار";
      } else {
        showFeedback("error", `❌ فشل الرفع: ${result.detail || "حدث خطأ غير متوقع"}`);
      }
    } catch (err) {
      showFeedback("error", `❌ خطأ في الاتصال بالخادم: ${err.message}`);
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.innerHTML = "<span>رفع وتضمين في Qdrant</span>";
    }
  });

  // -------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------
  function generateSessionId() {
    return "sess_" + Math.random().toString(36).substring(2, 10);
  }

  function updateSessionDisplay() {
    sessionDisplay.textContent = `كود الجلسة: ${sessionId.substring(0, 12)}`;
  }

  function appendMessage(role, text, sources = []) {
    const wrapper = document.createElement("div");
    wrapper.className = `message-wrapper ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "👤" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    const textEl = document.createElement("div");
    textEl.className = "message-text";
    
    // Simple line break / formatting parser
    textEl.innerHTML = formatMarkdownText(text);
    bubble.appendChild(textEl);

    // If sources exist, add attribution card
    if (sources && sources.length > 0) {
      const sourcesCard = document.createElement("div");
      sourcesCard.className = "sources-card";

      const title = document.createElement("div");
      title.className = "sources-title";
      title.textContent = "📚 المصادر المقتبس منها من كتالوج دروسات:";
      sourcesCard.appendChild(title);

      const tagsContainer = document.createElement("div");
      tagsContainer.className = "sources-tags";

      sources.forEach(src => {
        const tag = document.createElement("div");
        tag.className = "source-tag";
        tag.innerHTML = `
          <span class="code">[${src.item_id || 'DOC'}]</span>
          <span>صفحة ${src.page || '1'}</span>
          <span class="score">(${Math.round((src.score || 0) * 100)}% تطابق)</span>
        `;
        tagsContainer.appendChild(tag);
      });

      sourcesCard.appendChild(tagsContainer);
      bubble.appendChild(sourcesCard);
    }

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const id = "typing_" + Date.now();
    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper assistant";
    wrapper.id = id;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "🤖";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble typing-bubble";
    bubble.innerHTML = `
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    `;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
    scrollToBottom();
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function showFeedback(type, message) {
    uploadFeedback.className = `feedback-alert ${type}`;
    uploadFeedback.textContent = message;
    uploadFeedback.classList.remove("hidden");
  }

  function formatMarkdownText(raw) {
    // Converts basic bold, newlines, and bullet points to HTML
    let formatted = raw
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n\n/g, "<br><br>")
      .replace(/\n/g, "<br>");
    return formatted;
  }
});
