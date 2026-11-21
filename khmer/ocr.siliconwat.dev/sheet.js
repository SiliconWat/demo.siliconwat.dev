// The Khmer review page (/khmer-review). Reads this site's words (sheet.json) and what the native readers have entered
// (translate.333.eco), shows each entry, and — with a reviewer's private link (#k=…) — saves a press as a new row.
// ⛔ Every stored text is rendered as TEXT (textContent), never HTML. ⛔ The link's token stays in the fragment and in memory.
import { flatten, placeholderGap, stateOf } from "./logic.js";

const meta = (n) => document.querySelector(`meta[name="${n}"]`)?.content ?? "";
const API = meta("translate-api").replace(/\/$/, "");
const SITE = meta("translate-site");
const TOKEN = (location.hash.match(/[#&]k=([A-Za-z0-9_-]{20,200})/) ?? [])[1] ?? null;

// Our draft Khmer for the page's own words (marked as a draft in the footer).
const T = {
  approve: ["ត្រឹមត្រូវហើយ", "Right as drafted"],
  correct: ["កែតម្រូវ", "Correct it"],
  ask: ["សួរសំណួរ", "Ask a question"],
  save: ["រក្សាទុក", "Save"],
  cancel: ["បោះបង់", "Cancel"],
  todo: ["មិនទាន់បានពិនិត្យ", "Not yet reviewed"],
  approved: ["ត្រឹមត្រូវហើយ", "Right as drafted"],
  corrected: ["បានកែតម្រូវ", "Corrected"],
  draft: ["សេចក្តីព្រាងរបស់យើង", "Our draft"],
  noKhmer: ["មិនទាន់មានភាសាខ្មែរ", "No Khmer yet"],
  khmerOnly: ["(បង្ហាញតែជាភាសាខ្មែរ)", "(shown in Khmer only)"],
  questions: ["សំណួរ", "Questions"],
  englishChanged: ["អត្ថបទអង់គ្លេសបានផ្លាស់ប្តូរ ក្រោយការពិនិត្យនេះ។ សូមមើលម្តងទៀត។", "The English changed after this review. Please look again."],
  draftChanged: ["សេចក្តីព្រាងរបស់យើងបានផ្លាស់ប្តូរ ក្រោយពេលអ្នកយល់ព្រម។ សូមមើលម្តងទៀត។", "Our draft changed after it was approved. Please look again."],
  keep: ["សូមរក្សា {x} ទុកដដែល។ ទំព័រនឹងបំពេញវាដោយខ្លួនឯង។", "Keep {x} as it is: the page fills it in."],
  again: ["ចុច «រក្សាទុក» ម្តងទៀត ដើម្បីរក្សាទុកតាមដែលបានសរសេរ។", "Press Save again to keep it as written."],
  saved: ["បានរក្សាទុក", "Saved"],
  notSaved: ["មិនទាន់បានរក្សាទុកទេ។ សូមពិនិត្យការតភ្ជាប់ ហើយចុច «រក្សាទុក» ម្តងទៀត។", "Not saved. Check the connection and press Save again."],
  linkGone: ["តំណនេះលែងដំណើរការហើយ។ សូមសុំតំណថ្មី។", "This link no longer works. Please ask for a new one."],
  tooMany: ["ថ្ងៃនេះបានរក្សាទុកច្រើនហើយ។ សូមបន្តនៅថ្ងៃស្អែក។", "That is a full day's entries. Please continue tomorrow."],
  writer: ["តំណរបស់អ្នកដំណើរការ។ អ្វីដែលអ្នករក្សាទុកនឹងនៅជាប់ ហើយមិនត្រូវបានលុបទេ។", "Your review link works. What you save is kept, and nothing is erased."],
  viewOnly: ["សម្រាប់មើលតែប៉ុណ្ណោះ។ អ្នកពិនិត្យបើកទំព័រនេះពីតំណផ្ទាល់ខ្លួនរបស់ពួកគេ។", "View only. Reviewers open this page from their own link."],
  badLink: ["តំណនេះមិនដំណើរការទេ (ត្រូវបានបិទ ឬវាយខុស)។ ទំព័រនេះសម្រាប់មើលតែប៉ុណ្ណោះ។", "This link does not work (cancelled or mistyped). The page is view only."],
  offline: ["មិនអាចភ្ជាប់ទៅកន្លែងរក្សាទុកបានទេ។ កំពុងបង្ហាញតែសេចក្តីព្រាងរបស់យើង ហើយមិនអាចរក្សាទុកបានទេ។", "The store could not be reached. Showing our drafts only; nothing can be saved."],
  show: ["បង្ហាញ", "Show"],
  all: ["ទាំងអស់", "All"],
  progress: ["បានពិនិត្យ {a} ក្នុងចំណោម {b}", "{a} of {b} reviewed"],
  working: ["កំពុងរក្សាទុក", "Saving"],
  yourKhmer: ["ភាសាខ្មែររបស់អ្នក", "Your Khmer"],
  yourQuestion: ["សំណួររបស់អ្នក", "Your question"],
};

const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") e.className = v; else if (k === "text") e.textContent = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k !== null && k !== undefined && k !== false) e.append(k);
  return e;
};
/** a label in both languages: Khmer first (the reviewers'), English beneath */
const bi = ([km, en], vars = {}) => {
  const fill = (s) => s.replace(/\{(\w)\}/g, (_, k) => vars[k] ?? `{${k}}`);
  return el("span", { class: "bi" }, el("span", { lang: "km", text: fill(km) }), el("span", { class: "en", lang: "en", text: fill(en) }));
};
/** a text with its {placeholders} marked, as text nodes only */
const marked = (s, lang) => {
  const span = el("span", { lang });
  for (const part of String(s).split(/(\{\w+\})/)) span.append(/^\{\w+\}$/.test(part) ? el("span", { class: "ph", text: part }) : document.createTextNode(part));
  return span;
};
const day = (ms) => { const d = new Date(ms); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; };

let sheet, entries, rows = [], role = null, store = true, filter = "all", open = null;

function counts() {
  const done = entries.filter((e) => stateOf(e, rows).status !== "todo").length;
  return { done, all: entries.length };
}

function header() {
  const bar = document.getElementById("status");
  bar.replaceChildren();
  const msg = !store ? T.offline : role ? T.writer : TOKEN ? T.badLink : T.viewOnly;
  bar.append(el("p", { class: `banner ${!store || (TOKEN && !role) ? "warn" : role ? "ok" : ""}` }, bi(msg)));
  const { done, all } = counts();
  const todo = all - done;
  bar.append(el("div", { class: "tools" },
    el("p", { class: "progress" }, bi(T.progress, { a: String(done), b: String(all) })),
    el("div", { class: "filter", role: "group", "aria-label": "Show" },
      el("button", { type: "button", "aria-pressed": String(filter === "all"), onclick: () => { filter = "all"; render(); } }, bi([`${T.all[0]} (${all})`, `${T.all[1]} (${all})`])),
      el("button", { type: "button", "aria-pressed": String(filter === "todo"), onclick: () => { filter = "todo"; render(); } }, bi([`${T.todo[0]} (${todo})`, `${T.todo[1]} (${todo})`])))));
}

function card(e) {
  const s = stateOf(e, rows);
  const art = el("article", { class: `card ${s.status}${e.waiting ? " long" : ""}`, id: "e-" + e.key, "data-key": e.key });
  art.append(el("div", { class: "head" },
    el("span", { class: "n", text: String(e.n) }),
    el("span", { class: "badge" }, bi(T[s.status])),
    s.latest ? el("span", { class: "when", text: day(s.latest.at) }) : null,
    el("code", { class: "key", text: e.key })));
  art.append(el("div", { class: "en" }, e.en ? marked(e.en, "en") : bi(T.khmerOnly)));
  art.append(el("div", { class: "km" }, s.khmer ? marked(s.khmer, "km") : el("span", { class: "none" }, bi(T.noKhmer))));
  if (s.latest && e.km && s.khmer !== e.km) {
    art.append(el("details", { class: "draft" }, el("summary", {}, bi(T.draft)), el("div", {}, marked(e.km, "km"))));
  }
  if (s.englishChanged) art.append(el("p", { class: "flag" }, bi(T.englishChanged)));
  if (s.draftChanged) art.append(el("p", { class: "flag" }, bi(T.draftChanged)));
  if (s.notes.length) {
    art.append(el("div", { class: "notes" }, el("p", { class: "label" }, bi(T.questions)),
      el("ul", {}, s.notes.map((nt) => el("li", {}, el("span", { class: "when", text: day(nt.at) + " " }), el("span", { text: nt.note }))))));
  }
  if (role && store) {
    if (open?.key === e.key) art.append(editor(e, s));
    else {
      const acts = el("div", { class: "acts" });
      // "right as drafted" approves our draft word for word; it is offered while our draft is what the page would show
      const current = s.status === "approved" && !s.draftChanged && !s.englishChanged;
      if (e.km && !current) acts.append(el("button", { type: "button", class: "primary", onclick: (ev) => save(e, { kind: "approve", km: e.km }, ev.currentTarget) }, bi(T.approve)));
      acts.append(el("button", { type: "button", onclick: () => { open = { key: e.key, kind: "text" }; render(e.key); } }, bi(T.correct)));
      acts.append(el("button", { type: "button", onclick: () => { open = { key: e.key, kind: "note" }; render(e.key); } }, bi(T.ask)));
      art.append(acts);
    }
  }
  if (!s.latest) art.append(el("div", { class: "paper", "aria-hidden": "true" }));   // print only: room for a handwritten correction
  return art;
}

function editor(e, s) {
  const isNote = open.kind === "note";
  const id = "ed-" + e.key;
  const box = el("textarea", { id, lang: isNote ? null : "km", rows: e.waiting ? "8" : "3", class: isNote ? "" : "kmbox" });
  box.value = isNote ? "" : (s.khmer ?? "");
  const msg = el("p", { class: "msg", role: "status" });
  let warned = null;
  const saveBtn = el("button", { type: "submit", class: "primary" }, bi(T.save));
  const form = el("form", { class: "editor", onsubmit: (ev) => {
    ev.preventDefault();
    const v = box.value;
    if (!v.trim()) { box.focus(); return; }
    if (!isNote) {
      const gap = placeholderGap(e, v);
      const key = gap.missing.concat(gap.extra).join(" ");
      if (key && warned !== key) {
        warned = key;
        msg.replaceChildren(bi(T.keep, { x: key }), el("br"), bi(T.again));
        return;
      }
    }
    save(e, isNote ? { kind: "note", note: v } : { kind: "text", km: v }, saveBtn, msg);
  } },
  el("label", { for: id }, bi(isNote ? T.yourQuestion : T.yourKhmer)), box, msg,
  el("div", { class: "acts" }, saveBtn, el("button", { type: "button", onclick: () => { open = null; render(e.key); } }, bi(T.cancel))));
  queueMicrotask(() => box.focus());
  return form;
}

async function save(e, row, btn, msg) {
  if (btn.disabled) return;
  const width = btn.offsetWidth;
  btn.disabled = true; btn.setAttribute("aria-busy", "true"); btn.style.minWidth = width + "px";
  const label = [...btn.childNodes];
  btn.replaceChildren(el("span", { class: "dots", "aria-hidden": "true" }, el("i"), el("i"), el("i")), el("span", { class: "sr" }, bi(T.working)));
  const restore = () => { btn.replaceChildren(...label); btn.disabled = false; btn.removeAttribute("aria-busy"); };
  const tell = (t) => { const m = msg ?? btn.closest("article")?.querySelector(".msg") ?? btn.closest("article")?.appendChild(el("p", { class: "msg", role: "status" })); m?.replaceChildren(bi(t)); };
  try {
    const r = await fetch(`${API}/v1/surfaces/${encodeURIComponent(SITE)}/entries`, {
      method: "POST", headers: { authorization: "Bearer " + TOKEN, "content-type": "application/json" },
      body: JSON.stringify({ entries: [{ key: e.key, base_en: e.en, base_km: e.km ?? null, ...row }] }),
    });
    if (r.status === 201) {
      const { saved } = await r.json();
      rows.push({ id: saved[0].id, at: saved[0].at, key: e.key, base_en: e.en, base_km: e.km ?? null, km: null, note: null, ...row });
      open = null;
      render(e.key, T.saved);
      return;
    }
    restore();
    tell(r.status === 401 ? T.linkGone : r.status === 429 ? T.tooMany : T.notSaved);
  } catch {
    restore();
    tell(T.notSaved);
  }
}

function render(focusKey, note) {
  header();
  const list = document.getElementById("list");
  const keepY = focusKey ? document.getElementById("e-" + focusKey)?.getBoundingClientRect().top : null;
  list.replaceChildren();
  let group = null, section = null;
  for (const e of entries) {
    if (filter === "todo" && stateOf(e, rows).status !== "todo" && e.key !== focusKey) continue;
    if (e.group !== group) {
      group = e.group;
      section = el("section", {}, el("h2", { text: group }));
      list.append(section);
    }
    section.append(card(e));
  }
  if (focusKey) {
    const c = document.getElementById("e-" + focusKey);
    if (c && keepY !== null && keepY !== undefined) window.scrollBy(0, c.getBoundingClientRect().top - keepY);
    if (c && note) c.append(el("p", { class: "msg done", role: "status" }, bi(note)));
  }
}

async function main() {
  try {
    sheet = await (await fetch("sheet.json", { cache: "no-cache" })).json();
  } catch {
    document.getElementById("list").textContent = "sheet.json could not be read.";
    return;
  }
  if (/^#[0-9a-f]{6}$/i.test(sheet.accent ?? "")) document.documentElement.style.setProperty("--accent", sheet.accent);
  entries = flatten(sheet);
  const [got, me] = await Promise.all([
    fetch(`${API}/v1/surfaces/${encodeURIComponent(SITE)}/entries`, { cache: "no-store" }).then((r) => (r.ok ? r.json() : Promise.reject())).catch(() => null),
    TOKEN ? fetch(`${API}/v1/me`, { headers: { authorization: "Bearer " + TOKEN }, cache: "no-store" }).then((r) => (r.ok ? r.json() : null)).catch(() => null) : null,
  ]);
  if (got) rows = got.entries; else store = false;
  role = me?.role ?? null;
  render();
}
main();
