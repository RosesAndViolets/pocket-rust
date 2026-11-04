#!/usr/bin/env python3
"""Check every problem in course_src.py against the real Rust compiler, then write ../course.json.

What is checked:
  fill   - the answer compiles (and prints `output` if given); every wrong bank option fails or prints something else.
  error  - the program fails with `error_code`, and the compiler's message points at `line`.
           The message the learner sees is the compiler's own, captured here.
  output - the program prints exactly `answer` (or fails to compile, if the answer is "won't compile").
  order  - the order as written works; every other order of the lines is tried, and each one
           that also prints `output` is accepted by the app.
  cards  - every lesson card's code compiles on its own, so no card leans on an earlier one.
  gates  - no code uses something a later lesson teaches.

Usage: python3 tools/build.py        (needs rustc on PATH)
"""
import hashlib, html, itertools, json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from course_src import COURSE, GATES, WONT  # noqa: E402

CACHE_FILE = HERE / ".rustc-cache.json"
OUT = HERE.parent / "course.json"
cache = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
problems_found = []


def lines_of(code):
    return code.strip("\n").split("\n")


def program(lines, wrap):
    if wrap:
        return "fn main() {\n" + "\n".join(("    " + l) if l else "" for l in lines) + "\n}\n"
    return "\n".join(lines) + "\n"


def compile_run(src):
    """-> {ok, stdout, diags:[{level, code, lines, rendered}]} (cached by source hash)."""
    key = hashlib.sha1(src.encode()).hexdigest()
    if key in cache:
        return cache[key]
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "main.rs"
        path.write_text(src)
        p = subprocess.run(["rustc", "--edition", "2021", "-A", "warnings", "--error-format=json",
                            "--color", "never", "-o", str(Path(d) / "bin"), str(path)],
                           capture_output=True, text=True, cwd=d)
        diags = []
        for raw in p.stderr.splitlines():
            try:
                j = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if j.get("level") != "error" or not j.get("code"):
                continue
            spans = []
            def walk(x):
                for s in x.get("spans", []):
                    spans.extend(range(s["line_start"], s["line_end"] + 1))
                for c in x.get("children", []):
                    walk(c)
            walk(j)
            primary = [s["line_start"] for s in j.get("spans", []) if s.get("is_primary")]
            rendered = j.get("rendered", "").replace(str(path), "src/main.rs").rstrip()
            diags.append({"code": j["code"]["code"], "lines": sorted(set(spans)), "primary": primary, "rendered": rendered})
        res = {"ok": p.returncode == 0, "stdout": None, "diags": diags}
        if res["ok"]:
            try:
                r = subprocess.run([str(Path(d) / "bin")], capture_output=True, text=True, timeout=2)
                res["stdout"] = r.stdout if r.returncode == 0 else None
                res["ok"] = r.returncode == 0
            except subprocess.TimeoutExpired:  # a reordered loop that never ends
                res["ok"] = False
    cache[key] = res
    return res


def out_lines(res):
    return None if res["stdout"] is None else res["stdout"].rstrip("\n").split("\n")


def problem(where, msg):
    problems_found.append(f"{where}: {msg}")


def md(text):
    """`code` -> <code>, everything else escaped."""
    parts = text.split("`")
    return "".join(f"<code>{html.escape(p)}</code>" if i % 2 else html.escape(p) for i, p in enumerate(parts))


def substitute(lines, values):
    it = iter(values)
    return [re.sub("__", lambda _: next(it), l) for l in lines]


def check_gates(where, n, text):
    """Only code counts: comments, text in quotes and the "won't compile" chip are skipped."""
    text = raw = text.replace("__", " ").replace(WONT, " ")
    text = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    text = re.sub(r"//[^\n]*", "", text) + (" {:?}" if "{:?}" in raw else "")  # debug printing lives inside quotes
    for pat, lesson in GATES:
        if lesson > n:
            m = re.search(pat, text)
            if m:
                problem(where, f"uses `{m.group(0)}`, which lesson {lesson} teaches")


def check_card(where, c, pool):
    """A card must make sense on its own: its code compiles with nothing from earlier cards.
    Code without its own `fn main` is put inside one (structs, impls and fns are allowed there too)."""
    lines = lines_of(c["code"])
    r = pool.submit(compile_run, program(lines, "fn main" not in c["code"])).result()
    if not r["ok"]:
        first = r["diags"][0]["rendered"].split("\n")[0] if r["diags"] else "it doesn't run"
        problem(where, f"doesn't work on its own: {first}")


def check_fill(where, p, pool):
    lines = lines_of(p["code"])
    gaps = sum(l.count("__") for l in lines)
    if gaps != len(p["answer"]):
        problem(where, f"{gaps} gaps but {len(p['answer'])} answers")
        return
    good = pool.submit(compile_run, program(substitute(lines, p["answer"]), p["wrap"]))
    wrongs = []
    for k in range(gaps):
        for b in p["bank"]:
            if b == p["answer"][k]:
                continue
            vals = list(p["answer"]); vals[k] = b
            wrongs.append((b, pool.submit(compile_run, program(substitute(lines, vals), p["wrap"]))))
    g = good.result()
    if not g["ok"]:
        problem(where, "answer doesn't compile/run:\n" + "\n".join(d["rendered"] for d in g["diags"]))
        return
    if p.get("output") and out_lines(g) != p["output"]:
        problem(where, f"prints {out_lines(g)}, expected {p['output']}")
    for b, f in wrongs:
        r = f.result()
        if r["ok"] and out_lines(r) == out_lines(g):
            problem(where, f"wrong option `{b}` also works")


