/* Dark Leyla Vault Studio — browser-local registry prototype.
 * Demo records only. This module does not authenticate users, authorize actions,
 * upload assets, or create privileged approvals. Server integration is a separate gate.
 */
(() => {
  "use strict";
  const KEY = "dark-leyla-vault-registry:v1";
  const $ = (id) => document.getElementById(id);
  const now = () => new Date().toISOString();
  const uid = (prefix) => prefix + "_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  const emptyState = () => ({ schema: 1, profiles: [], assets: [], activity: [] });
  let state = null;
  let activeProfileId = null;

  function validState(value) {
    return !!value && value.schema === 1 &&
      Array.isArray(value.profiles) && Array.isArray(value.assets) && Array.isArray(value.activity);
  }
  function load() {
    if (state) return state;
    try {
      const raw = localStorage.getItem(KEY);
      const parsed = raw ? JSON.parse(raw) : null;
      state = validState(parsed) ? parsed : emptyState();
    } catch {
      state = emptyState();
    }
    return state;
  }
  function persist(next, action, detail, profileId) {
    const event = { id: uid("act"), at: now(), action, detail, profileId: profileId || null };
    next.activity = [event, ...(next.activity || [])].slice(0, 500);
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
    } catch {
      toast("Browser storage is full. Export a backup or remove large records.");
      return false;
    }
    state = next;
    render();
    return true;
  }
  function toast(message) {
    const node = $("toast");
    if (!node) return;
    node.textContent = message;
    node.classList.add("show");
    window.clearTimeout(toast.timer);
    toast.timer = window.setTimeout(() => node.classList.remove("show"), 2800);
  }
  function node(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }
  function optionList(select, rows, placeholder) {
    select.replaceChildren();
    if (placeholder) select.append(new Option(placeholder, ""));
    rows.forEach((row) => select.append(new Option(row.label, row.value)));
  }
  function addProfile(data) {
    const stamp = now();
    const profile = {
      id: uid("persona"), name: data.name, codename: data.codename, category: data.category,
      role: data.role, identity: data.identity, notes: data.notes,
      skills: data.skills, tags: data.tags, status: "TAGGED", archived: false,
      revisions: [{ version: 1, summary: "Registry profile created", at: stamp }],
      createdAt: stamp, updatedAt: stamp
    };
    const next = load();
    next.profiles.unshift(profile);
    activeProfileId = profile.id;
    return persist(next, "PROFILE_CREATED", "Persona registered: " + profile.name, profile.id);
  }
  function saveProfile() {
    const name = $("personaName").value.trim();
    if (!name) return toast("A display name is required.");
    const data = {
      name,
      codename: $("personaCodename").value.trim(),
      category: $("personaCategory").value,
      role: $("personaRole").value,
      identity: $("personaIdentity").value.trim(),
      notes: $("personaNotes").value.trim(),
      skills: $("personaSkills").value.split(",").map(x => x.trim()).filter(Boolean),
      tags: $("personaTags").value.split(",").map(x => x.trim().toLowerCase()).filter(Boolean)
    };
    const next = load();
    const existing = next.profiles.find(p => p.id === activeProfileId);
    if (!existing) {
      if (addProfile(data)) toast("Persona saved to this browser's demo registry.");
      return;
    }
    const changed = ["name","codename","category","role","identity","notes"].some(k => existing[k] !== data[k]) ||
      JSON.stringify(existing.skills) !== JSON.stringify(data.skills) || JSON.stringify(existing.tags) !== JSON.stringify(data.tags);
    if (!changed) return toast("No profile changes to save.");
    const version = (existing.revisions?.length || 1) + 1;
    Object.assign(existing, data, { updatedAt: now() });
    existing.revisions = [{ version, summary: "Profile metadata revised", at: existing.updatedAt }, ...(existing.revisions || [])];
    if (persist(next, "PROFILE_REVISED", "Persona revised to v" + version + ": " + existing.name, existing.id)) {
      toast("New profile revision saved locally.");
    }
  }
  function selectProfile(id) {
    const p = load().profiles.find(x => x.id === id);
    if (!p) return;
    activeProfileId = p.id;
    $("personaName").value = p.name || "";
    $("personaCodename").value = p.codename || "";
    $("personaCategory").value = p.category || "AI Persona";
    $("personaRole").value = p.role || "Assistant persona";
    $("personaIdentity").value = p.identity || "";
    $("personaNotes").value = p.notes || "";
    $("personaSkills").value = (p.skills || []).join(", ");
    $("personaTags").value = (p.tags || []).join(", ");
    $("personaStatus").value = p.status || "TAGGED";
    renderProfiles();
    renderRevisions(p);
  }
  function renderRevisions(profile) {
    const target = $("revisionList");
    if (!target) return;
    target.replaceChildren();
    (profile?.revisions || []).forEach(r => {
      const item = node("div", "mini-card");
      item.append(node("strong", "", "v" + r.version + " · " + r.summary));
      item.append(node("p", "", new Date(r.at).toLocaleString()));
      target.append(item);
    });
    if (!profile) target.append(node("p", "micro", "Select a persona to inspect its revisions."));
  }
  function renderProfiles() {
    const target = $("personaRegistryList");
    if (!target) return;
    target.replaceChildren();
    const q = ($("personaSearch")?.value || "").trim().toLowerCase();
    const status = $("personaFilter")?.value || "ALL";
    const rows = load().profiles.filter(p => {
      const hay = [p.name,p.codename,p.category,p.role,p.identity,p.notes,...(p.skills||[]),...(p.tags||[])].join(" ").toLowerCase();
      return (!q || hay.includes(q)) && (status === "ALL" || p.status === status);
    });
    if (!rows.length) {
      target.append(node("div", "empty-state", "No matching persona records. Create a profile above to begin the local registry."));
      return;
    }
    rows.forEach(p => {
      const card = node("div", "queue-item");
      const icon = node("div", "thumb", "◉");
      const body = node("div");
      body.append(node("strong", "", p.name + (p.codename ? " · " + p.codename : "")));
      body.append(node("small", "", (p.category || "Persona") + " · " + (p.role || "Unassigned") + " · v" + (p.revisions?.length || 1)));
      const statusTag = node("span", "tag", p.archived ? "ARCHIVED" : p.status);
      const open = node("button", "btn", "Open");
      open.type = "button";
      open.addEventListener("click", () => selectProfile(p.id));
      card.append(icon, body, statusTag, open);
      target.append(card);
    });
  }
  function updateCatalogStatus() {
    const p = load().profiles.find(x => x.id === activeProfileId);
    if (!p) return toast("Select or save a persona first.");
    const status = $("personaStatus").value;
    const noteText = $("personaReviewNote").value.trim();
    if (status === "SEALED") return toast("Use the separate catalog seal action after local confirmation.");
    if (!noteText) return toast("Add a review note before changing catalog status.");
    if (status === "CONFIRMED" && !window.confirm("Mark this profile CONFIRMED in the local demo catalog only? This is not identity, rights, consent, or production approval.")) return;
    p.status = status;
    p.archived = status === "ARCHIVED";
    p.updatedAt = now();
    if (!p.reviewNotes) p.reviewNotes = [];
    p.reviewNotes.unshift({ id: uid("review"), at: p.updatedAt, status, note: noteText });
    $("personaReviewNote").value = "";
    if (persist(load(), "CATALOG_REVIEW", "Local catalog status set to " + status + " for " + p.name, p.id)) {
      toast("Catalog status updated locally. No privileged approval was created.");
    }
  }
  function sealProfile() {
    const p = load().profiles.find(x => x.id === activeProfileId);
    if (!p) return toast("Select a persona first.");
    if (p.status !== "CONFIRMED" || p.archived) return toast("Only locally CONFIRMED, non-archived profiles can receive a catalog seal.");
    if (!window.confirm("Apply a catalog-only seal? This does not authorize production, publication, rights, or identity.")) return;
    p.status = "SEALED";
    p.updatedAt = now();
    p.revisions = [{ version: (p.revisions?.length || 1) + 1, summary: "Catalog seal applied (non-authoritative)", at: p.updatedAt }, ...(p.revisions || [])];
    if (persist(load(), "CATALOG_SEALED", "Catalog-only seal applied to " + p.name, p.id)) {
      toast("Catalog seal recorded. No production permission was granted.");
    }
  }
  function addAsset() {
    const title = $("assetTitle").value.trim();
    const profileId = $("assetProfile").value;
    if (!title || !profileId) return toast("Choose a persona and enter an asset title.");
    const asset = {
      id: uid("asset"), profileId, title, type: $("assetType").value,
      version: $("assetVersion").value.trim() || "v1",
      sourceUrl: $("assetSource").value.trim(),
      visibility: $("assetVisibility").value,
      createdAt: now()
    };
    const next = load();
    next.assets.unshift(asset);
    if (persist(next, "ASSET_REGISTERED", "Asset metadata registered: " + title, profileId)) {
      $("assetTitle").value = "";
      $("assetVersion").value = "v1";
      $("assetSource").value = "";
      toast("Asset metadata saved locally. No file was uploaded.");
    }
  }
  function renderAssets() {
    const target = $("assetRegistryList");
    if (!target) return;
    target.replaceChildren();
    const profiles = new Map(load().profiles.map(p => [p.id,p.name]));
    optionList($("assetProfile"), load().profiles.map(p => ({label:p.name,value:p.id})), "Select persona");
    if (!load().assets.length) {
      target.append(node("div", "empty-state", "No asset metadata has been registered."));
      return;
    }
    load().assets.forEach(a => {
      const card = node("div", "queue-item");
      card.append(node("div", "thumb", "▣"));
      const body = node("div");
      body.append(node("strong", "", a.title));
      body.append(node("small", "", (profiles.get(a.profileId) || "Unknown persona") + " · " + a.type + " · " + a.version));
      card.append(body, node("span", "tag", a.visibility));
      target.append(card);
    });
  }
  function renderActivity() {
    const target = $("activityList");
    if (!target) return;
    target.replaceChildren();
    if (!load().activity.length) {
      target.append(node("div", "empty-state", "No activity yet. Registry actions will be recorded in this browser only."));
      return;
    }
    load().activity.forEach(a => {
      const item = node("div", "queue-item");
      item.append(node("div", "thumb", "◷"));
      const body = node("div");
      body.append(node("strong", "", a.action));
      body.append(node("small", "", new Date(a.at).toLocaleString() + " · " + a.detail));
      item.append(body);
      target.append(item);
    });
  }
  function renderStats() {
    $("statProfiles") && ($("statProfiles").textContent = String(load().profiles.length));
    $("statAssets") && ($("statAssets").textContent = String(load().assets.length));
    $("statPending") && ($("statPending").textContent = String(load().profiles.filter(p => p.status === "PENDING_REVIEW").length));
  }
  function render() {
    renderProfiles();
    renderAssets();
    renderActivity();
    renderStats();
    const p = load().profiles.find(x => x.id === activeProfileId);
    renderRevisions(p);
  }
  function exportBackup() {
    const blob = new Blob([JSON.stringify(load(), null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "dark-leyla-vault-demo-backup.json";
    a.click();
    URL.revokeObjectURL(url);
    toast("Local JSON backup exported.");
  }
  function importBackup(file) {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result || ""));
        if (!validState(parsed)) throw new Error("Backup schema is not supported.");
        const profileIds = new Set(parsed.profiles.map(p => p.id));
        if (parsed.assets.some(a => !profileIds.has(a.profileId))) throw new Error("Backup contains an asset with no matching persona.");
        state = parsed;
        if (!persist(state, "BACKUP_IMPORTED", "JSON backup imported into local demo storage.")) throw new Error("Could not write imported backup.");
        activeProfileId = null;
        render();
        toast("Backup imported to this browser only.");
      } catch (e) {
        toast("Import rejected: " + (e?.message || "invalid backup"));
      }
    };
    reader.readAsText(file);
  }
  function resetDemo() {
    if (!window.confirm("Clear this browser's Dark Leyla demo registry? Export a backup first if needed.")) return;
    state = emptyState();
    activeProfileId = null;
    try {
      localStorage.removeItem(KEY);
      render();
      toast("Local demo registry cleared.");
    } catch {
      toast("Could not clear browser storage.");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    $("personaSave")?.addEventListener("click", saveProfile);
    $("personaSearch")?.addEventListener("input", renderProfiles);
    $("personaFilter")?.addEventListener("change", renderProfiles);
    $("personaReviewSave")?.addEventListener("click", updateCatalogStatus);
    $("personaSeal")?.addEventListener("click", sealProfile);
    $("assetSave")?.addEventListener("click", addAsset);
    $("backupExport")?.addEventListener("click", exportBackup);
    $("backupImport")?.addEventListener("change", e => e.target.files?.[0] && importBackup(e.target.files[0]));
    $("registryReset")?.addEventListener("click", resetDemo);
    $("ledgerRefresh")?.addEventListener("click", renderActivity);
    const nav = document.querySelector(".nav[aria-label='Studio navigation']");
    if (nav && !nav.querySelector("[data-view='ledger']")) {
      const b = node("button", "");
      b.dataset.view = "ledger";
      b.append(node("span", "ico", "◷"), document.createTextNode("Activity Ledger"));
      b.addEventListener("click", () => {
        document.querySelectorAll(".section-view").forEach(v => v.classList.toggle("active", v.id === "view-ledger"));
        document.querySelectorAll(".nav button").forEach(x => x.classList.toggle("active", x === b));
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
      nav.append(b);
    }
    render();
    const indicator = $("storageIndicator");
    if (indicator) indicator.textContent = "LOCAL DEMO DATA · browser storage only · not shared";
  });
})();