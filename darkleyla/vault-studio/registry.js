/* Dark Leyla Vault Studio — browser-local registry prototype.
 * Demo records only. No authentication, server authorization, remote storage,
 * privileged approvals, provider execution, or publication are implemented here.
 */
(() => {
  "use strict";
  const KEY = "dark-leyla-vault-registry:v2";
  const $ = id => document.getElementById(id);
  const now = () => new Date().toISOString();
  const uid = prefix => prefix + "_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  const STATUSES = ["TAGGED","PENDING_REVIEW","CONFIRMED","SEALED","REJECTED","ARCHIVED"];
  const emptyState = () => ({ schema: 1, profiles: [], skills: [], assets: [], activity: [] });
  let state = null;
  let activeProfileId = null;

  function validState(v) {
    if (!v || v.schema !== 1 || !["profiles","skills","assets","activity"].every(k => Array.isArray(v[k]))) return false;
    const unique = rows => new Set(rows.map(x => x?.id)).size === rows.length && rows.every(x => typeof x?.id === "string" && x.id.length > 0);
    if (![v.profiles,v.skills,v.assets,v.activity].every(unique)) return false;
    const profileIds = new Set(v.profiles.map(p => p.id));
    const skillIds = new Set(v.skills.map(s => s.id));
    for (const p of v.profiles) {
      if (typeof p.name !== "string" || !p.name.trim() || !STATUSES.includes(p.status) ||
          !Array.isArray(p.skills) || !Array.isArray(p.tags) || !Array.isArray(p.notes) ||
          !Array.isArray(p.images) || !Array.isArray(p.revisions || p.versions)) return false;
      if (p.skills.some(id => !skillIds.has(id))) return false;
      if (p.catalogFlag !== catalogFlagFor(p.status)) return false;
      if (p.images.some(i => typeof i.id !== "string" || typeof i.src !== "string" ||
          !(i.src.startsWith("data:image/") || /^https?:\/\//i.test(i.src)))) return false;
    }
    for (const a of v.assets) {
      if (!profileIds.has(a.profileId) || !["VAULT","PUBLIC_DERIVATIVE"].includes(a.visibility)) return false;
      if (a.imageId && !v.profiles.some(p => p.id === a.profileId && p.images.some(i => i.id === a.imageId))) return false;
    }
    return true;
  }
  function catalogFlagFor(status) {
    return ({TAGGED:"tagged_not_confirmed",PENDING_REVIEW:"pending_review",CONFIRMED:"catalog_confirmed",
      SEALED:"silk_sealed",REJECTED:"rejected",ARCHIVED:"archived"})[status] || "tagged_not_confirmed";
  }
  function canSeal(p) { return p.status === "CONFIRMED" && !p.archived; }
  function load() {
    if (state) return state;
    try {
      const raw = localStorage.getItem(KEY);
      const parsed = raw ? JSON.parse(raw) : null;
      state = validState(parsed) ? parsed : emptyState();
    } catch { state = emptyState(); }
    return state;
  }
  function toast(message) {
    const el = $("toast");
    if (!el) return;
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => el.classList.remove("show"), 2800);
  }
  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function record(next, action, detail, profileId) {
    next.activity.unshift({id:uid("act"),at:now(),profileId:profileId || undefined,action,detail});
    next.activity = next.activity.slice(0,500);
    try { localStorage.setItem(KEY, JSON.stringify(next)); }
    catch { toast("Browser storage is full. Export a backup or remove image records."); return false; }
    state = next;
    render();
    return true;
  }
  function setActiveProfile(p) {
    activeProfileId = p.id;
    $("personaName").value = p.name || "";
    $("personaCodename").value = p.codename || "";
    $("personaCategory").value = p.category || "AI Persona";
    $("personaRole").value = p.role || "Assistant persona";
    $("personaIdentity").value = p.identity || "";
    $("personaNotes").value = p.notesText || "";
    $("personaSkills").value = (p.skills || []).map(id => load().skills.find(s => s.id === id)?.name || "").filter(Boolean).join(", ");
    $("personaTags").value = (p.tags || []).join(", ");
    $("personaStatus").value = p.status || "TAGGED";
    renderProfiles();
    renderRevisions(p);
  }
  function saveProfile() {
    const name = $("personaName").value.trim();
    if (!name) return toast("A display name is required.");
    const skillNames = $("personaSkills").value.split(",").map(x => x.trim()).filter(Boolean);
    const next = JSON.parse(JSON.stringify(load()));
    const skillIds = skillNames.map(name => {
      let found = next.skills.find(s => s.name.toLowerCase() === name.toLowerCase());
      if (!found) {
        found = {id:uid("skill"),name,description:"Added from Persona Forge profile",category:"Uncategorized"};
        next.skills.push(found);
      }
      return found.id;
    });
    const data = {
      name, codename:$("personaCodename").value.trim(), category:$("personaCategory").value,
      role:$("personaRole").value, identity:$("personaIdentity").value.trim(),
      notesText:$("personaNotes").value.trim(), skills:skillIds,
      tags:$("personaTags").value.split(",").map(x=>x.trim().toLowerCase()).filter(Boolean)
    };
    const p = next.profiles.find(x => x.id === activeProfileId);
    if (!p) {
      const stamp = now(), id = uid("persona");
      const profile = {id,...data,faction:"",persona:name,lane:"VAULT",gate:"UNVERIFIED",status:"TAGGED",
        catalogFlag:catalogFlagFor("TAGGED"),archived:false,demo:true,notes:[],images:[],
        revisions:[{id:uid("rev"),label:"v1",summary:"Registry profile created",at:stamp}],
        versions:[{id:uid("rev"),label:"v1",summary:"Registry profile created",at:stamp}],
        createdAt:stamp,updatedAt:stamp};
      next.profiles.unshift(profile);
      activeProfileId = id;
      if (record(next,"PROFILE_CREATED","Persona registered: "+name,id)) toast("Persona saved to this browser's demo registry.");
      return;
    }
    const changed = ["name","codename","category","role","identity","notesText"].some(k=>p[k]!==data[k]) ||
      JSON.stringify(p.skills)!==JSON.stringify(data.skills) || JSON.stringify(p.tags)!==JSON.stringify(data.tags);
    if (!changed) return toast("No profile changes to save.");
    Object.assign(p,data,{updatedAt:now(),persona:name});
    p.revisions.unshift({id:uid("rev"),label:"v"+(p.revisions.length+1),summary:"Profile metadata revised",at:p.updatedAt});p.versions=p.revisions;
    if (record(next,"PROFILE_REVISED","Persona revised: "+name,p.id)) toast("New profile revision saved locally.");
  }
  function renderProfiles() {
    const target=$("personaRegistryList"); if(!target)return;
    target.replaceChildren();
    const q=($("personaSearch")?.value||"").trim().toLowerCase(), status=$("personaFilter")?.value||"ALL";
    const rows=load().profiles.filter(p=>{
      const skillNames=(p.skills||[]).map(id=>load().skills.find(s=>s.id===id)?.name||"");
      const hay=[p.name,p.codename,p.category,p.role,p.identity,p.notesText,...skillNames,...(p.tags||[])].join(" ").toLowerCase();
      return (!q||hay.includes(q))&&(status==="ALL"||p.status===status);
    });
    if(!rows.length){target.append(el("div","empty-state","No matching persona records. Create a profile above to begin."));return;}
    rows.forEach(p=>{
      const card=el("div","queue-item"), body=el("div"), icon=el("div","thumb","◉");
      body.append(el("strong","",p.name+(p.codename?" · "+p.codename:"")));
      body.append(el("small","",(p.category||"Persona")+" · "+(p.role||"Unassigned")+" · "+(p.revisions?.length||1)+" revisions"));
      const status=el("span","tag",p.archived?"ARCHIVED":p.status);
      const open=el("button","btn","Open"); open.type="button"; open.addEventListener("click",()=>setActiveProfile(p));
      card.append(icon,body,status,open); target.append(card);
    });
  }
  function renderRevisions(p) {
    const target=$("revisionList"); if(!target)return;
    target.replaceChildren();
    (p?.revisions||[]).forEach(r=>{
      const item=el("div","mini-card");
      item.append(el("strong","",r.label+" · "+r.summary),el("p","",new Date(r.at).toLocaleString()));
      target.append(item);
    });
    if(!p)target.append(el("p","micro","Select a persona to inspect its revisions."));
  }
  function reviewProfile() {
    const next=JSON.parse(JSON.stringify(load()));
    const p=next.profiles.find(x=>x.id===activeProfileId);
    if(!p)return toast("Select or save a persona first.");
    const status=$("personaStatus").value, note=$("personaReviewNote").value.trim();
    if(status==="SEALED")return toast("Use the separate catalog seal action after local confirmation.");
    if(!note)return toast("Add a review note before changing catalog status.");
    if(status==="CONFIRMED"&&!confirm("Mark CONFIRMED in this local demo catalog only? This is not identity, rights, consent, or production approval."))return;
    p.status=status;p.catalogFlag=catalogFlagFor(status);p.archived=status==="ARCHIVED";p.updatedAt=now();
    p.notes.unshift({id:uid("note"),text:"[Local review → "+status+"] "+note,at:p.updatedAt});
    $("personaReviewNote").value="";
    if(record(next,"CATALOG_REVIEW","Local catalog status set to "+status+": "+p.name,p.id))
      toast("Catalog status updated locally. No privileged approval was created.");
  }
  function sealProfile() {
    const next=JSON.parse(JSON.stringify(load()));
    const p=next.profiles.find(x=>x.id===activeProfileId);
    if(!p)return toast("Select a persona first.");
    if(!canSeal(p))return toast("Only CONFIRMED, non-archived profiles can receive a catalog seal.");
    if(!confirm("Apply a catalog-only seal? This does not authorize production, publication, rights, identity, or consent."))return;
    p.status="SEALED";p.catalogFlag=catalogFlagFor("SEALED");p.updatedAt=now();
    p.revisions.unshift({id:uid("rev"),label:"v"+(p.revisions.length+1),summary:"Catalog seal applied (non-authoritative)",at:p.updatedAt});p.versions=p.revisions;
    if(record(next,"CATALOG_SEALED","Catalog-only seal applied: "+p.name,p.id))
      toast("Catalog seal recorded. No production permission was granted.");
  }
  function addSkill() {
    const name=$("skillName").value.trim(); if(!name)return toast("Skill name is required.");
    const next=JSON.parse(JSON.stringify(load()));
    if(next.skills.some(s=>s.name.toLowerCase()===name.toLowerCase()))return toast("That skill already exists.");
    const skill={id:uid("skill"),name,category:$("skillCategory").value,description:$("skillDescription").value.trim()};
    next.skills.push(skill);
    if(record(next,"SKILL_CREATED","Skill created: "+name)){$("skillName").value="";$("skillDescription").value="";toast("Skill added to local Skill Forge.");}
  }
  function renderSkills() {
    const target=$("skillRegistryList");if(!target)return;
    target.replaceChildren();
    if(!load().skills.length){target.append(el("div","empty-state","No skills registered. Add reusable skills for Persona Forge profiles."));return;}
    load().skills.forEach(s=>{
      const card=el("div","queue-item"),body=el("div");
      body.append(el("strong","",s.name),el("small","",(s.category||"Uncategorized")+" · "+(s.description||"No description")));
      card.append(el("div","thumb","✧"),body,el("span","tag","SKILL"));target.append(card);
    });
  }
  function addAsset() {
    const title=$("assetTitle").value.trim(),profileId=$("assetProfile").value,file=$("assetImage").files?.[0];
    if(!title||!profileId)return toast("Choose a persona and enter an asset title.");
    if(file && (!/^image\/(png|jpeg|webp|gif)$/i.test(file.type)||file.size>1200000))
      return toast("Use a PNG, JPEG, WebP, or GIF image up to 1.2 MB.");
    const finish = imageData => {
      const next=JSON.parse(JSON.stringify(load())),profile=next.profiles.find(p=>p.id===profileId);
      if(!profile)return toast("The selected persona no longer exists.");
      let imageId;
      if(imageData){imageId=uid("image");profile.images.unshift({id:imageId,src:imageData,caption:title,kind:"upload"});}
      const asset={id:uid("asset"),profileId,title,type:$("assetType").value,version:$("assetVersion").value.trim()||"v1",
        visibility:$("assetVisibility").value,imageId,sourceUrl:$("assetSource").value.trim(),createdAt:now()};
      next.assets.unshift(asset);
      if(record(next,"ASSET_REGISTERED","Asset metadata registered: "+title,profileId)){
        $("assetTitle").value="";$("assetVersion").value="v1";$("assetSource").value="";$("assetImage").value="";
        toast(imageData?"Asset and image saved in this browser.":"Asset metadata saved locally; no file uploaded.");
      }
    };
    if(file){const reader=new FileReader();reader.onload=()=>finish(String(reader.result||""));reader.onerror=()=>toast("Image could not be read.");reader.readAsDataURL(file);}
    else finish(null);
  }
  function renderAssets() {
    const target=$("assetRegistryList");if(!target)return;
    target.replaceChildren();
    const profiles=load().profiles;
    const select=$("assetProfile"),current=select.value;
    select.replaceChildren(new Option(profiles.length?"Select persona":"Create a persona first",""));
    profiles.forEach(p=>select.append(new Option(p.name,p.id)));
    if(profiles.some(p=>p.id===current))select.value=current;
    if(!load().assets.length){target.append(el("div","empty-state","No asset records have been registered."));return;}
    load().assets.forEach(a=>{
      const p=profiles.find(x=>x.id===a.profileId),img=p?.images?.find(x=>x.id===a.imageId);
      const card=el("div","queue-item");
      if(img){const image=document.createElement("img");image.src=img.src;image.alt=a.title;image.loading="lazy";image.style.cssText="width:54px;height:54px;object-fit:cover;border-radius:8px;border:1px solid var(--line)";card.append(image);}
      else card.append(el("div","thumb","▣"));
      const body=el("div");body.append(el("strong","",a.title),el("small","",(p?.name||"Unknown persona")+" · "+a.type+" · "+a.version));
      card.append(body,el("span","tag",a.visibility));
      if(a.sourceUrl&&/^https:\/\//i.test(a.sourceUrl)){const link=el("a","btn","Source");link.href=a.sourceUrl;link.target="_blank";link.rel="noopener noreferrer";card.append(link);}
      target.append(card);
    });
  }
  function renderActivity() {
    const target=$("activityList");if(!target)return;target.replaceChildren();
    if(!load().activity.length){target.append(el("div","empty-state","No activity yet. Registry actions will be recorded in this browser only."));return;}
    load().activity.forEach(a=>{
      const item=el("div","queue-item"),body=el("div");
      body.append(el("strong","",a.action),el("small","",new Date(a.at).toLocaleString()+" · "+a.detail));
      item.append(el("div","thumb","◷"),body);target.append(item);
    });
  }
  function renderStats() {
    $("statProfiles")&&($("statProfiles").textContent=String(load().profiles.length));
    $("statAssets")&&($("statAssets").textContent=String(load().assets.length));
    $("statPending")&&($("statPending").textContent=String(load().profiles.filter(p=>p.status==="PENDING_REVIEW").length));
  }
  function render() {
    renderProfiles();renderRevisions(load().profiles.find(p=>p.id===activeProfileId));
    renderSkills();renderAssets();renderActivity();renderStats();
  }
  function exportBackup() {
    const blob=new Blob([JSON.stringify(load(),null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download="dark-leyla-vault-demo-backup.json";a.click();URL.revokeObjectURL(url);
    toast("Local JSON backup exported. Protect this file; it is not encrypted.");
  }
  function importBackup(file) {
    const reader=new FileReader();
    reader.onload=()=>{
      try{
        const parsed=JSON.parse(String(reader.result||""));
        if(!parsed||parsed.schema!==1||!Array.isArray(parsed.profiles)||!Array.isArray(parsed.skills)||!Array.isArray(parsed.assets)||!Array.isArray(parsed.activity))throw new Error("Backup schema is not supported.");
        parsed.profiles=parsed.profiles.map(p=>({...p,identity:p.identity||"",notesText:p.notesText||p.notes?.[0]?.text||"",revisions:p.revisions||p.versions||[],versions:p.versions||p.revisions||[]}));
        if(!validState(parsed))throw new Error("Backup failed schema, reference, or status validation.");
        state=parsed;activeProfileId=null;
        if(record(state,"BACKUP_IMPORTED","JSON backup imported into local demo storage."))toast("Backup imported to this browser only.");
      }catch(e){toast("Import rejected: "+(e?.message||"invalid backup"));}
    };
    reader.onerror=()=>toast("Backup file could not be read.");
    reader.readAsText(file);
  }
  function resetDemo() {
    if(!confirm("Clear this browser's Dark Leyla demo registry? Export a backup first if needed."))return;
    state=emptyState();activeProfileId=null;
    try{localStorage.removeItem(KEY);render();toast("Local demo registry cleared.");}
    catch{toast("Could not clear browser storage.");}
  }
  document.addEventListener("DOMContentLoaded",()=>{
    $("personaSave")?.addEventListener("click",saveProfile);
    $("personaSearch")?.addEventListener("input",renderProfiles);
    $("personaFilter")?.addEventListener("change",renderProfiles);
    $("personaReviewSave")?.addEventListener("click",reviewProfile);
    $("personaSeal")?.addEventListener("click",sealProfile);
    $("skillSave")?.addEventListener("click",addSkill);
    $("assetSave")?.addEventListener("click",addAsset);
    $("backupExport")?.addEventListener("click",exportBackup);
    $("backupImport")?.addEventListener("change",e=>e.target.files?.[0]&&importBackup(e.target.files[0]));
    $("registryReset")?.addEventListener("click",resetDemo);
    $("ledgerRefresh")?.addEventListener("click",renderActivity);
    const nav=document.querySelector(".nav[aria-label='Studio navigation']");
    if(nav&&!nav.querySelector("[data-view='ledger']")){
      const b=el("button","");b.dataset.view="ledger";b.append(el("span","ico","◷"),document.createTextNode("Activity Ledger"));
      b.addEventListener("click",()=>{document.querySelectorAll(".section-view").forEach(v=>v.classList.toggle("active",v.id==="view-ledger"));document.querySelectorAll(".nav button").forEach(x=>x.classList.toggle("active",x===b));window.scrollTo({top:0,behavior:"smooth"});});nav.append(b);
    }
    const skillNav=document.querySelector(".nav[aria-label='Studio navigation']");
    if(skillNav&&!skillNav.querySelector("[data-view='skills']")){
      const b=el("button","");b.dataset.view="skills";b.append(el("span","ico","✧"),document.createTextNode("Skill Forge"));
      b.addEventListener("click",()=>{document.querySelectorAll(".section-view").forEach(v=>v.classList.toggle("active",v.id==="view-skills"));document.querySelectorAll(".nav button").forEach(x=>x.classList.toggle("active",x===b));window.scrollTo({top:0,behavior:"smooth"});});skillNav.append(b);
    }
    render();
    if($("storageIndicator"))$("storageIndicator").textContent="Local demo state only · LOCAL DEMO DATA · browser storage only · not shared";
  });
})();