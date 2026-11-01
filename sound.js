// Pocket Rust sound effects: the "Bubble Pop" kit, synthesized live with Web Audio (no audio files).
// Each sound is timed by app.js to land with its animation. Pitch wobbles a little on repeated
// sounds so tapping doesn't get grating.
//
// iPhone silent switch: by default iOS mutes web sounds when the switch is on. With "Play on silent"
// on, the page asks for the "playback" audio session (Safari 17+), or on older iOS plays a silent
// looping <audio> track, which has the same effect. Either way, like any app that plays sound on
// silent, it pauses music playing in other apps while Pocket Rust is open.
window.Sfx = (() => {
  "use strict";
  const KEY = "pocket-rust:sound";
  const defaults = { on: true, volume: 0.7, ignoreSilent: true };
  let s = { ...defaults };
  try { Object.assign(s, JSON.parse(localStorage.getItem(KEY)) || {}); } catch { /* storage blocked */ }
  const isIOS = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

  let ctx = null, master = null, noiseBuf = null, silentLoop = null;
  // iOS breaks the audio engine when the phone locks or the app goes to the background: it can report
  // "running" afterwards and still play nothing. So after any trip to the background the engine is
  // marked stale, and the next tap builds a fresh one.
  let stale = false, sessionType = null;

  // ───────── audio session / silent switch ─────────
  function silentWavUrl() {   // 0.5 s of 8-bit 8 kHz silence, built in memory
    const n = 4000, b = new ArrayBuffer(44 + n), v = new DataView(b);
    const str = (o, t) => [...t].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
    str(0, "RIFF"); v.setUint32(4, 36 + n, true); str(8, "WAVEfmt "); v.setUint32(16, 16, true);
    v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, 8000, true); v.setUint32(28, 8000, true);
    v.setUint16(32, 1, true); v.setUint16(34, 8, true); str(36, "data"); v.setUint32(40, n, true);
    for (let i = 0; i < n; i++) v.setUint8(44 + i, 128);
    return URL.createObjectURL(new Blob([b], { type: "audio/wav" }));
  }
  function applySession() {
    const want = s.on && s.ignoreSilent;
    if (navigator.audioSession) {
      const type = want ? "playback" : "ambient";
      if (sessionType !== type) {        // only change it when it really changes; switching it can break the engine
        try { navigator.audioSession.type = type; sessionType = type; } catch { /* not allowed */ }
      }
      return;
    }
    if (!isIOS) return;
    if (want) {
      if (!silentLoop) { silentLoop = new Audio(silentWavUrl()); silentLoop.loop = true; silentLoop.setAttribute("playsinline", ""); silentLoop.volume = 0.01; }
      if (document.visibilityState === "visible") silentLoop.play().catch(() => {});
    } else if (silentLoop) silentLoop.pause();
  }
  // Audio may only start from a tap, so every tap makes sure it's awake.
  function unlock() {
    if (!s.on) return;
    applySession();
    if (ctx && (stale || ctx.state === "interrupted" || ctx.state === "closed")) {
      try { ctx.close(); } catch { /* already gone */ }
      ctx = null; master = null; noiseBuf = null;
    }
    stale = false;
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = s.volume; master.connect(ctx.destination);
      ctx.addEventListener("statechange", () => { if (ctx && ctx.state === "interrupted") stale = true; });
    }
    if (ctx.state !== "running") ctx.resume().catch(() => {});
  }
  document.addEventListener("pointerdown", unlock, true);
  document.addEventListener("keydown", unlock, true);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") { stale = true; if (silentLoop) silentLoop.pause(); }
  });
  window.addEventListener("pagehide", () => { stale = true; });
  window.addEventListener("pageshow", e => { if (e.persisted) stale = true; });

  // ───────── voices ─────────
  const jit = (f, amt = 0.035) => f * (1 + (Math.random() - 0.5) * amt);
  function env(g, t, a, d, v) {
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(Math.max(v, 0.0002), t + a);
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + d);
  }
  function tone({ type = "sine", f, f2, t = 0, a = 0.006, d = 0.15, v = 0.25, lp }) {
    const now = ctx.currentTime + t, o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.setValueAtTime(f, now);
    if (f2) o.frequency.exponentialRampToValueAtTime(f2, now + a + d * 0.8);
    let n = o;
    if (lp) { const fl = ctx.createBiquadFilter(); fl.type = "lowpass"; fl.frequency.value = lp; o.connect(fl); n = fl; }
    env(g, now, a, d, v); n.connect(g); g.connect(master); o.start(now); o.stop(now + a + d + 0.05);
  }
  function noise({ t = 0, d = 0.2, v = 0.15, f = 1200, f2, q = 1.2, a = 0.01 }) {
    if (!noiseBuf) {
      noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
      const ch = noiseBuf.getChannelData(0); for (let i = 0; i < ch.length; i++) ch[i] = Math.random() * 2 - 1;
    }
    const now = ctx.currentTime + t, src = ctx.createBufferSource(), fl = ctx.createBiquadFilter(), g = ctx.createGain();
    src.buffer = noiseBuf; fl.type = "bandpass"; fl.Q.value = q; fl.frequency.setValueAtTime(f, now);
    if (f2) fl.frequency.exponentialRampToValueAtTime(f2, now + a + d);
    env(g, now, a, d, v); src.connect(fl); fl.connect(g); g.connect(master); src.start(now); src.stop(now + a + d + 0.05);
  }

  // ───────── Bubble Pop ─────────
  const KIT = {
    tap: () => tone({ f: jit(520), f2: 300, d: 0.07, v: 0.22 }),                 // chip squishes down
    place: () => { tone({ f: jit(280), f2: 900, d: 0.09, v: 0.28 }); tone({ f: 1250, d: 0.04, v: 0.06, t: 0.05 }); },  // lands in a gap
    remove: () => tone({ f: jit(820), f2: 240, d: 0.1, v: 0.2 }),               // sent back
    select: () => tone({ type: "triangle", f: jit(760), f2: 640, d: 0.05, v: 0.16 }),
    press: () => tone({ f: 190, f2: 90, d: 0.12, v: 0.4, lp: 900 }),            // big button thump
    next: () => { noise({ f: 500, f2: 1800, d: 0.16, v: 0.06 }); tone({ f: 420, f2: 640, d: 0.1, v: 0.07, t: 0.04 }); },
    word: i => tone({ f: 420 * Math.pow(1.09, i), f2: 620 * Math.pow(1.09, i), d: 0.05, v: 0.06 }),
    right: () => {
      [[523, 790], [660, 990], [790, 1320]].forEach(([a, b], i) => tone({ f: a, f2: b, d: 0.12, v: 0.22, t: i * 0.08 }));
      tone({ f: 160, f2: 80, d: 0.14, v: 0.35, t: 0.26, lp: 700 });
    },
    wrong: () => { tone({ f: 330, f2: 230, d: 0.16, v: 0.24 }); tone({ f: 250, f2: 150, d: 0.22, v: 0.24, t: 0.16 }); },
    complete: () => {
      [523, 659, 784, 1046, 1318].forEach((f, i) => tone({ f, f2: f * 1.5, d: 0.12, v: 0.22, t: i * 0.09 }));
      [2093, 2637, 3136].forEach((f, i) => tone({ type: "triangle", f, d: 0.25, v: 0.05, t: 0.5 + i * 0.06 }));
    },
    back: () => tone({ f: 600, f2: 340, d: 0.08, v: 0.15 }),
  };

  function play(name, arg, delay = 0) {
    if (!s.on || !ctx || stale || ctx.state !== "running") return;
    const fn = KIT[name]; if (!fn) return;
    const go = () => { try { fn(arg); } catch { /* a dropped sound is fine */ } };
    if (delay) setTimeout(go, delay); else go();
  }
  // Headline words: one rising note per word, in step with the word animation (70 ms apart).
  function words(n, start = 120) { for (let i = 0; i < Math.min(n, 9); i++) play("word", i, start + i * 70); }

  function set(patch) {
    Object.assign(s, patch);
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch { /* storage blocked */ }
    if (master) master.gain.value = s.volume;
    if (s.on) unlock(); else applySession();
  }

  return { play, words, set, get settings() { return { ...s }; }, isIOS };
})();
