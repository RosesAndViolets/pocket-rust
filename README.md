# Pocket Rust

Learn Rust from scratch on your phone. Each lesson is a few short cards, then problems you
answer by tapping: fill the gap, find the error, order the lines, predict the output.
Problems you miss come back during later lessons and in Review.

A static web app: no server, no build step for the app itself. Works offline once opened,
and can be added to the home screen.

## Files

| File | What it is |
| --- | --- |
| `index.html`, `app.css`, `app.js` | The app. `app.js` routes on the hash: home, `#lesson-<id>`, `#review`, `#settings`. |
| `sound.js` | Sound effects (the Bubble Pop kit), made live with Web Audio. No audio files. |
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

It needs `rustc` and `clippy-driver` (usually in `~/.cargo/bin`) on your PATH. For each problem it checks that:

- **Fill the gap:** the answer compiles and prints what it should, and every wrong chip
  fails or prints something else.
- **Find the error:** the program fails with the stated error code at the stated line. The
  compiler's own message is saved and shown to you after a right answer.
- **Predict the output:** the program prints exactly the answer, or fails to compile if the
  answer is "won't compile".
- **Order the lines:** the written order works. Every other order is also compiled and run,
  and any that print the same output are accepted too.
- **Find the smell (`smell`):** working code triggers exactly the named Clippy lint on the
  stated primary line. The fixed code has no warnings and prints the same output. Both use
  `-W clippy::all -W clippy::pedantic`; wrapped code's line numbers are adjusted for `fn main`.
- **Pick the better version (`better`):** A and B compile and print the same output. A stated
  lint occurs in the worse version only. With `lint=None`, the app labels it a "judgement call".
- **Real snippets (`real`):** shown, not compiled. Include repo, tag or full commit, path,
  1-based `(start, end)` lines (up to 25), and license. Non-commit refs are checked against
  GitHub tags on first build (needs network and git); successful checks are cached. Branch
  names such as `main` and `master` are rejected. Use `repo=None, own=True` for private owner
  code: all other credits remain required, but no link is shown and it says "your code".
- **Test examples:** code containing `#[test]` or `#[cfg(test)]` also compiles and runs
  with `rustc --test`, so assertions inside tests are checked as well as ordinary main output.
- **Every card stands alone:** each ordinary lesson card's code compiles by itself, so a card never
  leans on a name (`p`, `Point`, `ages`…) that only an earlier card showed.
- **No skipping ahead:** no code uses something a later lesson teaches (the `GATES` list).

If anything fails, it prints what's wrong and leaves `course.json` unchanged. Compiler
and Clippy results are cached in `tools/.rustc-cache.json`.

Each lesson has `part`: 1 (Basics), 2 (Real programs, by area), or 3 (Review and fix).
The home screen groups lessons by part. Lesson numbers stay sequential; ids and saved
progress keys stay the same. Add lessons before the final review lesson as the course grows.

Author helpers in `tools/course_src.py`:

```python
real(h, p, code, repo, tag, path, lines, license, note=None, *, own=False)
smell(prompt, code, line, lint, fixed, good, bad, wrap=False)
better(prompt, a, b, answer, lint, good, bad, wrap=False)
```

## Sound

Every tap, pop, right and wrong answer has a sound, timed to its animation. The speaker button
on the home screen turns them on or off; Settings has the volume. Sounds follow the phone's
silent switch, and music from other apps keeps playing underneath.

iOS can leave web audio silent after the phone locks, so whenever the app goes to the background
`sound.js` throws its audio engine away and builds a fresh one on the next tap.

## Sync

Progress is kept in the browser. To share it between devices, open **Settings** and enter a
GitHub repo, a file path and a fine-grained token that can only read and write that repo's
contents. The app reads the file, merges it with local progress, and writes it back. When
you're offline it waits until you're back online.

## Credits

Lesson 16, "Fix the compiler", adapts puzzles from Akira Nishikawa's Rust Compile Challenge
(MIT license, © 2021 Akira Nishikawa): translated, shortened, and turned into tap-to-answer problems.

"Fighting the borrow checker the wrong way" quotes [Rayon v1.10.0, src/slice/mod.rs, lines 203–208](https://github.com/rayon-rs/rayon/blob/v1.10.0/src/slice/mod.rs#L203-L208),
under the MIT license, © 2010 The Rust Project Developers. The snippet was checked against
that tag's raw file. The [MIT notice](licenses/rayon-MIT.txt) is included with this app.

The command-line lessons quote [ripgrep 14.1.1](https://github.com/BurntSushi/ripgrep/tree/14.1.1)
(Cargo workspace, exit status, application dispatch, globset error structure), under the MIT
license, © 2015 Andrew Gallant. The [MIT notice](licenses/ripgrep-MIT.txt) is included.

They also quote [clap v4.5.20](https://github.com/clap-rs/clap/tree/v4.5.20)
(derive examples for boolean flags and typed parsing), under the MIT license,
© Individual contributors. The [MIT notice](licenses/clap-MIT.txt) is included.
Both projects offer alternative licenses; these excerpts use their MIT terms.
Every card links to its exact file and line range at the release tag.

The web-server lessons quote [axum axum-v0.7.9](https://github.com/tokio-rs/axum/tree/axum-v0.7.9)
(router, extractors, shared state, and centralized error responses), under the MIT license,
© 2019 Axum Contributors. The [MIT notice](licenses/axum-MIT.txt) is included.

They also quote [mini-redis v0.3.0](https://github.com/tokio-rs/mini-redis/tree/v0.3.0)
(command/storage separation and short lock lifetime), under the MIT license,
© 2020 Tokio Contributors. The [MIT notice](licenses/mini-redis-MIT.txt) is included.
Public excerpts link to exact lines at those release tags and are shown, not compiled.

“Your own server” shows short Websidian excerpts with the owner's permission, labelled
“your code” without public links. They contain code only, with no personal data or file paths.
Exercises use plain std analogues; their checks do not prove async runtime behavior.

The calculations lessons also quote [Rayon v1.10.0](https://github.com/rayon-rs/rayon/tree/v1.10.0)
(iterator pipeline, mutable slice splitting, and split/work/join reduction), using the same
[MIT notice](licenses/rayon-MIT.txt) credited above.

They quote [ndarray 0.16.1](https://github.com/rust-ndarray/ndarray/tree/0.16.1)
(storage and shape, generic numeric bounds, and in-place mapping), under the MIT license,
© 2015–2021 Ulrik Sverdrup “bluss”, Jim Turner, and ndarray developers.
The [MIT notice](licenses/ndarray-MIT.txt) is included. ndarray also offers Apache-2.0;
these excerpts use its MIT terms. Every excerpt links to exact tagged lines.
The std exercises check behavior and allocation structure, not measured speed or Rayon scheduling.

## Running it locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Offline caching needs `https` or `localhost`.
