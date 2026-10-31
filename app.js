// Pocket Rust — lessons, tap-to-answer problems, review of missed problems, GitHub sync.
// Views are routed on the hash: "" home, "#lesson-<id>", "#review", "#sync".
(() => {
  "use strict";
  const PROGRESS_KEY = "pocket-rust:progress";
  const SYNC_KEY = "pocket-rust:sync";
  const WONT = "won't compile";
  const app = document.getElementById("app");

  // ───────── storage (every access guarded: private windows and previews can refuse it) ─────────
  const ls = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* not available */ } },
    del(k) { try { localStorage.removeItem(k); } catch { /* not available */ } },
  };
  const blank = () => ({ v: 1, lessons: {}, missed: {}, updated: 0 });
  let progress = Object.assign(blank(), ls.get(PROGRESS_KEY) || {});
  function save() { progress.updated = Date.now(); ls.set(PROGRESS_KEY, progress); Sync.soon(); }

  // ───────── course ─────────
  let COURSE = null;
  const problemById = {};
  const lessonOf = {};

  // ───────── helpers ─────────
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const KW = new Set("fn let mut match for in if else return struct impl use pub ref static const move loop while break trait Self self enum as".split(" "));
  const TY = new Set("char u8 i32 u32 f64 usize String str bool Vec Option Result Some None Ok Err".split(" "));
  function hl(src) {
    const ci = src.indexOf("//");
    const code = ci >= 0 ? src.slice(0, ci) : src, cm = ci >= 0 ? src.slice(ci) : "";
    const out = code.replace(/("(?:[^"\\]|\\.)*"|'[^']'|\b\d[\d_.]*\b|\b[a-z_]+!|\b[A-Za-z_]\w*\b|[^\w"']+)/g, t => {
      const e = esc(t);
      if (t[0] === '"') return `<span class="tk-s">${e}</span>`;
      if (/^\d/.test(t)) return `<span class="tk-n">${e}</span>`;
      if (/!$/.test(t)) return `<span class="tk-m">${e}</span>`;
      if (KW.has(t)) return `<span class="tk-k">${e}</span>`;
      if (TY.has(t)) return `<span class="tk-t">${e}</span>`;
      return e;
    });
    return out + (cm ? `<span class="cm">${esc(cm)}</span>` : "");
  }
  const codeBlock = lines => `<div class="code">` + lines.map((l, n) => `<div class="ln"><span class="no">${n + 1}</span><span>${hl(l)}</span></div>`).join("") + `</div>`;
  const words = s => s.split(" ").map((w, i) => `<span class="w" style="--w:${i}">${esc(w)}</span>`).join(" ");
  const shuffle = a => a.map(v => [Math.random(), v]).sort((x, y) => x[0] - y[0]).map(v => v[1]);
  const rustc = text => esc(text).replace(/^(error(\[E\d+\])?)/m, '<span class="e">$1</span>').replace(/^(help|note)(:)/gm, '<span class="h">$1</span>$2');
  function animate(el) {
    el.classList.remove("enter");
    [...el.children].forEach((c, i) => c.style.setProperty("--i", i));
    void el.offsetWidth;
    el.classList.add("enter");
  }
  const ago = t => { const s = Math.round((Date.now() - t) / 1000); return s < 60 ? "just now" : s < 3600 ? `${Math.round(s / 60)} min ago` : s < 86400 ? `${Math.round(s / 3600)} h ago` : `${Math.round(s / 86400)} d ago`; };

  // ───────── progress rules ─────────
  const missedOn = () => Object.entries(progress.missed).filter(([id, m]) => m.on && problemById[id]).sort((a, b) => a[1].t - b[1].t).map(([id]) => id);
  function markMissed(id) { progress.missed[id] = { on: true, t: Date.now() }; save(); }
  function clearMissed(id) { if (progress.missed[id]?.on) { progress.missed[id] = { on: false, t: Date.now() }; save(); } }
  const nextLesson = () => COURSE.lessons.find(l => !progress.lessons[l.id]) || null;

  // ───────── home ─────────
  function home() {
    const done = COURSE.lessons.filter(l => progress.lessons[l.id]).length;
    const nl = nextLesson();
    const miss = missedOn().length;
    const sync = Sync.state();
    app.innerHTML = `<main class="home">
      <header class="home-top">
        <div class="brand"><h1>Pocket <span>Rust</span></h1>
          <button class="btn plain small sync-btn" type="button" data-go="#sync"><i class="dot ${sync.dot}"></i>Sync</button></div>
        <p class="lede"><b>${done} of ${COURSE.lessons.length}</b> lessons done${miss ? ` · <b>${miss}</b> to review` : ""}</p>
        <div class="track" aria-hidden="true"><i style="width:${(done / COURSE.lessons.length) * 100}%"></i></div>
      </header>
      ${nl ? `<section class="chunk up">
          <span class="tag lemon">Up next · Lesson ${nl.n}</span>
          <h2>${esc(nl.title)}</h2><p>${nl.summary}</p>
          <button class="btn go" type="button" data-go="#lesson-${nl.id}">Start lesson</button></section>`
        : `<section class="chunk up"><span class="tag">Course complete</span><h2>You finished all ${COURSE.lessons.length} lessons.</h2>
          <p>Replay any lesson below, or review what you missed.</p></section>`}
      ${miss ? `<button class="chunk review" type="button" data-go="#review"><span class="big">${miss}</span>
          <div><b>Review</b><span>Problems you got wrong, ready for another go.</span></div><span class="tag white">Go</span></button>` : ""}
      <h2 class="sec">All lessons</h2>
      <ol class="lessons">${COURSE.lessons.map(l => {
        const p = progress.lessons[l.id];
        const cls = p ? "done" : l === nl ? "next" : "";
        const state = p ? `<span class="state done">${p.right}/${p.total}</span>` : l === nl ? `<span class="state next">Next</span>` : `<span class="state new">New</span>`;
        return `<li><button class="chunk lesson-row ${cls}" type="button" data-go="#lesson-${l.id}">
          <span class="num">${l.n}</span><span><b>${esc(l.title)}</b><span class="sum">${l.summary}</span></span>${state}</button></li>`;
      }).join("")}</ol>
      <p class="foot-note">Every problem is checked against the real Rust compiler (${esc(COURSE.rustc || "rustc")}).</p>
    </main>`;
    animate(app.firstElementChild);
  }

  // ───────── player (lesson or review) ─────────
  function player(mode, lesson) {
    // steps: {type:"card", card} | {type:"problem", p, review:bool} | {type:"done"}
    const steps = [];
    let reviewIds = [];
    if (mode === "lesson") {
      lesson.cards.forEach(card => steps.push({ type: "card", card }));
      const earlier = missedOn().filter(id => lessonOf[id].n < lesson.n).slice(0, 2);
      reviewIds = earlier;
      lesson.problems.forEach((p, i) => {
        steps.push({ type: "problem", p, review: false });
        if ((i === 1 || i === 3) && earlier.length) steps.push({ type: "problem", p: problemById[earlier.shift()], review: true });
      });
      earlier.forEach(id => steps.push({ type: "problem", p: problemById[id], review: true }));
    } else {
      reviewIds = missedOn().slice(0, 8);
      reviewIds.forEach(id => steps.push({ type: "problem", p: problemById[id], review: true }));
    }
    steps.push({ type: "done" });

    let cur = 0, just = null, tapped = null;
    const st = steps.map(s => s.type === "problem" ? fresh(s.p) : null);
    const tally = { right: 0, total: 0, cleared: 0 };

    app.innerHTML = `<div class="player">
      <div class="ptop"><button class="close" type="button" aria-label="Close and go home">✕</button>
        <div class="track" aria-hidden="true"><i></i></div><span class="count"></span></div>
      <div class="pbody" aria-live="polite"></div>
      <div class="pfoot"><button class="btn plain back" type="button">Back</button><button class="btn go" type="button">Next</button></div>
    </div>`;
    const $ = s => app.querySelector(s);
    const body = $(".pbody"), go = $(".go"), back = $(".back"), bar = $(".track i"), count = $(".count");
    $(".close").addEventListener("click", () => { location.hash = ""; });

    function fresh(p) {
      if (p.type === "fill" || p.type === "output") return { fill: p.answer.map(() => null), bank: shuffle(p.bank), done: false, tries: 0 };
      if (p.type === "order") return { seq: [], pool: shuffle(p.pool.map((t, k) => ({ t, k }))), done: false, tries: 0 };
      return { pick: null, done: false, tries: 0 };
    }

    function render(motion) {
      const step = steps[cur];
      const nCards = steps.filter(s => s.type === "card").length;
      const probs = steps.filter(s => s.type === "problem");
      bar.style.width = `${(cur / (steps.length - 1)) * 100}%`;
      if (step.type === "card") count.textContent = `Card ${cur + 1}/${nCards}`;
      else if (step.type === "problem") count.textContent = `${probs.indexOf(step) + 1}/${probs.length}`;
      else count.textContent = "Done";
      back.hidden = !(step.type === "card" && cur > 0);
      let h = "";

      if (step.type === "card") {
        const c = step.card;
        h = `<span class="tag">Lesson ${lesson.n} · ${esc(lesson.title)}</span>
          <h2 class="headline">${words(c.h)}</h2>
          <p class="copy">${c.p}</p>${codeBlock(c.code)}${c.note ? `<p class="note">${c.note}</p>` : ""}
          <div class="dots" aria-hidden="true">${steps.filter(s => s.type === "card").map((_, i) => `<i class="${i === cur ? "on" : ""}"></i>`).join("")}</div>`;
        go.disabled = false;
        go.textContent = cur < nCards - 1 ? "Next" : "Start problems";
      } else if (step.type === "done") {
        h = doneView();
        go.disabled = false;
        go.textContent = mode === "lesson" && nextAfter() ? "Next lesson" : "Home";
      } else {
        h = problemView(step, st[cur], motion);
        const s = st[cur], p = step.p;
        const ready = s.fill ? s.fill.every(Boolean) : s.seq ? s.seq.length === p.pool.length : s.pick !== null;
        go.disabled = !(s.done || ready);
        go.textContent = s.done ? (s.ok ? "Continue" : "Try again") : "Check";
      }
      body.innerHTML = h;
      body.dataset.problem = step.type === "problem" ? step.p.id : "";
      just = null; tapped = null;
      if (motion === "step") { body.scrollTop = 0; animate(body); } else body.classList.remove("enter");
      if (motion === "fb") { const f = body.querySelector(".fb"); if (f) setTimeout(() => f.scrollIntoView({ block: "nearest", behavior: "smooth" }), 80); }
    }

    function problemView(step, s, motion) {
      const p = step.p;
      const label = { fill: "Fill the gap", error: "Find the error", output: "Predict the output", order: "Order the lines" }[p.type];
      const from = lessonOf[p.id];
      let h = step.review ? `<span class="tag lemon">Review · Lesson ${from.n}</span>` : `<span class="tag">${label}</span>`;
      h += `<p class="prompt">${words(step.review ? `${label}: ${p.prompt}` : p.prompt)}</p>`;
      const locked = s.done && s.ok;
      const slot = k => {
        const v = s.fill[k];
        return `<button type="button" class="slot ${v ? "filled" : ""} ${just === "s" + k ? "just" : ""}" data-slot="${k}" aria-label="Gap ${k + 1}${v ? ": " + esc(v) : ", empty"}">${v ? esc(v) : "&nbsp;"}</button>`;
      };
      const bank = () => `<div class="bank">` + s.bank.map(b => `<button type="button" class="chip ${tapped === "c" + b ? "boing" : ""}" data-chip="${esc(b)}" ${locked ? "disabled" : ""}>${esc(b)}</button>`).join("") + `</div>`;
      if (p.type === "fill") {
        let gap = 0;
        h += `<div class="code">` + p.lines.map((l, n) => {
          const parts = l.split("__");
          const inner = parts.map((part, j) => hl(part) + (j < parts.length - 1 ? slot(gap++) : "")).join("");
          return `<div class="ln"><span class="no">${n + 1}</span><span>${inner}</span></div>`;
        }).join("") + `</div>` + bank();
      } else if (p.type === "output") {
        h += codeBlock(p.lines) + `<div class="out"><span class="lbl">Printed</span>` + p.answer.map((_, k) => `<div>${slot(k)}</div>`).join("") + `</div>` + bank();
      } else if (p.type === "error") {
        h += `<div class="code">` + p.lines.map((l, n) => {
          const cls = s.pick === n ? (locked ? "ok" : "sel") : "";
          return `<button type="button" class="ln ${cls}" data-line="${n}" aria-pressed="${s.pick === n}"><span class="no">${n + 1}</span><span>${hl(l)}</span></button>`;
        }).join("") + `</div>`;
      } else if (p.type === "order") {
        h += `<div class="code">` + p.head.map(l => `<div class="ln"><span>${hl(l)}</span></div>`).join("") +
          `<div class="answer">` + s.seq.map((it, j) => `<button type="button" class="chip line ${just === "q" + j ? "just" : ""}" data-seq="${j}">${hl(it.t)}</button>`).join("") + `</div>` +
          p.tail.map(l => `<div class="ln"><span>${hl(l)}</span></div>`).join("") + `</div>`;
        h += `<div class="bank lines">` + s.pool.map((it, j) => `<button type="button" class="chip line" data-pool="${j}">${hl(it.t)}</button>`).join("") + `</div>`;
      }
      if (s.done) {
        const showRustc = p.rustc && (s.ok || p.type !== "error");
        h += `<div class="fb ${s.ok ? "good" : "bad"} ${motion === "fb" ? "pop" : ""}"><div><b>${s.ok ? "Right." : "Not quite."}</b> ${s.ok ? p.good : p.bad}</div>${showRustc && s.ok ? `<div class="rustc">${rustc(p.rustc)}</div>` : ""}</div>`;
      }
      return h;
    }

    function nextAfter() { return mode === "lesson" ? COURSE.lessons[lesson.n] || null : null; }

    function doneView() {
      if (mode === "review") {
        const left = missedOn().length;
        return `<span class="tag">Review done</span><h2 class="headline">${words("Nice work going back over these.")}</h2>
          <div class="score">${tally.cleared}<small> / ${tally.total} cleared</small></div>
          <p class="copy">${left ? `${left} still to practise. They'll keep coming back until you get them right first time.` : "Nothing left to review."}</p>`;
      }
      const nx = nextAfter();
      const missedHere = steps.filter((s, i) => s.type === "problem" && !s.review && st[i].tries > 1).length;
      return `<span class="tag">Lesson ${lesson.n} complete</span><h2 class="headline">${words(`${lesson.title}: done!`)}</h2>
        <div class="score">${tally.right}<small> / ${tally.total} right first time</small></div>
        <p class="copy">${missedHere ? `The ${missedHere} you missed will come back during later lessons.` : "Perfect run. Nothing to review from this one."}</p>
        ${nx ? `<div class="chunk next-card"><small>Up next</small><b>Lesson ${nx.n} · ${esc(nx.title)}</b><span>${nx.summary}</span></div>` : ""}`;
    }

    function check() {
      const step = steps[cur], p = step.p, s = st[cur];
      if (s.fill) s.ok = s.fill.every((v, i) => v === p.answer[i]);
      else if (s.seq) { const got = s.seq.map(x => x.t).join("\n"); s.ok = p.accept.some(a => a.join("\n") === got); }
      else s.ok = s.pick === p.answer;
      const first = s.tries === 0;
      s.tries++;
      s.done = true;
      if (first) {
        if (!step.review) { tally.total++; if (s.ok) tally.right++; }
        else { tally.total += mode === "review" ? 1 : 0; }
        if (s.ok) { if (progress.missed[p.id]?.on) { clearMissed(p.id); if (mode === "review") tally.cleared++; } }
        else markMissed(p.id);
      }
      if (navigator.vibrate) try { navigator.vibrate(s.ok ? 12 : [20, 40, 20]); } catch { /* not allowed */ }
      render("fb");
    }

    body.addEventListener("click", e => {
      const step = steps[cur]; if (step.type !== "problem") return;
      const s = st[cur], t = e.target.closest("button");
      if (!t || (s.done && s.ok)) return;
      if (s.done) s.done = false;
      if (t.dataset.chip !== undefined) {
        let k = s.fill.findIndex(v => !v);
        if (k < 0) k = s.fill.length - 1;   // all gaps full: the tap replaces the last answer
        s.fill[k] = t.dataset.chip; just = "s" + k;
        tapped = "c" + t.dataset.chip;
      } else if (t.dataset.slot !== undefined) s.fill[+t.dataset.slot] = null;
      else if (t.dataset.line !== undefined) s.pick = +t.dataset.line;
      else if (t.dataset.pool !== undefined) { s.seq.push(s.pool.splice(+t.dataset.pool, 1)[0]); just = "q" + (s.seq.length - 1); }
      else if (t.dataset.seq !== undefined) s.pool.push(s.seq.splice(+t.dataset.seq, 1)[0]);
      else return;
      render();
    });

    go.addEventListener("click", () => {
      const step = steps[cur];
      if (step.type === "card") { cur++; return render("step"); }
      if (step.type === "done") {
        const nx = nextAfter();
        location.hash = nx ? `#lesson-${nx.id}` : "";
        return;
      }
      const s = st[cur];
      if (s.done && s.ok) {
        cur++;
        if (steps[cur].type === "done" && mode === "lesson") {
          const prev = progress.lessons[lesson.id];
          if (!prev || prev.right <= tally.right) progress.lessons[lesson.id] = { done: Date.now(), right: tally.right, total: tally.total };
          save();
        }
        return render("step");
      }
      if (s.done) { s.done = false; return render(); }
      check();
    });
    back.addEventListener("click", () => { if (cur > 0) { cur--; render("step"); } });
    render("step");
  }

  // ───────── sync: progress lives in one JSON file in a GitHub repo ─────────
  const Sync = (() => {
    let cfg = ls.get(SYNC_KEY) || null;   // {token, repo, path}
    let status = { kind: "off", text: "Not set up", at: (ls.get(SYNC_KEY + ":at") || 0) };
    let timer = null, running = false;
    const listeners = new Set();
    const set = (kind, text) => { status = { ...status, kind, text }; listeners.forEach(f => f()); };

    const b64e = str => { const b = new TextEncoder().encode(str); let s = ""; b.forEach(x => s += String.fromCharCode(x)); return btoa(s); };
    const b64d = b64 => new TextDecoder().decode(Uint8Array.from(atob(b64.replace(/\s/g, "")), c => c.charCodeAt(0)));
    const stable = o => JSON.stringify(o, (k, v) => v && typeof v === "object" && !Array.isArray(v) ? Object.fromEntries(Object.entries(v).sort()) : v);

    async function api(method, body) {
      const path = cfg.path.split("/").map(encodeURIComponent).join("/");
      const r = await fetch(`https://api.github.com/repos/${cfg.repo}/contents/${path}`, {
        method, cache: "no-store",
        headers: { Authorization: `Bearer ${cfg.token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
        body: body ? JSON.stringify(body) : undefined,
      });
      return r;
    }
    async function pull() {
      const r = await api("GET");
      if (r.status === 404) return { sha: null, data: null };
      if (!r.ok) throw Object.assign(new Error("http"), { status: r.status });
      const j = await r.json();
      return { sha: j.sha, data: JSON.parse(b64d(j.content)) };
    }
    function merge(a, b) {
      const out = blank();
      for (const id of new Set([...Object.keys(a.lessons || {}), ...Object.keys(b.lessons || {})])) {
        const x = a.lessons?.[id], y = b.lessons?.[id];
        out.lessons[id] = !x ? y : !y ? x : (y.right > x.right || (y.right === x.right && y.done < x.done)) ? y : x;
      }
      for (const id of new Set([...Object.keys(a.missed || {}), ...Object.keys(b.missed || {})])) {
        const x = a.missed?.[id], y = b.missed?.[id];
        out.missed[id] = !x ? y : !y ? x : (y.t > x.t ? y : x);
      }
      out.updated = Math.max(a.updated || 0, b.updated || 0);
      return out;
    }
    async function run() {
      if (!cfg || running) return;
      if (!navigator.onLine) return set("wait", "Offline. Will sync when you're back online.");
      running = true; set("wait", "Syncing…");
      try {
        for (let attempt = 0; attempt < 2; attempt++) {
          const { sha, data } = await pull();
          const merged = data ? merge(progress, data) : progress;
          progress = merged; ls.set(PROGRESS_KEY, progress);
          if (data && stable(merged) === stable(data)) break;
          const r = await api("PUT", { message: "Update Pocket Rust progress", content: b64e(JSON.stringify(merged, null, 1)), ...(sha ? { sha } : {}) });
          if (r.ok) break;
          if (r.status === 409 || r.status === 422) continue; // changed elsewhere meanwhile: pull and merge again
          throw Object.assign(new Error("http"), { status: r.status });
        }
        status.at = Date.now(); ls.set(SYNC_KEY + ":at", status.at);
        set("ok", "Synced");
        if (!location.hash) home();
      } catch (e) {
        const s = e.status;
        set("err", s === 401 ? "GitHub rejected the token. Check it hasn't expired."
          : s === 403 || s === 404 ? "No access to that repo. Check the name and that the token can write to it."
          : "Couldn't reach GitHub. Will try again later.");
      } finally { running = false; }
    }
    window.addEventListener("online", () => run());
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") run(); });
    return {
      get cfg() { return cfg; },
      configure(c) { cfg = c; if (c) ls.set(SYNC_KEY, c); else { ls.del(SYNC_KEY); set("off", "Not set up"); } },
      run, soon() { if (!cfg) return; clearTimeout(timer); timer = setTimeout(run, 1200); },
      state() { return { ...status, dot: !cfg ? "" : status.kind === "ok" ? "ok" : status.kind === "err" ? "err" : "wait" }; },
      onChange(f) { listeners.add(f); return () => listeners.delete(f); },
    };
  })();

  function syncView() {
    const c = Sync.cfg || { token: "", repo: "", path: "pocket-rust/progress.json" };
    app.innerHTML = `<main class="home">
      <header class="home-top"><div class="brand"><h1>Sync</h1><button class="close" type="button" data-go="" aria-label="Back home">✕</button></div>
        <p class="lede">Keep your progress on every device by saving it to a file in one of your GitHub repos.</p></header>
      <form class="chunk form" id="sync-form" autocomplete="off">
        <div class="field"><label for="repo">Repository</label><input id="repo" name="repo" placeholder="your-name/pocket-rust-progress" value="${esc(c.repo)}" required pattern="[\\w.-]+/[\\w.-]+" spellcheck="false" autocapitalize="off">
          <small>owner/name. A private repo is best.</small></div>
        <div class="field"><label for="path">File</label><input id="path" name="path" value="${esc(c.path)}" required spellcheck="false" autocapitalize="off"></div>
        <div class="field"><label for="token">Access token</label><input id="token" name="token" type="password" value="${esc(c.token)}" required spellcheck="false" autocapitalize="off">
          <small>Stays on this device only.</small></div>
        <div class="status" id="sync-status" role="status"></div>
        <div class="row"><button class="btn go" type="submit">Save and sync</button>${Sync.cfg ? `<button class="btn plain" type="button" id="forget">Turn off</button>` : ""}</div>
      </form>
      <section class="chunk form"><b>Making a token</b>
        <ol class="steps">
          <li>Open <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">GitHub → new fine-grained token</a>.</li>
          <li>Under repository access, pick <b>only</b> your progress repo.</li>
          <li>Under permissions, set <b>Contents</b> to <b>Read and write</b>.</li>
          <li>Copy the token and paste it above. Do the same on each device.</li>
        </ol></section>
    </main>`;
    const statusEl = app.querySelector("#sync-status");
    const paint = () => { const s = Sync.state(); statusEl.textContent = s.text + (s.kind === "ok" && s.at ? ` · ${ago(s.at)}` : ""); };
    paint();
    const off = Sync.onChange(paint);
    window.addEventListener("hashchange", off, { once: true });
    app.querySelector("#sync-form").addEventListener("submit", e => {
      e.preventDefault();
      const f = new FormData(e.target);
      Sync.configure({ repo: f.get("repo").trim(), path: f.get("path").trim().replace(/^\/+/, ""), token: f.get("token").trim() });
      Sync.run();
    });
    app.querySelector("#forget")?.addEventListener("click", () => { Sync.configure(null); syncView(); });
    animate(app.firstElementChild);
  }

  // ───────── routing ─────────
  function route() {
    if (!COURSE) return;
    const h = location.hash.slice(1);
    window.scrollTo(0, 0);
    if (h.startsWith("lesson-")) { const l = COURSE.lessons.find(x => x.id === h.slice(7)); if (l) return player("lesson", l); }
    if (h === "review" && missedOn().length) return player("review");
    if (h === "sync") return syncView();
    if (h) { history.replaceState(null, "", location.pathname + location.search); }
    home();
  }
  document.addEventListener("click", e => {
    const t = e.target.closest("[data-go]");
    if (t) { e.preventDefault(); const to = t.dataset.go; if (to === "" ) { history.pushState(null, "", location.pathname + location.search); route(); } else location.hash = to; }
  });
  window.addEventListener("hashchange", route);
  window.addEventListener("popstate", route);

  // ───────── start ─────────
  app.innerHTML = `<div class="loading">Loading lessons…</div>`;
  fetch("course.json").then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }).then(c => {
    COURSE = c;
    c.lessons.forEach(l => l.problems.forEach(p => { problemById[p.id] = p; lessonOf[p.id] = l; }));
    route();
    Sync.run();
  }).catch(() => {
    app.innerHTML = `<div class="loading">Couldn't load the lessons. Check your connection and reopen the app.</div>`;
  });

  if ("serviceWorker" in navigator && /^(https:|http:\/\/localhost|http:\/\/127\.)/.test(location.href)) {
    try { navigator.serviceWorker.register("sw.js").catch(() => {}); } catch { /* not allowed here */ }
  }
})();
