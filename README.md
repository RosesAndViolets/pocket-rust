# Pocket Rust

Learn Rust from scratch on your phone. Each lesson is a few short cards, then problems you
answer by tapping: fill the gap, find the error, order the lines, predict the output.
Problems you miss come back during later lessons and in Review.

A static web app: no server, no build step for the app itself. Works offline once opened,
and can be added to the home screen.

## Files

| File | What it is |
| --- | --- |
| `index.html`, `app.css`, `app.js` | The app. `app.js` routes on the hash: home, `#lesson-<id>`, `#review`, `#sync`. |
| `course.json` | The lessons, generated. Don't edit by hand. |
| `sw.js`, `manifest.webmanifest`, `icons/` | Offline cache and home-screen install. |
| `tools/course_src.py` | The lessons as written: cards and problems. Edit this. |
| `tools/build.py` | Checks every problem with `rustc`, then writes `course.json`. |
| `tools/icons.py` | Draws the icons. |

## Changing lessons

Edit `tools/course_src.py`, then run:

```sh
python3 tools/build.py
```

It needs `rustc` on your PATH. For each problem it checks that:

- **Fill the gap:** the answer compiles and prints what it should, and every wrong chip
  fails or prints something else.
- **Find the error:** the program fails with the stated error code at the stated line. The
  compiler's own message is saved and shown to you after a right answer.
- **Predict the output:** the program prints exactly the answer, or fails to compile if the
  answer is "won't compile".
- **Order the lines:** the written order works. Every other order is also compiled and run,
  and any that print the same output are accepted too.
- **No skipping ahead:** no code uses something a later lesson teaches (the `GATES` list).

If anything fails, it prints what's wrong and leaves `course.json` unchanged. Compiler
results are cached in `tools/.rustc-cache.json`.

## Sync

Progress is kept in the browser. To share it between devices, open **Sync** and enter a
GitHub repo, a file path and a fine-grained token that can only read and write that repo's
contents. The app reads the file, merges it with local progress, and writes it back. When
you're offline it waits until you're back online.

## Running it locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Offline caching needs `https` or `localhost`.
