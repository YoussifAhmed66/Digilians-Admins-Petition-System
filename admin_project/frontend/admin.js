// 🔴 TODO: Replace with your actual Google Cloud Run URL after deployment
// Example: "https://admin-backend-xxxx-uc.a.run.app/api/admin"
const API_BASE = "/api/admin";


const listView = document.getElementById("listView");
const detailView = document.getElementById("detailView");
const petitionsList = document.getElementById("petitionsList");
const petitionDetails = document.getElementById("petitionDetails");
const fileLinks = document.getElementById("fileLinks");
const petitionHistory = document.getElementById("petitionHistory");
const loading = document.getElementById("loading");

const refreshBtn = document.getElementById("refreshBtn");
const backBtn = document.getElementById("backBtn");
const decisionForm = document.getElementById("decisionForm");

const filterType = document.getElementById("filterType");
const filterStatus = document.getElementById("filterStatus");
const filterDate = document.getElementById("filterDate");
const searchInput = document.getElementById("searchInput");
const clearFiltersBtn = document.getElementById("clearFiltersBtn");

let currentPetitionId = null;
let allPetitions = [];

function showLoading(show) {
  loading.classList.toggle("hidden", !show);
}

async function fetchPetitions() {
  showLoading(true);
  try {
    const res = await fetch(`${API_BASE}/petitions`);
    const data = await res.json();
    allPetitions = data;
    applyFilters();
  } catch (err) {
    alert("تعذر تحميل الطلبات");
  } finally {
    showLoading(false);
  }
}

function applyFilters() {
  let filtered = allPetitions;

  const typeVal   = filterType.value.trim();
  const statusVal = filterStatus.value.trim();
  const dateVal   = filterDate.value.trim();
  const query     = searchInput.value.trim().toLowerCase();

  if (typeVal)   filtered = filtered.filter(p => p.petition_type === typeVal);
  if (statusVal) filtered = filtered.filter(p => p.status === statusVal);
  if (dateVal)   filtered = filtered.filter(p => p.submitted_date === dateVal);

  if (query) {
    filtered = filtered.filter(p =>
      (p.petition_code   || "").toLowerCase().includes(query) ||
      (p.student_name_ar || "").toLowerCase().includes(query) ||
      (p.military_number || "").toLowerCase().includes(query)
    );
  }

  renderList(filtered);
}

function renderList(petitions) {
  // Show result count above table
  const existingCount = document.getElementById("resultCount");
  if (existingCount) existingCount.remove();
  const countBadge = document.createElement("div");
  countBadge.id = "resultCount";
  countBadge.className = "result-count";
  countBadge.style.marginBottom = "12px";
  countBadge.textContent = `${petitions.length} طلب`;
  petitionsList.closest(".card").before(countBadge);

  petitionsList.innerHTML = "";
  petitions.forEach((p) => {
    const tr = document.createElement("tr");
    
    const isInternal = p.petition_type === "internal";
    const typeLabel = isInternal ? "<span class='badge' style='background:#6c757d'>داخلي</span>" : "<span class='badge' style='background:#0d6efd'>خارجي</span>";
    
    const exitDateStr = p.exit_datetime ? new Date(p.exit_datetime).toLocaleDateString("ar-EG") : "-";
    const submissionDateStr = p.submitted_date || "-";

    tr.innerHTML = `
      <td>${p.petition_code}</td>
      <td>${typeLabel}</td>
      <td>${p.student_name_ar}</td>
      <td>${submissionDateStr}</td>
      <td>${exitDateStr}</td>
      <td><span class="badge badge-${p.status}">${getStatusLabel(p.status)}</span></td>
      <td><button class="view-btn" onclick="viewDetails('${p.id}')">عرض</button></td>
    `;
    petitionsList.appendChild(tr);
  });
}

function getStatusLabel(status) {
  switch (status) {
    case "approved": return "تمت الموافقة";
    case "declined": return "مرفوض";
    default: return "قيد الانتظار";
  }
}

async function viewDetails(id) {
  currentPetitionId = id;
  showLoading(true);
  try {
    const res = await fetch(`${API_BASE}/petitions/${id}`);
    const data = await res.json();
    renderDetails(data);
    listView.classList.add("hidden");
    detailView.classList.remove("hidden");
  } catch (err) {
    alert("تعذر تحميل تفاصيل الطلب");
  } finally {
    showLoading(false);
  }
}