def check_error(where, p, pool):
    lines = lines_of(p["code"])
    r = pool.submit(compile_run, program(lines, False)).result()
    if r["ok"] or not r["diags"]:
        problem(where, "program compiles, but should fail")
        return
    d = r["diags"][0]
    if d["code"] != p["error_code"]:
        problem(where, f"error is {d['code']}, expected {p['error_code']}")
    if p["line"] not in d["lines"]:
        problem(where, f"error points at lines {d['lines']}, not {p['line']}")
    p["rustc"] = d["rendered"].split("\n\nerror: aborting")[0]


def check_output(where, p, pool):
    lines = lines_of(p["code"])
    r = pool.submit(compile_run, program(lines, p["wrap"])).result()
    for a in p["answer"]:
        if a not in p["bank"]:
            problem(where, f"answer `{a}` isn't in the bank")
    if p["answer"] == [WONT]:
        if r["ok"]:
            problem(where, f"compiles and prints {out_lines(r)}, but the answer says it won't compile")
        elif r["diags"]:
            p["rustc"] = r["diags"][0]["rendered"]
        return
    if not r["ok"]:
        problem(where, "doesn't compile/run:\n" + "\n".join(d["rendered"] for d in r["diags"]))
    elif out_lines(r) != p["answer"]:
        problem(where, f"prints {out_lines(r)}, answer says {p['answer']}")


def check_order(where, p, pool):
    pool_lines = p["pool"]
    trimmed = [l.strip() for l in pool_lines]
    perms = sorted(set(itertools.permutations(range(len(pool_lines)), len(pool_lines))))
    seen, jobs = set(), []
    for perm in perms:
        key = tuple(trimmed[i] for i in perm)
        if key in seen:
            continue
        seen.add(key)
        src = program(p["head"] + [pool_lines[i] for i in perm] + p["tail"], False)
        jobs.append((key, pool.submit(compile_run, src)))
    accept = [list(k) for k, f in jobs if f.result()["ok"] and out_lines(f.result()) == p["output"]]
    if trimmed not in accept:
        problem(where, "the order as written doesn't print the expected output")
    p["accept"] = accept


def main():
    built = []
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        for n, lesson in enumerate(COURSE, 1):
            L = {"id": lesson["id"], "n": n, "title": lesson["title"], "summary": md(lesson["summary"]),
                 "cards": [], "problems": []}
            for c in lesson["cards"]:
                check_gates(f"{lesson['id']} card '{c['h']}'", n, c["code"])
                check_card(f"{lesson['id']} card '{c['h']}'", c, pool)
                L["cards"].append({"h": c["h"], "p": md(c["p"]), "code": lines_of(c["code"]),
                                   "note": md(c["note"]) if c.get("note") else None})
            for k, p in enumerate(lesson["problems"], 1):
                where = f"{lesson['id']} problem {k} ({p['type']})"
                p = dict(p)
                code_text = p.get("code") or "\n".join(p.get("head", []) + p.get("pool", []) + p.get("tail", []))
                check_gates(where, n, code_text + "\n" + "\n".join(p.get("bank", [])))
                {"fill": check_fill, "error": check_error, "output": check_output, "order": check_order}[p["type"]](where, p, pool)
                q = {"id": f"{lesson['id']}-{k}", "type": p["type"], "prompt": p["prompt"],
                     "good": md(p["good"]), "bad": md(p["bad"])}
                if p["type"] in ("fill", "output", "error"):
                    q["lines"] = lines_of(p["code"])
                if p["type"] in ("fill", "output"):
                    q["bank"], q["answer"] = p["bank"], p["answer"]
                if p["type"] == "error":
                    q["answer"] = p["line"] - 1
                if p.get("rustc"):
                    q["rustc"] = p["rustc"]
                if p["type"] == "order":
                    q.update(head=p["head"], tail=p["tail"], pool=[l.strip() for l in p["pool"]], accept=p["accept"])
                L["problems"].append(q)
            built.append(L)
    CACHE_FILE.write_text(json.dumps(cache))
    if problems_found:
        print(f"{len(problems_found)} problem(s):\n")
        print("\n\n".join(problems_found))
        sys.exit(1)
    rustc = subprocess.run(["rustc", "--version"], capture_output=True, text=True).stdout.split(" (")[0].strip()
    OUT.write_text(json.dumps({"version": 1, "rustc": rustc, "lessons": built}, ensure_ascii=False, indent=1))
    total = sum(len(l["problems"]) for l in built)
    print(f"OK: {len(built)} lessons, {total} problems, all checked by rustc. Wrote {OUT.name}.")


if __name__ == "__main__":
    main()
