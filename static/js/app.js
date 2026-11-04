document.addEventListener("DOMContentLoaded", () => {
  // Modal de confirmação de eliminação
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-delete-url]");
    if (!b) return;
    document.getElementById("deleteForm").action = b.dataset.deleteUrl;
    document.getElementById("deleteName").textContent = b.dataset.deleteName;
  });
  // Toasts
  document.querySelectorAll(".toast").forEach(t => new bootstrap.Toast(t, {delay: 5000}).show());
  // Menu mobile
  const t = document.getElementById("sidebarToggle");
  if (t) t.addEventListener("click", () => document.querySelector(".sidebar").classList.toggle("show"));
  // Pesquisa dinâmica: submete os filtros ao escrever / alterar
  const form = document.querySelector("form.filter-form");
  if (form) {
    let timer;
    form.querySelectorAll("input[type=text],input[type=number]").forEach(i =>
      i.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => { sessionStorage.setItem("focus", i.name); form.submit(); }, 450); }));
    form.querySelectorAll("select,input[type=date]").forEach(i => i.addEventListener("change", () => form.submit()));
    const f = sessionStorage.getItem("focus");
    if (f) { sessionStorage.removeItem("focus"); const el = form.querySelector(`[name="${f}"]`); if (el) { el.focus(); try { el.setSelectionRange(el.value.length, el.value.length); } catch (e) {} } }
  }
});