async function handlePrint(id, pdfUrl, attachments, existingAdmin) {
  const includeAttachments = document.getElementById('includeAttachments').checked;
  let adminName = existingAdmin || document.getElementById('admin_name').value;
  
  if (!adminName) {
    adminName = prompt("يرجى إدخال اسم المسؤول لتسجيل عملية الطباعة:");
  }
  if (!adminName) return;

  try {
    const notes = includeAttachments ? "تمت الطباعة مع المرفقات" : "تمت الطباعة بدون مرفقات";
    await fetch(`${API_BASE}/petitions/${id}/log-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ admin_name: adminName, action: 'printed', notes: notes })
    });

    // 1. Open the PDF file for printing (PDF is the only format that supports direct browser printing)
    if (pdfUrl) {
      // Adding #toolbar=0 can sometimes help, but opening it is the main step
      const printWin = window.open(pdfUrl, '_blank');
      // Note: Auto-triggering print() on a cross-origin PDF is often blocked, 
      // but the user will see the PDF and can press Ctrl+P or use the print icon.
    } else {
      alert("ملف PDF غير متوفر لهذا الطلب حالياً.");
    }

    // 2. Open attachments if toggled
    if (includeAttachments && attachments && attachments.length > 0) {
      attachments.forEach((att, idx) => {
        setTimeout(() => {
          window.open(att.signed_url, '_blank');
        }, (idx + 1) * 400);
      });
    }

    viewDetails(id);
  } catch (err) {
    console.error(err);
    alert("فشل تسجيل عملية الطباعة");
  }
}

function renderDetails(p) {
  const isInternal = p.petition_type === "internal";
  
  let datesAndReasonsHtml = "";
  if (!isInternal) {
    datesAndReasonsHtml = `
      <div class="detail-row"><span>تاريخ الخروج:</span> ${p.exit_datetime ? new Date(p.exit_datetime).toLocaleString("ar-EG") : "-"}</div>
      <div class="detail-row"><span>تاريخ العودة:</span> ${p.return_datetime ? new Date(p.return_datetime).toLocaleString("ar-EG") : "-"}</div>
      <div class="detail-row"><span>الأسباب:</span> ${p.reasons ? p.reasons.join("، ") : "-"}</div>
    `;
  }

  petitionDetails.innerHTML = `
    <div class="detail-row"><span>نوع الطلب:</span> ${isInternal ? "داخلي" : "خارجي (DEEPS)"}</div>
    <div class="detail-row"><span>الاسم:</span> ${p.student_name_ar}</div>
    <div class="detail-row"><span>الرقم العسكري:</span> ${p.military_number}</div>
    <div class="detail-row"><span>البرنامج:</span> ${p.programs.name_ar}</div>
    <div class="detail-row"><span>المسار:</span> ${p.tracks.name}</div>
    <div class="detail-row"><span>المعمل:</span> ${p.labs.code}</div>
    ${datesAndReasonsHtml}
    <div class="detail-row"><span>الوصف:</span> ${p.description || "لا يوجد"}</div>
    <div class="detail-row"><span>تاريخ التقديم:</span> ${p.submitted_date || "-"}</div>
  `;

  // -- Print Controls (Hidden for now) --------------------------
  /*
  fileLinks.innerHTML = `
    <div class="print-actions-card">
      <h4>إجراءات الطباعة</h4>
      <div class="print-controls">
        <label class="switch-container">
          <input type="checkbox" id="includeAttachments" />
          <span class="switch-slider"></span>
          <span class="switch-label">تشمل المرفقات</span>
        </label>
        <button class="print-primary-btn" onclick="handlePrint('${p.id}', '${p.signed_pdf_url || ''}', ${JSON.stringify(p.attachments || []).replace(/"/g, '&quot;')}, '${p.decided_by || ''}')">
          طباعة الطلب 🖨️
        </button>
      </div>
    </div>
  `;
  */
  fileLinks.innerHTML = ""; // Clear or initialize

  fileLinks.innerHTML += "<h4>المستندات المنشأة</h4>";
  if (p.signed_pdf_url) {
    fileLinks.innerHTML += `<div class="detail-row"><span>ملف PDF:</span> <a href="${p.signed_pdf_url}" class="file-link" target="_blank">تحميل PDF</a></div>`;
  } else {
    fileLinks.innerHTML += `<div class="detail-row"><span>ملف PDF:</span> <span class="empty-msg">غير متوفر حالياً</span></div>`;
  }

  fileLinks.innerHTML += "<h4 style='margin-top:1rem'>المرفقات المرفوعة</h4>";
  if (p.attachments && p.attachments.length) {
    const ul = document.createElement("ul");
    ul.className = "file-list";
    p.attachments.forEach(att => {
      ul.innerHTML += `<li><a href="${att.signed_url}" class="file-link" target="_blank">${att.original_name || 'مرفق'}</a></li>`;
    });
    fileLinks.appendChild(ul);
  } else {
    fileLinks.innerHTML += "<p class='empty-msg'>لا توجد مرفقات</p>";
  }
  
  // Set radio buttons if already decided
  if (p.status !== "pending") {
    const radio = decisionForm.querySelector(`input[value="${p.status}"]`);
    if(radio) radio.checked = true;
    decisionForm.admin_notes.value = p.admin_notes || "";
  } else {
    decisionForm.reset();
  }

  renderHistory(p.history || []);
}

function renderHistory(history) {
  petitionHistory.innerHTML = "";
  if (!history.length) {
    petitionHistory.innerHTML = "<p class='empty-msg'>لا يوجد سجل لهذا الطلب بعد</p>";
    return;
  }

  const table = document.createElement("table");
  table.className = "history-table";
  table.innerHTML = `
    <thead>
      <tr>
        <th>الإجراء</th>
        <th>المسؤول</th>
        <th>التاريخ والوقت</th>
        <th>الملاحظات</th>
      </tr>
    </thead>
    <tbody></tbody>
  `;

  const tbody = table.querySelector("tbody");
  history.forEach(item => {
    const tr = document.createElement("tr");
    
    const date = new Date(item.created_at).toLocaleString("ar-EG", {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
    const actionLabel = getActionLabel(item.action);
    const color = getActionColor(item.action);
    
    tr.innerHTML = `
      <td><span class="status-badge" style="background: ${color}20; color: ${color}; border: 1px solid ${color}40">${actionLabel}</span></td>
      <td><strong>${item.admin_name || "-"}</strong></td>
      <td class="date-cell">${date}</td>
      <td class="notes-cell">${item.admin_notes || "-"}</td>
    `;
    tbody.appendChild(tr);
  });
  
  petitionHistory.appendChild(table);
}

function getActionLabel(action) {
  switch (action) {
    case "submitted": return "تم تقديم الطلب";
    case "approved": return "تمت الموافقة";
    case "declined": return "تم الرفض";
    default: return action;
  }
}

function getActionColor(action) {
  switch (action) {
    case "submitted": return "#64748b";
    case "approved": return "#22c55e";
    case "declined": return "#ef4444";
    default: return "#94a3b8";
  }
}

backBtn.addEventListener("click", () => {
  detailView.classList.add("hidden");
  listView.classList.remove("hidden");
  fetchPetitions();
});

refreshBtn.addEventListener("click", fetchPetitions);

decisionForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(decisionForm);
  const status = formData.get("status");
  const admin_name = formData.get("admin_name");
  const admin_notes = formData.get("admin_notes");

  showLoading(true);
  try {
    const res = await fetch(`${API_BASE}/petitions/${currentPetitionId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, admin_name, admin_notes })
    });
    if (!res.ok) throw new Error();
    alert("تم حفظ القرار وإعادة توليد المستندات بنجاح");
    viewDetails(currentPetitionId); // Refresh details
  } catch (err) {
    alert("فشل حفظ القرار");
  } finally {
    showLoading(false);
  }
});

// Event listeners for filters
filterType.addEventListener("change", applyFilters);
filterStatus.addEventListener("change", applyFilters);
filterDate.addEventListener("change", applyFilters);
searchInput.addEventListener("input", applyFilters);

clearFiltersBtn.addEventListener("click", () => {
  filterType.value   = "";
  filterStatus.value = "";
  filterDate.value   = "";
  searchInput.value  = "";
  applyFilters();
});

// Init
fetchPetitions();
