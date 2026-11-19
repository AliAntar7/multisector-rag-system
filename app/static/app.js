// DROSAT RAG Client Application - ChatGPT / Antigravity UI
document.addEventListener("DOMContentLoaded", () => {
  // State
  let activeSector = "all";
  let activeSectorLabel = "جميع القطاعات (بحث عام)";
  let activeSavedSessionId = null; // No history item active by default on fresh load
  let sessionId = generateSessionId();

  const sectorNames = {
    "all": "جميع القطاعات (بحث عام)",
    "courses_curriculum": "المناهج والكورسات",
    "teachers_centers": "المدرسين والسناتر والمواعيد",
    "policies_support": "السياسات والدعم الفني"
  };

  const sectorIcons = {
    "all": "🌐",
    "courses_curriculum": "📚",
    "teachers_centers": "🏫",
    "policies_support": "💳"
  };

  // DOM Elements
  const sidebarDrawer = document.getElementById("sidebarDrawer");
  const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
  const newChatBtn = document.getElementById("newChatBtn");
  const historyList = document.getElementById("historyList");
  const sessionDisplay = document.getElementById("sessionDisplay");
  
  const messagesViewport = document.getElementById("messagesViewport");
  const messagesContainer = document.getElementById("messagesContainer");
  const chatForm = document.getElementById("chatForm");
  const queryInput = document.getElementById("queryInput");
  const sendBtn = document.getElementById("sendBtn");

  // Sector Dropup & Help Elements (Model Picker Style)
  const sectorTriggerBtn = document.getElementById("sectorTriggerBtn");
  const sectorMenu = document.getElementById("sectorMenu");
  const sectorOptions = document.querySelectorAll(".sector-option");
  const activeSectorNameEl = document.getElementById("activeSectorName");
  const activeSectorIconEl = document.getElementById("activeSectorIcon");

  const sectorHelpBtn = document.getElementById("sectorHelpBtn");
  const helpPopover = document.getElementById("helpPopover");
  const closeHelpPopoverBtn = document.getElementById("closeHelpPopoverBtn");

  // Ingestion Modal Elements
  const uploadModal = document.getElementById("uploadModal");
  const openUploadModalBtn = document.getElementById("openUploadModalBtn");
  const closeUploadModalBtn = document.getElementById("closeUploadModalBtn");
  const cancelUploadBtn = document.getElementById("cancelUploadBtn");
  const uploadForm = document.getElementById("uploadForm");
  const pdfFileInput = document.getElementById("pdfFileInput");
  const uploadSector = document.getElementById("uploadSector");
  const uploadBtn = document.getElementById("uploadBtn");
  const fileLabel = document.getElementById("fileLabel");
  const uploadFeedback = document.getElementById("uploadFeedback");

  // Initial UI Setup
  updateSessionDisplay();
  setSectorByCode(activeSector);
  fetchSessions();

  // -------------------------------------------------------------
  // 1. Sidebar Toggle & Responsiveness
  // -------------------------------------------------------------
  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener("click", () => {
      sidebarDrawer.classList.toggle("collapsed");
    });
  }

  // -------------------------------------------------------------
  // 2. Sector Dropup Selection (Model Picker Style)
  // -------------------------------------------------------------
  if (sectorTriggerBtn) {
    sectorTriggerBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      sectorMenu.classList.toggle("hidden");
      sectorTriggerBtn.classList.toggle("open");
      if (helpPopover) helpPopover.classList.add("hidden");
    });
  }

  sectorOptions.forEach(opt => {
    opt.addEventListener("click", () => {
      const code = opt.getAttribute("data-sector");
      setSectorByCode(code);
      closeSectorMenu();
    });
  });

  function setSectorByCode(sector) {
    if (!sector || !sectorNames[sector]) sector = "all";
    activeSector = sector;
    activeSectorLabel = sectorNames[sector];

    if (activeSectorNameEl) activeSectorNameEl.textContent = activeSectorLabel;
    if (activeSectorIconEl) activeSectorIconEl.textContent = sectorIcons[sector] || "🌐";

    sectorOptions.forEach(opt => {
      if (opt.getAttribute("data-sector") === sector) opt.classList.add("active");
      else opt.classList.remove("active");
    });
  }

  function closeSectorMenu() {
    if (sectorMenu) sectorMenu.classList.add("hidden");
    if (sectorTriggerBtn) sectorTriggerBtn.classList.remove("open");
  }

  // Help Popover
  if (sectorHelpBtn) {
    sectorHelpBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      helpPopover.classList.toggle("hidden");
      closeSectorMenu();
    });
  }

  if (closeHelpPopoverBtn) {
    closeHelpPopoverBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      helpPopover.classList.add("hidden");
    });
  }

  // Global click outside to dismiss menus
  document.addEventListener("click", (e) => {
    if (sectorMenu && !sectorMenu.contains(e.target) && !sectorTriggerBtn.contains(e.target)) {
      closeSectorMenu();
    }
    if (helpPopover && !helpPopover.contains(e.target) && !sectorHelpBtn.contains(e.target)) {
      helpPopover.classList.add("hidden");
    }
  });

  // -------------------------------------------------------------
  // 3. New Chat Action
  // -------------------------------------------------------------
  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
      startNewChat();
    });
  }

  function startNewChat() {
    activeSavedSessionId = null;
    sessionId = generateSessionId();
    updateSessionDisplay();
    renderWelcomeMessage();
    document.querySelectorAll(".history-item").forEach(item => item.classList.remove("active"));
    queryInput.focus();
  }

  function renderWelcomeMessage() {
    messagesContainer.innerHTML = `
      <div class="chat-row assistant">
        <div class="chat-row-content">
          <div class="msg-avatar bot-avatar">🤖</div>
          <div class="msg-body">
            <div class="msg-author">المساعد الذكي لمنصة دروسات</div>
            <div class="msg-text">
              <p>أهلاً بك يا بطل في المساعد الذكي الرسمي لمنصة <strong>دروسات التعليمية</strong>! 👋</p>
              <p>أنا مبرمج بنظام RAG متصل بكتالوج المنصة الرسمي مباشرة لتقديم إجابات موثقة بالصفحة وكود العنصر عن:</p>
              <ul>
                <li>📚 <strong>المناهج والكورسات:</strong> محتوى الحصص والأسعار والمدرسين (تالتة ثانوي، أولى وتانية).</li>
                <li>🏫 <strong>المدرسين والسناتر:</strong> مواعيد الحصص في السناتر وأرقام التواصل والقاعات.</li>
                <li>💳 <strong>سياسات الاشتراك والدعم:</strong> الدفع بكاشير وفوري وتوصيل الملازم للمحافظات.</li>
              </ul>
            </div>
            <div class="quick-prompts-wrapper">
              <div class="quick-prompts-label">
                <span class="sparkle-icon">✨</span>
                <span>اسأل عن:</span>
              </div>
              <div class="quick-prompts">
                <button class="prompt-chip" data-prompt="تفاصيل كورس الفيزياء لتالتة ثانوي وسعره كام ومين المدرس؟" data-sector="courses_curriculum">
                  🔬 كورس فيزياء تالتة ثانوي
                </button>
                <button class="prompt-chip" data-prompt="مواعيد وسنتر مستر محمد عبدالمعبود في مدينة نصر ورقم التواصل؟" data-sector="teachers_centers">
                  👨‍🏫 مواعيد مستر محمد عبدالمعبود
                </button>
                <button class="prompt-chip" data-prompt="صلاحية كود فوري ومواعيد شحن الملازم للمحافظات؟" data-sector="policies_support">
                  🚚 شحن الملازم وكود فوري
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    scrollToBottom();
  }

  // -------------------------------------------------------------
  // 4. Session History List (MongoDB)
  // -------------------------------------------------------------
  async function fetchSessions() {
    if (!historyList) return;
    try {
      const res = await fetch("/api/sessions/");
      if (!res.ok) throw new Error("Failed to fetch sessions");
      const sessions = await res.json();
      renderHistoryList(sessions);
    } catch (err) {
      console.warn("Could not load sessions from Atlas:", err);
      historyList.innerHTML = `<div class="history-empty">تعذر جلب السجل من السيرفر</div>`;
    }
  }

  function renderHistoryList(sessions) {
    if (!sessions || sessions.length === 0) {
      historyList.innerHTML = `<div class="history-empty">لا توجد محادثات سابقة بعد</div>`;
      return;
    }

    historyList.innerHTML = "";
    sessions.forEach(sess => {
      const item = document.createElement("div");
      item.className = "history-item" + (activeSavedSessionId && sess.session_id === activeSavedSessionId ? " active" : "");
      item.setAttribute("data-id", sess.session_id);

      const content = document.createElement("div");
      content.className = "history-item-content";

      const title = document.createElement("div");
      title.className = "history-item-title";
      title.textContent = sess.title || "محادثة بدون عنوان";
      title.title = sess.title;

      const meta = document.createElement("div");
      meta.className = "history-item-meta";
      const countText = `${sess.message_count || 1} رسائل`;
      meta.textContent = `${countText} • ${formatDate(sess.last_active)}`;

      content.appendChild(title);
      content.appendChild(meta);

      const actions = document.createElement("div");
      actions.className = "history-item-actions";
      const delBtn = document.createElement("button");
      delBtn.className = "btn-delete-session";
      delBtn.title = "حذف المحادثة";
      delBtn.innerHTML = `
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      `;
      delBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteSession(sess.session_id);
      });
      actions.appendChild(delBtn);

      item.appendChild(content);
      item.appendChild(actions);

      item.addEventListener("click", () => {
        loadSession(sess.session_id);
      });

      historyList.appendChild(item);
    });
  }

  async function loadSession(targetSessionId) {
    if (targetSessionId === activeSavedSessionId && messagesContainer.children.length > 1) {
      return; // Already open
    }
    activeSavedSessionId = targetSessionId;
    sessionId = targetSessionId;
    updateSessionDisplay();

    // Mark active in sidebar
    document.querySelectorAll(".history-item").forEach(item => {
      if (item.getAttribute("data-id") === activeSavedSessionId) item.classList.add("active");
      else item.classList.remove("active");
    });

    try {
      const res = await fetch(`/api/sessions/${sessionId}`);
      if (!res.ok) throw new Error("Failed to load session messages");
      const turns = await res.json();

      messagesContainer.innerHTML = "";
      if (turns.length === 0) {
        renderWelcomeMessage();
        return;
      }

      turns.forEach(turn => {
        appendUserMessage(turn.user_query, turn.sector);
        appendAssistantMessage(turn.assistant_response, turn.sources);
      });
      scrollToBottom();
    } catch (err) {
      console.error("Error loading session:", err);
      alert("تعذر تحميل المحادثة المحددة من السيرفر.");
    }
  }

  async function deleteSession(targetSessionId) {
    if (!confirm("هل أنت متأكد من حذف هذه المحادثة من سجل MongoDB؟")) return;
    try {
      const res = await fetch(`/api/sessions/${targetSessionId}`, { method: "DELETE" });
      if (res.ok) {
        if (targetSessionId === activeSavedSessionId) {
          startNewChat();
        } else {
          fetchSessions();
        }
      }
    } catch (err) {
      console.error("Error deleting session:", err);
    }
  }

  // -------------------------------------------------------------
  // 5. Chat Interaction
  // -------------------------------------------------------------
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // Append User Message
    appendUserMessage(query, activeSector);
    queryInput.value = "";
    queryInput.style.height = "auto";
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
      appendAssistantMessage(data.answer, data.sources);
      // Mark current session as active saved session and refresh list
      activeSavedSessionId = sessionId;
      fetchSessions();
    } catch (err) {
      removeTypingIndicator(typingId);
      appendAssistantMessage(
        "عذراً، حدث خطأ أثناء الاتصال بالخادم. يرجى التأكد من تشغيل السيرفر والمحاولة مرة أخرى."
      );
      console.error("Chat error:", err);
    } finally {
      sendBtn.disabled = false;
      queryInput.focus();
    }
  });

  // Textarea auto-resize and Enter key behavior
  queryInput.addEventListener("input", () => {
    queryInput.style.height = "auto";
    queryInput.style.height = Math.min(queryInput.scrollHeight, 140) + "px";
  });

  queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Quick Prompt Chips Delegation
  document.addEventListener("click", (e) => {
    const chip = e.target.closest(".prompt-chip");
    if (chip) {
      const prompt = chip.getAttribute("data-prompt");
      const sector = chip.getAttribute("data-sector");
      if (sector) {
        setSectorByCode(sector);
      }
      queryInput.value = prompt;
      queryInput.style.height = "auto";
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // -------------------------------------------------------------
  // 6. PDF Ingestion Modal Handlers
  // -------------------------------------------------------------
  if (openUploadModalBtn) {
    openUploadModalBtn.addEventListener("click", () => {
      uploadModal.classList.remove("hidden");
    });
  }

  function closeUploadModal() {
    if (uploadModal) {
      uploadModal.classList.add("hidden");
      uploadFeedback.classList.add("hidden");
      uploadForm.reset();
      fileLabel.textContent = "اسحب ملف PDF هنا أو اضغط للتصفح";
      uploadBtn.disabled = true;
    }
  }

  if (closeUploadModalBtn) closeUploadModalBtn.addEventListener("click", closeUploadModal);
  if (cancelUploadBtn) cancelUploadBtn.addEventListener("click", closeUploadModal);

  if (uploadModal) {
    uploadModal.addEventListener("click", (e) => {
      if (e.target === uploadModal) {
        closeUploadModal();
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && uploadModal && !uploadModal.classList.contains("hidden")) {
      closeUploadModal();
    }
  });

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
    uploadBtn.innerHTML = "<span>فهرسة في Qdrant... ⏳</span>";
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
          `✅ تم بنجاح: تم استخراج وتضمين ${result.chunks_extracted} فقرة للقطاع (${result.sector}) في سحابة Qdrant.`
        );
        uploadForm.reset();
        fileLabel.textContent = "اسحب ملف PDF هنا أو اضغط للتصفح";
      } else {
        showFeedback("error", `❌ فشل الرفع: ${result.detail || "حدث خطأ غير متوقع"}`);
      }
    } catch (err) {
      showFeedback("error", `❌ خطأ في الاتصال بالخادم: ${err.message}`);
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.innerHTML = "<span>فهرسة وتضمين في Qdrant ⚡</span>";
    }
  });

  // -------------------------------------------------------------
  // 7. Message Rendering Helpers
  // -------------------------------------------------------------
  function appendUserMessage(text, sector) {
    const row = document.createElement("div");
    row.className = "chat-row user";

    const content = document.createElement("div");
    content.className = "chat-row-content";

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar user-avatar";
    avatar.textContent = "👤";

    const body = document.createElement("div");
    body.className = "msg-body";

    if (sector && sector !== "all") {
      const badge = document.createElement("div");
      badge.className = "msg-sector-badge";
      badge.textContent = `🏷️ قطاع: ${sectorNames[sector] || sector}`;
      body.appendChild(badge);
    }

    const textBubble = document.createElement("div");
    textBubble.className = "msg-text";
    textBubble.textContent = text;
    body.appendChild(textBubble);

    content.appendChild(avatar);
    content.appendChild(body);
    row.appendChild(content);

    messagesContainer.appendChild(row);
    scrollToBottom();
  }

  function appendAssistantMessage(text, sources = []) {
    const row = document.createElement("div");
    row.className = "chat-row assistant";

    const content = document.createElement("div");
    content.className = "chat-row-content";

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar bot-avatar";
    avatar.textContent = "🤖";

    const body = document.createElement("div");
    body.className = "msg-body";

    const author = document.createElement("div");
    author.className = "msg-author";
    author.textContent = "المساعد الذكي لمنصة دروسات";
    body.appendChild(author);

    const textBubble = document.createElement("div");
    textBubble.className = "msg-text";
    textBubble.innerHTML = formatMarkdownText(text);
    body.appendChild(textBubble);

    // Citations Attribution Card
    if (sources && sources.length > 0) {
      const sourcesCard = document.createElement("div");
      sourcesCard.className = "sources-card";

      const title = document.createElement("div");
      title.className = "sources-title";
      title.innerHTML = `
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
        <span>المصادر المقتبسة من كتالوج دروسات الرسمي:</span>
      `;
      sourcesCard.appendChild(title);

      const tagsContainer = document.createElement("div");
      tagsContainer.className = "sources-tags";

      sources.forEach(src => {
        const tag = document.createElement("div");
        tag.className = "source-tag";
        tag.innerHTML = `
          <span class="code">[${src.item_id || 'DOC'}]</span>
          <span>صفحة ${src.page || '1'}</span>
          <span class="score">${Math.round((src.score || 0) * 100)}% تطابق</span>
        `;
        tagsContainer.appendChild(tag);
      });

      sourcesCard.appendChild(tagsContainer);
      body.appendChild(sourcesCard);
    }

    content.appendChild(avatar);
    content.appendChild(body);
    row.appendChild(content);

    messagesContainer.appendChild(row);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const id = "typing_" + Date.now();
    const row = document.createElement("div");
    row.className = "chat-row assistant";
    row.id = id;

    const content = document.createElement("div");
    content.className = "chat-row-content";

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar bot-avatar";
    avatar.textContent = "🤖";

    const body = document.createElement("div");
    body.className = "msg-body";

    const typingBubble = document.createElement("div");
    typingBubble.className = "typing-bubble";
    typingBubble.innerHTML = `
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    `;

    body.appendChild(typingBubble);
    content.appendChild(avatar);
    content.appendChild(body);
    row.appendChild(content);

    messagesContainer.appendChild(row);
    scrollToBottom();
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function scrollToBottom() {
    messagesViewport.scrollTop = messagesViewport.scrollHeight;
  }

  function generateSessionId() {
    return "sess_" + Math.random().toString(36).substring(2, 10);
  }

  function updateSessionDisplay() {
    if (sessionDisplay) {
      sessionDisplay.textContent = `جلسة: ${sessionId.substring(0, 12)}`;
    }
  }

  function showFeedback(type, message) {
    uploadFeedback.className = `feedback-badge ${type}`;
    uploadFeedback.textContent = message;
    uploadFeedback.classList.remove("hidden");
  }

  function formatDate(isoStr) {
    if (!isoStr) return "الآن";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString("ar-EG", { month: "short", day: "numeric" });
    } catch {
      return "سابقاً";
    }
  }

  function formatMarkdownText(raw) {
    if (!raw) return "";

    let text = raw
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");

    const lines = text.split("\n");
    let result = [];
    let inList = false;
    let listType = "ul";

    for (let line of lines) {
      const trimmed = line.trim();
      const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
      const bulletMatch = trimmed.match(/^[-*]\s+(.*)/);

      if (numMatch) {
        if (!inList || listType !== "ol") {
          if (inList) result.push(`</${listType}>`);
          result.push("<ol>");
          inList = true;
          listType = "ol";
        }
        result.push(`<li>${numMatch[2]}</li>`);
      } else if (bulletMatch) {
        if (!inList || listType !== "ul") {
          if (inList) result.push(`</${listType}>`);
          result.push("<ul>");
          inList = true;
          listType = "ul";
        }
        result.push(`<li>${bulletMatch[1]}</li>`);
      } else {
        if (inList) {
          result.push(`</${listType}>`);
          inList = false;
        }
        if (trimmed) {
          result.push(`<p>${trimmed}</p>`);
        }
      }
    }

    if (inList) {
      result.push(`</${listType}>`);
    }

    return result.join("");
  }
});
