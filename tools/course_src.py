"""The course, as written. `build.py` checks every problem with rustc and writes `course.json`.

Text fields take `backticks` for inline code. Code is a triple-quoted string.
Each lesson has `part`: 1 (Basics), 2 (Real programs, by area), 3 (Review and fix).
Cards made with `card` compile alone. `real(h, p, code, repo, tag, path, lines, license,
note=None)` shows a credited excerpt without compiling it. Use a real tag or full commit,
a 1-based (start, end) range of at most 25 lines, and a license. For private owner code,
use `repo=None, own=True` (no link, labelled "your code").
Problem types:
  fill   - `__` marks each gap; `answer` fills them in order; wrong bank options must not work.
  error  - a whole program; `line` (1-based) is the line the compiler rejects; `code` is its error code.
  output - `answer` is what the program prints, one entry per line; ["won't compile"] if it doesn't.
  order  - `pool` lines in the right order; the build finds every other order that also works.
  smell  - working code; clippy must report only `lint`, with a primary span on `line`.
           `fixed` must be warning-free and print the same output.
  better - versions `a` and `b` print the same; `answer` is "a" or "b". `lint` must occur
           only in the worse version. `lint=None` is an author judgement, labelled in the app.
`wrap=True` puts the code inside `fn main() { }` when it's compiled (the learner sees it unwrapped).
"""

WONT = "won't compile"


def card(h, p, code, note=None):
    return {"h": h, "p": p, "code": code, "note": note}


def real(h, p, code, repo, tag, path, lines, license, note=None, *, own=False):
    return dict(type="real", h=h, p=p, code=code, repo=repo, tag=tag, path=path,
                lines=lines, license=license, note=note, own=own)


def smell(prompt, code, line, lint, fixed, good, bad, wrap=False):
    return dict(type="smell", prompt=prompt, code=code, line=line, lint=lint,
                fixed=fixed, good=good, bad=bad, wrap=wrap)


def better(prompt, a, b, answer, lint, good, bad, wrap=False):
    return dict(type="better", prompt=prompt, a=a, b=b, answer=answer, lint=lint,
                good=good, bad=bad, wrap=wrap)


def fill(prompt, code, bank, answer, good, bad, output=None, wrap=True):
    return {"type": "fill", "prompt": prompt, "code": code, "bank": bank, "answer": answer,
            "good": good, "bad": bad, "output": output, "wrap": wrap}


def err(prompt, code, line, error_code, good, bad):
    return {"type": "error", "prompt": prompt, "code": code, "line": line, "error_code": error_code,
            "good": good, "bad": bad, "wrap": False}


def out(prompt, code, bank, answer, good, bad, wrap=True):
    return {"type": "output", "prompt": prompt, "code": code, "bank": bank, "answer": answer,
            "good": good, "bad": bad, "wrap": wrap}


def order(prompt, head, pool, tail, output, good, bad):
    return {"type": "order", "prompt": prompt, "head": head, "pool": pool, "tail": tail,
            "output": output, "good": good, "bad": bad}


COURSE = []

# ─────────────────────────────── 1 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "variables", "title": "Variables",
    "summary": "Your first program: `let`, `mut` and printing.",
    "cards": [
        card("Every program starts at main",
             "A Rust program runs the code inside `fn main() { }`. `fn` means function. For now, every example lives inside it.",
             '''
fn main() {
    println!("Hello!");
}''',
             "`println!` prints a line. The `!` marks it as a macro, a special kind of function. You don't need to know more than that yet."),
        card("let makes a variable",
             "`let` gives a value a name. Put the name in curly braces inside the text to print its value.",
             '''
let age = 30;
println!("{age}");  // prints 30''',
             "Every statement ends with a semicolon. Text after `//` is a comment: Rust ignores it."),
        card("Variables can't change unless you say so",
             "Once set, a variable stays the same. Add `mut` (short for mutable) to allow a new value later.",
             '''
let mut level = 1;
level = 2;           // fine, it's mut
println!("{level}"); // prints 2''',
             "Without `mut`, the compiler stops you. That's on purpose: you can trust a value won't change behind your back."),
    ],
    "problems": [
        fill("Make this compile.", '''
fn main() {
    let __ count = 0;
    count = count + 1;
    println!("{count}");
}''', ["mut", "var", "const", "let"], ["mut"],
             "Line 3 gives `count` a new value, so it has to be declared `let mut`.",
             "Line 3 changes `count`. Which word lets a variable change? (`var` is from other languages; Rust doesn't have it.)",
             output=["1"], wrap=False),
        err("Which line does the compiler reject?", '''
fn main() {
    let score = 10;
    score = 20;
    println!("{score}");
}''', 3, "E0384",
            "`score` wasn't declared `mut`, so it can't get a new value. The compiler even suggests the fix.",
            "That line is fine. Look for the line that tries to change a variable."),
        order("Make the program print 1, then 2.", ["fn main() {"],
              ["    let mut n = 1;", '    println!("{n}");', "    n = n + 1;", '    println!("{n}");'],
              ["}"], ["1", "2"],
              "Code runs top to bottom: make `n`, print it, change it, print again.",
              "A variable has to exist before you use it, and the change has to happen between the two prints."),
        out("What does this print?", '''
let mut a = 3;
println!("{a}");
a = a * 2;
println!("{a}");''', ["3", "5", "6", "9"], ["3", "6"],
            "The first print sees 3. Then `a` becomes 3 × 2, so the second print sees 6.",
            "Each print shows the value at that moment. What is `a` before line 3, and after?"),
        fill("Make it print 8.", '''
let apples = 4;
let pears = 2;
let total = apples __ pears;
println!("{total}");''', ["+", "-", "*", "/"], ["*"],
             "4 × 2 is 8. Rust uses `+ - * /` for arithmetic, like most languages.",
             "Work out what each operator gives with 4 and 2.", output=["8"]),
        out("What does this print?", '''
let x = 2;
let mut y = x;
y = y + 10;
println!("{x}");
println!("{y}");''', ["0", "2", "10", "12"], ["2", "12"],
            "`let mut y = x;` copies the number. Changing `y` later doesn't touch `x`.",
            "`y` starts as a copy of `x`. Does changing `y` change `x`?"),
    ],
})

# ─────────────────────────────── 2 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "types", "title": "Numbers and types",
    "summary": "Whole numbers, decimals, true/false, and why Rust cares.",
    "cards": [
        card("Every value has a type",
             "`i32` is a whole number, `f64` a decimal, `bool` is `true` or `false`. Rust usually works out the type itself, but you can write it after a colon.",
             '''
let age: i32 = 30;
let height: f64 = 1.75;
let is_ready: bool = true;''',
             "`i32` means a 32-bit integer and `f64` a 64-bit float. Those are the everyday defaults."),
        card("Printing any value",
             "`{}` in the text is filled with the next value after the comma. Use it when you want to print a calculation directly.",
             '''
println!("{}", 7 / 2);     // 3
println!("{}", 7 % 2);     // 1
println!("{}", 7.0 / 2.0); // 3.5''',
             "Dividing two whole numbers gives a whole number: the decimal part is dropped. `%` gives the remainder."),
        card("Types don't mix on their own",
             "You can't add an `i32` to an `f64` directly. Convert one with `as` first.",
             '''
let whole: i32 = 3;
let half: f64 = 0.5;
let total = whole as f64 + half; // 3.5''',
             "Rust never converts number types behind your back, so you always see where precision could change."),
        card("Same name, new variable",
             "Writing `let` again with the same name makes a new variable that hides the old one. This is called shadowing.",
             '''
let x = 5;
let x = x + 1;      // a new x, made from the old one
println!("{x}");    // prints 6''',
             "Shadowing is different from `mut`: each `let` makes a fresh variable, so it can even have a new type."),
    ],
    "problems": [
        out("What does this print?", '''
println!("{}", 7 / 2);
println!("{}", 7 % 2);''', ["0", "1", "3", "3.5"], ["3", "1"],
            "7 / 2 with whole numbers is 3 (the .5 is dropped), and 7 % 2 is the remainder, 1.",
            "Both numbers are whole, so the answer to 7 / 2 is whole too. `%` is the remainder."),
        err("Which line does the compiler reject?", '''
fn main() {
    let apples: i32 = 3;
    let weight: f64 = 1.5;
    let total = apples + weight;
    println!("{total}");
}''', 4, "E0277",
            "An `i32` can't be added to an `f64`. One of them has to be converted with `as` first.",
            "That line is fine on its own. Look for where two different types meet."),
        fill("Make this compile and print 4.5.", '''
let apples: i32 = 3;
let weight: f64 = 1.5;
let total = apples __ f64 + weight;
println!("{total}");''', ["as", "to", "into", "in"], ["as"],
             "`apples as f64` turns 3 into 3.0, so it can be added to 1.5.",
             "Rust converts number types with one short keyword.", output=["4.5"]),
        fill("Fill in the type.", '''
let is_open: __ = true;
println!("{is_open}");''', ["bool", "i32", "f64", "true"], ["bool"],
             "`true` and `false` are `bool` values.",
             "`true` is a value, not a type. Which type holds yes/no values?", output=["true"]),
        out("What does this print?", '''
let x = 5;
let x = x * 2;
let x = x + 1;
println!("{x}");''', ["5", "6", "10", "11"], ["11"],
            "Each `let x` makes a new `x` from the previous one: 5, then 10, then 11.",
            "Follow each line in turn. Each new `x` is built from the one before."),
        order("Make the program print 2.5.", ["fn main() {"],
              ["    let total: i32 = 5;", "    let count: i32 = 2;", "    let avg = total as f64 / count as f64;", '    println!("{avg}");'],
              ["}"], ["2.5"],
              "Both numbers must exist before you divide them, and the print comes last. `total` and `count` can go in either order.",
              "Each variable has to be made before a line uses it."),
    ],
})

# ─────────────────────────────── 3 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "functions", "title": "Functions",
    "summary": "Write your own functions and return values from them.",
    "cards": [
        card("Make your own function",
             "Write `fn`, a name, `()` and a body in braces. Call it by its name followed by `()`.",
             '''
fn greet() {
    println!("Hi!");
}

fn main() {
    greet();
}''',
             "A function can be written above or below `main`. Rust finds it either way."),
        card("Parameters need types",
             "Inputs go inside the parentheses, each with its type. Rust always asks for parameter types.",
             '''
fn show(n: i32) {
    println!("{n}");
}

fn main() {
    show(5);
}'''),
        card("Returning a value",
             "`-> i32` says what the function gives back. The last line, written without a semicolon, is the value returned.",
             '''
fn double(n: i32) -> i32 {
    n * 2
}

fn main() {
    println!("{}", double(4)); // 8
}''',
             "In Rust, a block's last expression is its value. No `return` needed."),
        card("The semicolon matters",
             "`n * 2;` with a semicolon is a statement, so it gives back nothing. The compiler will tell you the types don't match. `return` also works, usually to leave a function early.",
             '''
fn triple(n: i32) -> i32 {
    return n * 3;
}''', "Most Rust code uses the no-semicolon style for the final value."),
    ],
    "problems": [
        fill("Make this compile.", '''
fn add(a: i32, b: i32) __ i32 {
    a + b
}

fn main() {
    println!("{}", add(2, 3));
}''', ["->", ":", "=", "<-"], ["->"],
             "`-> i32` names the type a function returns.",
             "The return type follows a small arrow.", output=["5"], wrap=False),
        err("Which line causes the problem?", '''
fn square(n: i32) -> i32 {
    n * n;
}

fn main() {
    println!("{}", square(4));
}''', 2, "E0308",
            "The semicolon turns `n * n` into a statement, so the function gives back nothing instead of an `i32`. The compiler suggests removing it.",
            "Look closely at how the function ends."),
        out("What does this print?", '''
fn double(n: i32) -> i32 {
    n * 2
}

fn main() {
    let a = double(3);
    let b = double(a);
    println!("{a}");
    println!("{b}");
}''', ["3", "6", "9", "12"], ["6", "12"],
            "`double(3)` is 6, and `double(6)` is 12.",
            "`b` is made by doubling `a`, not 3.", wrap=False),
        order("Make the program print 12.", ["fn main() {"],
              ["    let w = 3;", "    let h = 4;", "    let a = area(w, h);", '    println!("{a}");'],
              ["}", "", "fn area(w: i32, h: i32) -> i32 {", "    w * h", "}"], ["12"],
              "Both sizes exist before calling `area`, and the print comes last.",
              "`area(w, h)` needs `w` and `h` to exist already."),
        fill("Fill in the return type.", '''
fn half(n: f64) -> __ {
    n / 2.0
}

fn main() {
    println!("{}", half(5.0));
}''', ["f64", "i32", "bool", "()"], ["f64"],
             "Half of an `f64` is still an `f64`: 2.5.",
             "What type is `n / 2.0` when `n` is an `f64`?", output=["2.5"], wrap=False),
        out("What does this print?", '''
fn add_one(n: i32) -> i32 {
    n + 1
}

fn twice(n: i32) -> i32 {
    add_one(add_one(n))
}

fn main() {
    println!("{}", twice(5));
}''', ["6", "7", "10", "12"], ["7"],
            "`add_one` runs twice on 5: 6, then 7.",
            "`twice` doesn't double. It calls `add_one` two times.", wrap=False),
    ],
})

# ─────────────────────────────── 4 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "control", "title": "Decisions and loops",
    "summary": "`if`, `loop`, `while` and `for`.",
    "cards": [
        card("if chooses a path",
             "`if` runs a block when its condition is true; `else` runs otherwise. No parentheses needed around the condition.",
             '''
let temp = 30;
if temp > 25 {
    println!("hot");
} else {
    println!("fine");
}''',
             "Compare with `==` `!=` `<` `>` `<=` `>=`. Join conditions with `&&` (and) or `||` (or)."),
        card("if gives back a value",
             "Like a function body, each branch's last expression is its value, so `if` can set a variable. Both branches must give the same type.",
             '''
let n = 4;
let size = if n > 3 { "big" } else { "small" };
println!("{size}"); // big'''),
        card("Repeat with loop and while",
             "`loop` repeats forever until `break`. `while` repeats as long as its condition is true.",
             '''
let mut n = 0;
while n < 3 {
    n += 1;
}
println!("{n}"); // 3''',
             "`n += 1` is short for `n = n + 1`. `-=` and `*=` work the same way."),
        card("Count with for",
             "`for` walks through a range. `1..4` means 1, 2, 3: it stops before 4. `1..=4` includes the 4.",
             '''
for i in 1..4 {
    println!("{i}"); // 1, then 2, then 3
}'''),
    ],
    "problems": [
        out("What does this print?", '''
for i in 1..4 {
    println!("{i}");
}''', ["0", "1", "2", "3", "4"], ["1", "2", "3"],
            "`1..4` stops before 4, so it prints 1, 2, 3.",
            "A range with `..` doesn't include its end."),
        err("Which line does the compiler reject?", '''
fn main() {
    let n = 5;
    if n {
        println!("yes");
    }
}''', 3, "E0308",
            "An `if` needs a `bool`. A number is not true or false in Rust. You'd write something like `if n > 0`.",
            "Look at what the `if` is checking."),
        fill("Print 1 to 5.", '''
for i in 1__5 {
    println!("{i}");
}''', ["..=", "..", "to", "-"], ["..="],
             "`1..=5` includes the 5.",
             "`1..5` would stop at 4. Which range includes its end?", output=["1", "2", "3", "4", "5"]),
        order("Count down: print 3, 2, 1.", ["fn main() {"],
              ["    let mut n = 3;", "    while n > 0 {", '        println!("{n}");', "        n -= 1;", "    }"],
              ["}"], ["3", "2", "1"],
              "Print first, then subtract. Swapping those two would print 2, 1, 0.",
              "Think about whether the print should happen before or after `n` goes down."),
        out("What does this print?", '''
let n = 7;
let kind = if n % 2 == 0 { "even" } else { "odd" };
println!("{kind}");''', ["even", "odd", "7", "1"], ["odd"],
            "7 % 2 is 1, not 0, so the `else` branch gives `\"odd\"`.",
            "`n % 2 == 0` checks for an even number. Is 7 even?"),
        fill("Make it print \"sorry\".", '''
let age = 20;
let has_ticket = false;
if age >= 18 __ has_ticket {
    println!("come in");
} else {
    println!("sorry");
}''', ["&&", "||", "and", "+"], ["&&"],
             "With `&&` both must be true. There's no ticket, so it's \"sorry\".",
             "Which operator needs both sides to be true?", output=["sorry"]),
        out("What does this print?", '''
let mut count = 0;
loop {
    count += 2;
    if count > 5 {
        break;
    }
}
println!("{count}");''', ["4", "5", "6", "8"], ["6"],
            "count goes 2, 4, 6. At 6 it's finally more than 5, so the loop stops.",
            "Step through: add 2, then check. When is it first more than 5?"),
    ],
})

# ─────────────────────────────── 5 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "text", "title": "Text",
    "summary": "`String` and `&str`, and how to grow text.",
    "cards": [
        card("Two kinds of text",
             "Text in quotes, like `\"hi\"`, is a `&str`: fixed text built into the program. A `String` is text you can change and grow.",
             '''
let fixed = "hello";              // &str
let name = String::from("Ana");   // String''',
             "`String::from` is a function that belongs to the `String` type. The `::` means \"belongs to\". Lesson 8 explains it fully."),
        card("Growing a String",
             "Call methods on a value with a dot. `push_str` adds text to the end. Since that changes the String, the variable must be `mut`.",
             '''
let mut s = String::from("Hi");
s.push_str(", Ana");
println!("{s}"); // Hi, Ana'''),
        card("Measuring text",
             "`.len()` gives the length in bytes. For plain English letters that's the number of letters.",
             '''
let word = String::from("crab");
println!("{}", word.len()); // 4''',
             "Letters with accents or emoji take more than one byte each. That's why it's called bytes, not letters."),
    ],
    "problems": [
        fill("Make this compile.", '''
let __ greeting = String::from("Hello");
greeting.push_str("!");
println!("{greeting}");''', ["mut", "&", "const", "String"], ["mut"],
             "`push_str` changes the String, so the variable needs `mut`.",
             "Line 2 changes `greeting`. What does a variable need to allow that?", output=["Hello!"]),
        err("Which line does the compiler reject?", '''
fn main() {
    let name = String::from("Kim");
    name.push_str(" Lee");
    println!("{name}");
}''', 3, "E0596",
            "`push_str` changes `name`, but `name` isn't `mut`. Same rule as numbers.",
            "Which line tries to change the text?"),
        out("What does this print?", '''
let word = String::from("crab");
println!("{}", word.len());''', ["3", "4", "5", "crab"], ["4"],
            "\"crab\" has 4 letters, so 4 bytes.",
            "`.len()` counts the letters here."),
        fill("Make it print \"hello world\".", '''
let mut s = String::from("hello");
s.__(" world");
println!("{s}");''', ["push_str", "push", "add", "len"], ["push_str"],
             "`push_str` adds a piece of text to the end.",
             "Which method adds text to a String?", output=["hello world"]),
        order("Make the program print \"Hi, Sam!\".", ["fn main() {"],
              ['    let mut msg = String::from("Hi");', '    msg.push_str(", Sam");', '    msg.push_str("!");', '    println!("{msg}");'],
              ["}"], ["Hi, Sam!"],
              "Make the String, add the pieces in order, then print it.",
              "The pieces are added to the end, one after another."),
        out("What does this print?", '''
let mut s = String::from("ab");
s.push_str("cd");
println!("{}", s.len());
println!("{s}");''', ["2", "4", "ab", "abcd"], ["4", "abcd"],
            "After the push, `s` is \"abcd\": 4 letters long.",
            "The length is measured after `push_str` runs."),
    ],
})

# ─────────────────────────────── 6 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "ownership", "title": "Ownership",
    "summary": "Why each value has exactly one owner.",
    "cards": [
        card("One owner at a time",
             "Every value is owned by one variable. When the owner's block ends at `}`, the value is cleaned up automatically.",
             '''
{
    let s = String::from("hi");
    println!("{s}");
}   // s is cleaned up here''',
             "This is how Rust manages memory without a garbage collector."),
        card("Assigning moves a String",
             "`let b = a;` moves the String into `b`. Now `b` is the owner, and `a` can't be used any more.",
             '''
let a = String::from("hi");
let b = a;          // moved
println!("{b}");    // fine
// println!("{a}"); would not compile'''),
        card("Small values are copied",
             "Numbers and `bool` are small, so assigning copies them instead. Both variables stay usable.",
             '''
let x = 5;
let y = x;          // copied
println!("{x} {y}"); // 5 5'''),
        card("clone makes a real copy",
             "To keep both Strings, call `.clone()`. It copies the text into a new String with its own owner.",
             '''
let a = String::from("hi");
let b = a.clone();
println!("{a} {b}"); // hi hi''',
             "Passing a String into a function moves it too, just like `let b = a;`."),
    ],
    "problems": [
        err("Which line does the compiler reject?", '''
fn main() {
    let s = String::from("hi");
    let t = s;
    println!("{t}");
    println!("{s}");
}''', 5, "E0382",
            "`let t = s;` moved the String into `t`. After a move, `s` can't be used.",
            "That line is fine. Follow who owns the String after line 3."),
        fill("Make this compile.", '''
let s = String::from("hi");
let t = s.__();
println!("{s}");
println!("{t}");''', ["clone", "copy", "move", "len"], ["clone"],
             "`.clone()` makes a second String, so `s` keeps its own.",
             "You need a real copy so both variables have text.", output=["hi", "hi"]),
        out("What does this print?", '''
let a = 5;
let mut b = a;
b += 1;
println!("{a} {b}");''', ["5 6", "6 6", "5 5", WONT], ["5 6"],
            "Numbers are copied, so `a` is still 5 and only `b` changes.",
            "Is a number moved or copied?"),
        err("Which line does the compiler reject?", '''
fn shout(text: String) {
    println!("{text}!");
}

fn main() {
    let word = String::from("hey");
    shout(word);
    shout(word);
}''', 8, "E0382",
            "The first call moved `word` into the function. There's nothing left to pass the second time.",
            "Calling a function with a String moves it. Which call has nothing left to give?"),
        order("Print the text from a, then from b.", ["fn main() {"],
              ['    let a = String::from("x");', '    println!("{a}");', "    let b = a;", '    println!("{b}");'],
              ["}"], ["x", "x"],
              "Use `a` before the move. After `let b = a;` only `b` works.",
              "Once `a` is moved into `b`, `a` can't be printed."),
        out("What does this print?", '''
let x = 1;
{
    let x = 2;
    println!("{x}");
}
println!("{x}");''', ["1", "2"], ["2", "1"],
            "The inner `x` only lives inside the braces. After `}`, the outer `x` (1) is back.",
            "A variable made inside `{ }` disappears at the `}`."),
    ],
})

# ─────────────────────────────── 7 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "borrowing", "title": "Borrowing",
    "summary": "Use a value without taking it: `&` and `&mut`.",
    "cards": [
        card("Borrow instead of taking",
             "`&s` lends `s` out without moving it. A function that takes `&String` can read the text, and the caller keeps it.",
             '''
fn count(text: &String) -> usize {
    text.len()
}

fn main() {
    let s = String::from("hello");
    let n = count(&s);
    println!("{s} has {n} letters");
}''',
             "`usize` is a whole-number type for sizes and counts. `.len()` returns one."),
        card("&str takes any text",
             "A `&str` parameter accepts both quoted text and a borrowed String, so it's the usual choice for reading text.",
             '''
fn hello(name: &str) {
    println!("Hi {name}");
}

fn main() {
    let owned = String::from("Ana");
    hello(&owned);
    hello("Bo");
}'''),
        card("&mut lets a borrower change it",
             "`&mut` is a borrow that's allowed to change the value. The variable itself must also be `mut`.",
             '''
fn add_bang(s: &mut String) {
    s.push_str("!");
}

fn main() {
    let mut s = String::from("hi");
    add_bang(&mut s);
    println!("{s}"); // hi!
}'''),
        card("One writer or many readers",
             "At any moment you can have one `&mut` borrow, or any number of `&` borrows, but not both. This rule stops two parts of a program from changing the same data at once.",
             '''
let mut s = String::from("a");
let r1 = &s;
let r2 = &s;          // fine: two readers
println!("{r1} {r2}");
let w = &mut s;       // fine: readers are done
w.push_str("b");''',
             "A borrow counts as \"in use\" until its last use, not until the end of the block."),
    ],
    "problems": [
        fill("Fill in the parameter type.", '''
fn shout(text: __) {
    println!("{text}!");
}

fn main() {
    let word = String::from("hey");
    shout(&word);
    shout(&word);
}''', ["&String", "String", "&mut String", "mut String"], ["&String"],
             "`shout` borrows with `&String`, so `word` can be lent out again.",
             "The calls pass `&word`. Which type matches a plain borrow?", output=["hey!", "hey!"], wrap=False),
        err("Which line does the compiler reject?", '''
fn main() {
    let mut s = String::from("a");
    let r1 = &mut s;
    let r2 = &mut s;
    r1.push_str("b");
    r2.push_str("c");
}''', 4, "E0499",
            "`r1` is still in use (line 5) when `r2` asks for a second `&mut`. Only one writer at a time.",
            "Look for where a second changing borrow starts while the first is still in use."),
        fill("Make it print \"hi!\".", '''
fn add_bang(s: &mut String) {
    s.push_str("!");
}

fn main() {
    let mut s = String::from("hi");
    add_bang(__);
    println!("{s}");
}''', ["&mut s", "&s", "s", "mut s"], ["&mut s"],
             "The function asks for `&mut String`, so you lend it with `&mut s`.",
             "Match what the function's parameter asks for.", output=["hi!"], wrap=False),
        out("What does this print?", '''
fn len_of(t: &str) -> usize {
    t.len()
}

fn main() {
    let a = String::from("rust");
    let n = len_of(&a);
    println!("{n} {a}");
}''', ["4 rust", "rust 4", "4", WONT], ["4 rust"],
            "`len_of` only borrows `a`, so `a` is still usable afterwards.",
            "`&a` lends the String. Does the caller still have it?", wrap=False),
        out("What does this print?", '''
let mut s = String::from("hi");
let r = &s;
s.push_str("!");
println!("{r}");''', ["hi", "hi!", WONT], [WONT],
            "`r` is still reading `s` when `push_str` tries to change it. Readers and a writer can't overlap.",
            "`r` is used on the last line, so the borrow is still active when `s` changes."),
        order("Make it print \"Ada Lovelace\", then 12.", ["fn main() {"],
              ['    let mut name = String::from("Ada");', "    add_title(&mut name);", '    println!("{name}");', '    println!("{}", name.len());'],
              ["}", "", "fn add_title(n: &mut String) {", '    n.push_str(" Lovelace");', "}"], ["Ada Lovelace", "12"],
              "Make the String, lend it to `add_title` to change, then print.",
              "The name has to be changed before it's printed."),
    ],
})

# ─────────────────────────────── 8 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "structs", "title": "Structs and methods",
    "summary": "Your own types, and what `Type::new()` means.",
    "cards": [
        card("Group data with struct",
             "A `struct` is your own type with named fields. Make one by giving every field a value; read a field with a dot.",
             '''
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    println!("{}", p.x); // 1
}'''),
        card("Methods live in impl",
             "Functions inside `impl Point { }` belong to `Point`. A method's first parameter is `&self`: a borrow of the value it's called on.",
             '''
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn total(&self) -> i32 {
        self.x + self.y
    }
}

fn main() {
    let p = Point { x: 1, y: 2 };
    println!("{}", p.total()); // 3
}''',
             "Use `&mut self` for a method that changes the value. The variable must then be `mut`."),
        card("Type::new() explained",
             "A function in `impl` with no `self` is called on the type with `::`. By convention a function that builds a new value is called `new`. `Self` is shorthand for the type's own name.",
             '''
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn new(x: i32, y: i32) -> Self {
        Point { x: x, y: y }
    }
}

fn main() {
    let p = Point::new(1, 2);
    println!("{}", p.y); // 2
}''',
             "`String::from(\"hi\")` from Lesson 5 is exactly this: a function belonging to `String`."),
    ],
    "problems": [
        fill("Make it print 4.", '''
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 3, y: 4 };
    println!("{}", p.__);
}''', ["y", "x", "0", "Point"], ["y"],
             "`p.y` reads the `y` field, which is 4.",
             "Which field holds 4?", output=["4"], wrap=False),
        err("Which line does the compiler reject?", '''
struct Counter {
    n: i32,
}

impl Counter {
    fn bump(&mut self) {
        self.n += 1;
    }
}

fn main() {
    let c = Counter { n: 0 };
    c.bump();
}''', 13, "E0596",
            "`bump` takes `&mut self`, but `c` isn't `mut`, so it can't be lent out for changing.",
            "The method is fine. Look at how it's called."),
        fill("Make this compile.", '''
struct Rect {
    w: i32,
    h: i32,
}

impl Rect {
    fn new(w: i32, h: i32) -> Self {
        Rect { w: w, h: h }
    }

    fn area(&self) -> i32 {
        self.w * self.h
    }
}

fn main() {
    let r = Rect__new(2, 5);
    println!("{}", r.area());
}''', ["::", ".", "->", ":"], ["::"],
             "`new` has no `self`, so it's called on the type: `Rect::new`.",
             "Functions that belong to a type are reached with two colons.", output=["10"], wrap=False),
        out("What does this print?", '''
struct Score {
    points: i32,
}

impl Score {
    fn add(&mut self, n: i32) {
        self.points += n;
    }
}

fn main() {
    let mut s = Score { points: 1 };
    s.add(4);
    s.add(5);
    println!("{}", s.points);
}''', ["1", "5", "9", "10"], ["10"],
            "1 + 4 + 5 = 10. Each call changes the same `s`.",
            "Each `add` call changes `s.points`. Start at 1.", wrap=False),
        order("Make it print \"Rex says woof\", then \"Rexy says woof\".",
              ["struct Dog {", "    name: String,", "}", "", "impl Dog {", "    fn new(name: &str) -> Self {",
               "        Dog { name: String::from(name) }", "    }", "", "    fn speak(&self) {",
               '        println!("{} says woof", self.name);', "    }", "}", "", "fn main() {"],
              ['    let mut d = Dog::new("Rex");', "    d.speak();", '    d.name.push_str("y");', "    d.speak();"],
              ["}"], ["Rex says woof", "Rexy says woof"],
              "Make the dog, speak, change the name, speak again.",
              "The name changes between the two speeches."),
        fill("Make this compile.", '''
struct Square {
    side: i32,
}

impl Square {
    fn area(__) -> i32 {
        self.side * self.side
    }
}

fn main() {
    let s = Square { side: 3 };
    println!("{}", s.area());
    println!("{}", s.area());
}''', ["&self", "self", "&mut self", "Self"], ["&self"],
             "`&self` only borrows the square, so `area` can be called again.",
             "Plain `self` takes ownership, so the second call would fail. `&mut self` needs `s` to be `mut`.",
             output=["9", "9"], wrap=False),
    ],
})

# ─────────────────────────────── 9 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "lists", "title": "Lists",
    "summary": "`Vec`: a list that grows, and `Vec::new()`.",
    "cards": [
        card("Vec holds a list",
             "`Vec::new()` makes an empty list, using the `new` idea from Lesson 8. `push` adds an item to the end, so the list must be `mut`.",
             '''
let mut v = Vec::new();
v.push(10);
v.push(20);
println!("{}", v.len()); // 2'''),
        card("vec! starts with items",
             "`vec![...]` makes a list with items already in it. Get an item by its position in square brackets. Positions start at 0.",
             '''
let nums = vec![4, 8, 15];
println!("{}", nums[0]); // 4
println!("{}", nums[2]); // 15''',
             "Asking for a position that doesn't exist stops the program with an error message."),
        card("Looping over a Vec",
             "`for n in &nums` borrows the list and visits each item. Without the `&`, the loop takes ownership and the list is gone afterwards.",
             '''
let nums = vec![1, 2, 3];
for n in &nums {
    println!("{n}");
}
println!("{}", nums.len()); // still usable'''),
        card("Vec<T> names what's inside",
             "The type of a list of `i32` is `Vec<i32>`. The angle brackets say what kind of item it holds.",
             '''
let mut names: Vec<String> = Vec::new();
names.push(String::from("Ana"));''',
             "Every item in a Vec has the same type."),
    ],
    "problems": [
        fill("Make this compile.", '''
let __ v = Vec::new();
v.push(1);
v.push(2);
println!("{}", v.len());''', ["mut", "&", "const", "Vec"], ["mut"],
             "`push` changes the list, so `v` must be `mut`.",
             "What does a variable need so it can change?", output=["2"]),
        out("What does this print?", '''
let nums = vec![4, 8, 15];
println!("{}", nums[1]);
println!("{}", nums.len());''', ["2", "3", "4", "8", "15"], ["8", "3"],
            "Positions start at 0, so `nums[1]` is the second item, 8. There are 3 items.",
            "Position 0 is the first item."),
        err("Which line does the compiler reject?", '''
fn main() {
    let nums = vec![1, 2, 3];
    for n in nums {
        println!("{n}");
    }
    println!("{}", nums.len());
}''', 6, "E0382",
            "`for n in nums` (no `&`) moved the list into the loop. Writing `&nums` would borrow it instead.",
            "The loop is fine on its own. What happened to `nums` during it?"),
        fill("Fill in the item type.", '''
let mut names: Vec<__> = Vec::new();
names.push(String::from("Ana"));
println!("{}", names[0]);''', ["String", "i32", "Vec", "str"], ["String"],
             "The list holds `String` values, so it's a `Vec<String>`.",
             "What type does `String::from` make?", output=["Ana"]),
        order("Add up the list and print 10.", ["fn main() {", "    let nums = vec![2, 3, 5];"],
              ["    let mut total = 0;", "    for n in &nums {", "        total += n;", "    }", '    println!("{total}");'],
              ["}"], ["10"],
              "Start the total at 0, add each item in the loop, print after the loop ends.",
              "The total must exist before the loop, and the print belongs after it."),
        out("What does this print?", '''
let mut v = vec![1];
v.push(2);
v.push(3);
println!("{}", v[v.len() - 1]);''', ["1", "2", "3", WONT], ["3"],
            "The list is [1, 2, 3], length 3. Position 3 − 1 = 2 is the last item: 3.",
            "`v.len() - 1` is the position of the last item."),
    ],
})

# ─────────────────────────────── 10 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "enums", "title": "Enums and match",
    "summary": "A value that's one of several choices, and handling each one.",
    "cards": [
        card("enum: one of several choices",
             "An `enum` lists every choice a value can be. Pick one with `::`.",
             '''
enum Light {
    Red,
    Yellow,
    Green,
}

let l = Light::Green;'''),
        card("match handles each choice",
             "`match` compares a value against patterns, top to bottom, and runs the first one that fits. `=>` separates a pattern from what to do.",
             '''
enum Light {
    Red,
    Yellow,
    Green,
}

let l = Light::Green;
match l {
    Light::Red => println!("stop"),
    Light::Yellow => println!("slow"),
    Light::Green => println!("go"),
}'''),
        card("match must cover everything",
             "If any choice is missing, the program won't compile. `_` matches anything that's left, which is handy for numbers and text.",
             '''
let n = 3;
match n {
    1 => println!("one"),
    2 => println!("two"),
    _ => println!("lots"),
}''',
             "Because patterns are tried in order, `_` goes last."),
        card("Choices can carry data",
             "Each choice can hold values. `match` pulls them out into names you can use. Like `if`, a `match` can give back a value.",
             '''
enum Shape {
    Circle(f64),
    Square(f64),
}

fn area(s: Shape) -> f64 {
    match s {
        Shape::Circle(r) => 3.14 * r * r,
        Shape::Square(side) => side * side,
    }
}'''),
    ],
    "problems": [
        fill("Make this compile.", '''
enum Coin {
    Penny,
    Dime,
}

fn value(c: Coin) -> i32 {
    match c {
        Coin::Penny __ 1,
        Coin::Dime => 10,
    }
}

fn main() {
    println!("{}", value(Coin::Dime));
}''', ["=>", "->", "=", ":"], ["=>"],
             "Each `match` arm is `pattern => value`.",
             "Look at the other arm for the right arrow.", output=["10"], wrap=False),
        err("Which line does the compiler reject?", '''
enum Dir {
    Up,
    Down,
    Left,
}

fn main() {
    let d = Dir::Left;
    match d {
        Dir::Up => println!("up"),
        Dir::Down => println!("down"),
    }
}''', 9, "E0004",
            "`Dir::Left` isn't handled, so the `match` doesn't cover every choice.",
            "Every arm is fine on its own. Is any choice missing?"),
        order("Make it print \"two\".", ["fn main() {", "    let n = 2;", "    match n {"],
              ['        1 => println!("one"),', '        2 => println!("two"),', '        _ => println!("many"),'],
              ["    }", "}"], ["two"],
              "Arms are tried top to bottom and `_` catches everything, so the `2` arm has to come before `_`. Putting `_` last is the usual habit.",
              "Arms are tried top to bottom. What happens if `_` comes first?"),
        out("What does this print?", '''
enum Shape {
    Square(i32),
    Rect(i32, i32),
}

fn area(s: Shape) -> i32 {
    match s {
        Shape::Square(side) => side * side,
        Shape::Rect(w, h) => w * h,
    }
}

fn main() {
    println!("{}", area(Shape::Rect(2, 3)));
    println!("{}", area(Shape::Square(4)));
}''', ["5", "6", "8", "16"], ["6", "16"],
            "A 2 × 3 rectangle is 6; a square with side 4 is 16.",
            "Each shape uses its own arm. A square multiplies its side by itself.", wrap=False),
        fill("Make it compile and print \"Saturday\".", '''
let day = 6;
let kind = match day {
    6 => "Saturday",
    7 => "Sunday",
    __ => "weekday",
};
println!("{kind}");''', ["_", "else", "*", "0"], ["_"],
             "`_` covers every other number, so the `match` is complete.",
             "A number has far too many values to list. Which pattern matches anything?", output=["Saturday"]),
        out("What does this print?", '''
enum Light {
    Red,
    Green,
}

fn main() {
    let l = Light::Red;
    let action = match l {
        Light::Red => "stop",
        Light::Green => "go",
    };
    println!("{action}");
}''', ["stop", "go", "Red", WONT], ["stop"],
            "`l` is `Red`, so the `match` gives `\"stop\"`.",
            "The match gives back the value from the arm that fits.", wrap=False),
    ],
})

# ─────────────────────────────── 11 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "errors", "title": "Missing values and errors",
    "summary": "`Option`, `Result` and the `?` operator.",
    "cards": [
        card("Option: maybe a value",
             "Rust has no null. A value that might be missing is an `Option`: either `Some(value)` or `None`. Asking a Vec for a position with `.get` gives one.",
             '''
let nums = vec![10, 20];
let a = nums.get(1);  // Some(20)
let b = nums.get(5);  // None, no crash'''),
        card("Open an Option with match",
             "To use the value, `match` on both cases. The compiler won't let you forget `None`.",
             '''
let nums = vec![10, 20];
match nums.get(5) {
    Some(n) => println!("found {n}"),
    None => println!("nothing there"),
}'''),
        card("Result: worked or failed",
             "A `Result` is either `Ok(value)` or `Err(problem)`. Functions that can fail return one. `Result<i32, String>` means success gives an `i32` and failure gives a `String`.",
             '''
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("divide by zero"))
    } else {
        Ok(a / b)
    }
}'''),
        card("? passes the error along",
             "Inside a function that returns `Result`, writing `?` after a call gives you the value if it's `Ok`, or returns the `Err` straight away.",
             '''
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        return Err(String::from("divide by zero"));
    }
    Ok(a / b)
}

fn half_of_div(a: i32, b: i32) -> Result<i32, String> {
    let d = divide(a, b)?;  // stops here on Err
    Ok(d / 2)
}

fn main() {
    match half_of_div(10, 0) {
        Ok(v) => println!("{v}"),
        Err(e) => println!("{e}"), // divide by zero
    }
}''',
             "`.unwrap()` also takes the value out, but crashes the program on `None` or `Err`. It's fine for quick experiments."),
    ],
    "problems": [
        fill("Make it print 4.", '''
fn even(n: i32) -> Option<i32> {
    if n % 2 == 0 {
        __(n)
    } else {
        None
    }
}

fn main() {
    match even(4) {
        Some(x) => println!("{x}"),
        None => println!("none"),
    }
}''', ["Some", "Ok", "Option", "return"], ["Some"],
             "The function returns an `Option`, so a found value is `Some(n)`.",
             "The other branch gives `None`. What's its partner?", output=["4"], wrap=False),
        out("What does this print?", '''
let nums = vec![10, 20];
match nums.get(5) {
    Some(n) => println!("{n}"),
    None => println!("nothing"),
}''', ["10", "20", "nothing", WONT], ["nothing"],
            "There's no position 5, so `.get(5)` is `None`. No crash.",
            "The list only has positions 0 and 1."),
        err("Which line does the compiler reject?", '''
fn main() {
    let nums = vec![1, 2, 3];
    let first = nums.get(0);
    let doubled = first * 2;
    println!("{doubled}");
}''', 4, "E0369",
            "`first` is an `Option`, not a number. You have to open it with `match` (or similar) before doing maths.",
            "What type does `.get` give back?"),
        fill("Make this compile.", '''
fn half(n: i32) -> Result<i32, String> {
    if n % 2 == 0 {
        Ok(n / 2)
    } else {
        Err(String::from("odd"))
    }
}

fn quarter(n: i32) -> Result<i32, String> {
    let h = half(n)__;
    half(h)
}

fn main() {
    match quarter(8) {
        Ok(v) => println!("{v}"),
        Err(e) => println!("error: {e}"),
    }
}''', ["?", "!", ".clone()"], ["?"],
             "`half(n)?` gives the number inside `Ok`, or returns the `Err` from `quarter` early.",
             "`half(h)` needs a plain number. Which symbol takes it out of the `Result`?", output=["2"], wrap=False),
        out("What does this print?", '''
fn half(n: i32) -> Result<i32, String> {
    if n % 2 == 0 {
        Ok(n / 2)
    } else {
        Err(String::from("odd"))
    }
}

fn quarter(n: i32) -> Result<i32, String> {
    let h = half(n)?;
    half(h)
}

fn main() {
    match quarter(6) {
        Ok(v) => println!("{v}"),
        Err(e) => println!("error: {e}"),
    }
}''', ["1", "3", "error: odd", WONT], ["error: odd"],
            "half(6) is 3, but half(3) fails because 3 is odd, so `quarter` gives the `Err`.",
            "Work it through: half of 6, then half of that.", wrap=False),
        order("Make it print \"negative\", then 30.", ["fn check(age: i32) -> Result<i32, String> {"],
              ["    if age < 0 {", '        return Err(String::from("negative"));', "    }", "    Ok(age)"],
              ["}", "", "fn main() {", "    for age in vec![-1, 30] {", "        match check(age) {", '            Ok(a) => println!("{a}"),', '            Err(e) => println!("{e}"),', "        }", "    }", "}"],
              ["negative", "30"],
              "Check first and leave early with `return Err`. The final `Ok(age)` is the value when all is well.",
              "The last line of the function is its value, so the happy path goes at the end."),
    ],
})

# ─────────────────────────────── 12 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "traits", "title": "Traits and iterators",
    "summary": "Shared behaviour, tiny inline functions, and chains.",
    "cards": [
        card("Traits: a promise of methods",
             "A `trait` lists methods a type promises to have. It only names them; each type writes its own version.",
             '''
trait Speak {
    fn speak(&self) -> String;
}'''),
        card("impl Trait for Type",
             "`impl Speak for Dog` keeps the promise for `Dog`. Every method in the trait must be written.",
             '''
trait Speak {
    fn speak(&self) -> String;
}

struct Dog {
    name: String,
}

impl Speak for Dog {
    fn speak(&self) -> String {
        String::from("woof")
    }
}'''),
        card("Closures: small inline functions",
             "A closure is a function without a name. Its parameters go between pipes. You can store it in a variable and call it.",
             '''
let double = |x| x * 2;
println!("{}", double(4)); // 8'''),
        card("Iterators chain steps",
             "`.iter()` goes through a list item by item. Chain steps onto it: `map` changes each item using a closure, `sum` adds them up, `max` finds the biggest.",
             '''
let nums = vec![1, 2, 3];
let total: i32 = nums.iter().map(|n| n * 2).sum();
println!("{total}"); // 12''',
             "`max` gives an `Option`, because an empty list has no biggest item."),
    ],
    "problems": [
        fill("Make this compile.", '''
trait Greet {
    fn hello(&self) -> String;
}

struct Cat {
    name: String,
}

impl Greet __ Cat {
    fn hello(&self) -> String {
        self.name.clone()
    }
}

fn main() {
    let c = Cat { name: String::from("Tom") };
    println!("{}", c.hello());
}''', ["for", "to", "in", ":"], ["for"],
             "It reads as a sentence: implement `Greet` for `Cat`.",
             "Say it out loud: implement Greet ___ Cat.", output=["Tom"], wrap=False),
        err("Which line does the compiler reject?", '''
trait Shape {
    fn area(&self) -> i32;
    fn sides(&self) -> i32;
}

struct Square {
    side: i32,
}

impl Shape for Square {
    fn area(&self) -> i32 {
        self.side * self.side
    }
}

fn main() {
    let s = Square { side: 2 };
    println!("{}", s.area());
}''', 10, "E0046",
            "The trait promises `sides` too, but this `impl` only writes `area`.",
            "Compare what the trait asks for with what the `impl` provides."),
        out("What does this print?", '''
let add = |a, b| a + b;
let x = add(2, 3);
println!("{}", add(x, x));''', ["5", "6", "10", "25"], ["10"],
            "`x` is 5, and `add(5, 5)` is 10.",
            "Work out `x` first, then add it to itself."),
        out("What does this print?", '''
let nums = vec![1, 2, 3];
let total: i32 = nums.iter().map(|n| n * 10).sum();
println!("{total}");''', ["6", "60", "123", WONT], ["60"],
            "Each item becomes 10, 20, 30, and the sum is 60.",
            "`map` changes every item before `sum` adds them."),
        fill("Make it print the largest number.", '''
let nums = vec![4, 9, 2];
match nums.iter().__() {
    Some(n) => println!("{n}"),
    None => println!("empty"),
}''', ["max", "sum", "len", "map"], ["max"],
             "`max` gives `Some` of the biggest item: 9.",
             "Which step finds the biggest item and returns an `Option`?", output=["9"]),
        order("Make it print 12.",
              ["trait Area {", "    fn area(&self) -> i32;", "}", "", "struct Rect {", "    w: i32,", "    h: i32,", "}", ""],
              ["impl Area for Rect {", "    fn area(&self) -> i32 {", "        self.w * self.h", "    }", "}"],
              ["", "fn main() {", "    let r = Rect { w: 3, h: 4 };", '    println!("{}", r.area());', "}"], ["12"],
              "The `impl` block wraps the method, and the method wraps its body.",
              "Each `{` needs its matching `}` in the right place."),
    ],
})

# ─────────────────────────────── 13 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "generics", "title": "Generics and lifetimes",
    "summary": "One function for many types, and how long a borrow lasts.",
    "cards": [
        card("One function, many types",
             "A name in angle brackets after the function name, usually `T`, stands for \"any type\". The caller decides what `T` is.",
             '''
fn pick<T>(first: T, second: T, take_first: bool) -> T {
    if take_first { first } else { second }
}

fn main() {
    println!("{}", pick(1, 2, true));       // 1
    println!("{}", pick("a", "b", false));  // b
}''',
             "This is called a generic. `Vec<T>` from Lesson 9 works the same way."),
        card("Generic structs",
             "Structs can be generic too. `T` is filled in when you make one.",
             '''
struct Pair<T> {
    a: T,
    b: T,
}

let nums = Pair { a: 1, b: 2 };       // Pair<i32>
let words = Pair { a: "x", b: "y" };  // Pair<&str>''',
             "Methods on a generic struct start with `impl<T> Pair<T>`."),
        card("Bounds: what T must be able to do",
             "Inside a generic function, Rust only lets you do what every possible `T` can do. A bound like `T: PartialOrd` says \"only types that can be compared with < and >\".",
             '''
fn largest<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}''',
             "Bounds are traits from Lesson 12. Others you'll see: `Clone`, `Copy`, `Display` (can be printed with `{}`)."),
        card("Lifetimes: how long a borrow lasts",
             "When a function takes two borrows and returns one of them, Rust needs to know the result can't outlive the inputs. A lifetime name like `'a` says so.",
             '''
fn longer<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}''',
             "Read `'a` as \"lives at least as long as\". Most of the time Rust works lifetimes out itself; you only write them when it asks."),
    ],
    "problems": [
        fill("Make this generic function compile.", '''
fn pick<__>(first: T, second: T, take_first: bool) -> T {
    if take_first { first } else { second }
}

fn main() {
    println!("{}", pick(3, 7, false));
    println!("{}", pick("x", "y", true));
}''', ["T", "i32", "'a", "_"], ["T"],
             "`<T>` introduces the name `T`, which the parameters then use.",
             "The parameters use a type called `T`. Where does that name come from?", output=["7", "x"], wrap=False),
        err("Which line does the compiler reject?", '''
fn largest<T>(a: T, b: T) -> T {
    if a > b {
        a
    } else {
        b
    }
}

fn main() {
    println!("{}", largest(3, 9));
}''', 2, "E0369",
            "Not every type can be compared with `>`, so a plain `T` isn't allowed to. It needs a bound.",
            "The signature is fine on its own. Which line does something not every type can do?"),
        fill("Add the bound that makes `>` work.", '''
fn largest<T: __>(a: T, b: T) -> T {
    if a > b {
        a
    } else {
        b
    }
}

fn main() {
    println!("{}", largest(3, 9));
}''', ["PartialOrd", "Display", "Clone", "Copy"], ["PartialOrd"],
             "`PartialOrd` is the trait for `<` and `>`.",
             "Which trait is about comparing with greater and less than?", output=["9"], wrap=False),
        err("Which line does the compiler reject?", '''
fn longer(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    println!("{}", longer("hi", "hello"));
}''', 1, "E0106",
            "The result is a borrow of either `x` or `y`, and Rust can't tell which. It asks for a lifetime.",
            "The body is fine. Rust needs more information in the signature."),
        fill("Finish the lifetime.", '''
fn longer<'a>(x: &'a str, y: &'a str) -> &__ str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    println!("{}", longer("hi", "hello"));
}''', ["'a", "a", "T", "mut"], ["'a"],
             "The result lives as long as `'a`, the same as both inputs.",
             "The return type needs the same lifetime name as the inputs.", output=["hello"], wrap=False),
        out("What does this print?", '''
struct Pair<T> {
    a: T,
    b: T,
}

impl<T> Pair<T> {
    fn swap(self) -> Pair<T> {
        Pair { a: self.b, b: self.a }
    }
}

fn main() {
    let p = Pair { a: 1, b: 2 }.swap();
    println!("{} {}", p.a, p.b);
}''', ["1 2", "2 1", "2 2", WONT], ["2 1"],
            "`swap` builds a new `Pair` with the fields the other way round.",
            "Look at which field goes where in `swap`.", wrap=False),
    ],
})

# ─────────────────────────────── 14 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "modules", "title": "Modules, use and derive",
    "summary": "The lines at the top of every real Rust file.",
    "cards": [
        card("use brings names in",
             "Rust's standard library is organised into modules, and `::` walks through them. `use` brings a name in so you can write it short.",
             '''
use std::cmp::max;

fn main() {
    println!("{}", max(3, 8));            // 8
    println!("{}", std::cmp::min(3, 8));  // 3, full path, no use
}''',
             "`std` is the standard library. Real files usually start with a few `use` lines."),
        card("mod groups your own code",
             "`mod` makes a module. Everything inside is private unless marked `pub`, so you choose what the rest of the program can reach.",
             '''
mod shapes {
    pub fn area(w: i32, h: i32) -> i32 {
        w * h
    }
}

fn main() {
    println!("{}", shapes::area(2, 3)); // 6
}''',
             "In bigger projects each module usually lives in its own file."),
        card("#[derive] writes code for you",
             "`#[derive(Debug)]` above a struct adds the ability to print it with `{:?}`, which shows every field.",
             '''
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// println!("{:?}", Point { x: 1, y: 2 });
// prints: Point { x: 1, y: 2 }'''),
        card("The usual derives",
             "`Clone` adds `.clone()`. `PartialEq` adds `==`. `Debug` adds `{:?}`. You'll often see several at once.",
             '''
#[derive(Debug, Clone, PartialEq)]
struct Color {
    r: u8,
    g: u8,
    b: u8,
}''',
             "`u8` is a small whole number from 0 to 255, handy for colours."),
    ],
    "problems": [
        fill("Make it print 9.", '''
use std::cmp::__;

fn main() {
    println!("{}", max(4, 9));
}''', ["max", "min", "Max", "cmp"], ["max"],
             "`use std::cmp::max;` brings in exactly the name the code calls.",
             "The code calls `max`. Which name has to be brought in?", output=["9"], wrap=False),
        err("Which line does the compiler reject?", '''
mod bank {
    fn balance() -> i32 {
        100
    }
}

fn main() {
    println!("{}", bank::balance());
}''', 8, "E0603",
            "`balance` isn't `pub`, so code outside `bank` can't call it.",
            "The function is fine inside its module. Who's allowed to call it?"),
        out("What does this print?", '''
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    println!("{:?}", p);
}''', ["Point { x: 1, y: 2 }", "(1, 2)", "1 2", WONT], ["Point { x: 1, y: 2 }"],
            "`{:?}` with `Debug` prints the type name and every field.",
            "Debug printing shows the struct the way you'd write it.", wrap=False),
        err("Which line does the compiler reject?", '''
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    println!("{:?}", p);
}''', 8, "E0277",
            "`Point` has no `#[derive(Debug)]`, so `{:?}` doesn't know how to print it.",
            "Compare with the last problem. What's missing above the struct?"),
        fill("Make it print true.", '''
#[derive(__)]
struct Color {
    r: u8,
    g: u8,
    b: u8,
}

fn main() {
    let a = Color { r: 1, g: 2, b: 3 };
    let b = Color { r: 1, g: 2, b: 3 };
    println!("{}", a == b);
}''', ["PartialEq", "Debug", "Clone", "Eq"], ["PartialEq"],
             "`PartialEq` adds `==`, comparing every field.",
             "Which derive adds `==`?", output=["true"], wrap=False),
        order("Make it print \"hello\".", [],
              ["mod greet {", "    pub fn hello() {", '        println!("hello");', "    }", "}"],
              ["", "fn main() {", "    greet::hello();", "}"], ["hello"],
              "The module wraps the function, and the function wraps the print.",
              "Each `{` needs its matching `}`, and code that runs must be inside a function."),
    ],
})

# ─────────────────────────────── 15 ───────────────────────────────
COURSE.append({
    "part": 1, "id": "hashmaps", "title": "Maps",
    "summary": "`HashMap`: look values up by a key.",
    "cards": [
        card("HashMap: look things up by key",
             "A `HashMap` stores pairs: a key and its value. `insert` adds a pair; inserting the same key again replaces its value.",
             '''
use std::collections::HashMap;

fn main() {
    let mut ages = HashMap::new();
    ages.insert("Ana", 31);
    ages.insert("Bo", 27);
    println!("{}", ages.len()); // 2
}'''),
        card("Getting a value gives an Option",
             "The key might not be there, so `get` returns an `Option`, just like `.get` on a Vec in Lesson 11.",
             '''
use std::collections::HashMap;

let mut ages = HashMap::new();
ages.insert("Ana", 31);
match ages.get("Ana") {
    Some(age) => println!("{age}"),  // 31
    None => println!("not found"),
}'''),
        card("Counting with entry",
             "`entry(key).or_insert(0)` finds the value for a key, adding 0 first if it's missing. It gives back a `&mut` to the value; the `*` in front means \"the value itself\", so `+= 1` changes it.",
             '''
use std::collections::HashMap;

let mut counts = HashMap::new();
for w in vec!["a", "b", "a"] {
    *counts.entry(w).or_insert(0) += 1;
}
// counts: "a" -> 2, "b" -> 1''',
             "This is the standard way to count things in Rust."),
        card("Looping over a HashMap",
             "`for (key, value) in &map` visits every pair. The two names in brackets unpack each pair.",
             '''
use std::collections::HashMap;

let mut ages = HashMap::new();
ages.insert("Ana", 31);
ages.insert("Bo", 27);
for (name, age) in &ages {
    println!("{name} is {age}");
}''',
             "The order is not the order you inserted them, and can change between runs. Don't rely on it."),
    ],
    "problems": [
        fill("Make it print 1.", '''
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.__("red", 3);
    println!("{}", scores.len());
}''', ["insert", "push", "add", "get"], ["insert"],
             "`insert` adds a key and its value.",
             "`push` is for a Vec. Which method adds a pair to a map?", output=["1"], wrap=False),
        out("What does this print?", '''
use std::collections::HashMap;

fn main() {
    let mut stock = HashMap::new();
    stock.insert("apple", 5);
    match stock.get("pear") {
        Some(n) => println!("{n}"),
        None => println!("none left"),
    }
}''', ["5", "0", "none left", WONT], ["none left"],
            "There's no \"pear\" key, so `get` gives `None`.",
            "Which key was inserted, and which one is asked for?", wrap=False),
        out("What does this print?", '''
use std::collections::HashMap;

fn main() {
    let mut m = HashMap::new();
    m.insert("a", 1);
    m.insert("a", 2);
    println!("{}", m.len());
    match m.get("a") {
        Some(v) => println!("{v}"),
        None => println!("none"),
    }
}''', ["1", "2"], ["1", "2"],
            "Inserting the same key again replaces the value, so there's still 1 pair, now holding 2.",
            "A key can only appear once in a map.", wrap=False),
        err("Which line does the compiler reject?", '''
fn main() {
    let mut m = HashMap::new();
    m.insert("k", 1);
}''', 2, "E0433",
            "`HashMap` isn't brought in automatically. It needs `use std::collections::HashMap;` at the top.",
            "Which name has Rust never been told about?"),
        order("Count the words and print how many \"a\"s there are: 2.",
              ["use std::collections::HashMap;", "", "fn main() {", '    let words = vec!["a", "b", "a"];'],
              ["    let mut counts = HashMap::new();", "    for w in words {", "        *counts.entry(w).or_insert(0) += 1;", "    }"],
              ['    match counts.get("a") {', '        Some(n) => println!("{n}"),', '        None => println!("0"),', "    }", "}"], ["2"],
              "Make the empty map, then loop and count each word.",
              "The map has to exist before the loop can count into it."),
        fill("Make it print 3.", '''
use std::collections::HashMap;

fn main() {
    let mut counts = HashMap::new();
    for w in vec!["x", "y", "x", "x"] {
        *counts.entry(w).__(0) += 1;
    }
    match counts.get("x") {
        Some(n) => println!("{n}"),
        None => println!("0"),
    }
}''', ["or_insert", "insert", "get", "unwrap"], ["or_insert"],
             "`or_insert(0)` starts a missing word at 0, then `+= 1` counts it.",
             "You need the step that adds a starting value when the key is missing.", output=["3"], wrap=False),
    ],
})

# ─────────────────────────────── 16 ───────────────────────────────
# Adapted from Akira Nishikawa's Rust Compile Challenge (MIT license). See README, Credits.
COURSE.append({
    "part": 1, "id": "fixit", "title": "Fix the compiler",
    "summary": "Real puzzles: programs the compiler rejects, and the one change that fixes each.",
    "cards": [
        card("Every problem here is broken",
             "Each program in this lesson fails to compile. Your job: find the line, or pick the one change that makes it work. They use everything from the earlier lessons.",
             '''
let mut total = 0;
total += 5;
println!("{total}");  // 5''',
             "Take out `mut` and Rust stops with error E0384: you can't change a variable that isn't `mut`."),
        card("The error code is a clue",
             "Every compiler error has a code like `E0382`. The same mistake always gets the same code, so you start to recognise them.",
             '''
let s = String::from("hi");
let t = s.clone();  // without .clone(): E0382, s was moved
println!("{s} {t}");''',
             "On a computer, `rustc --explain E0382` prints a long explanation of any code. These puzzles come from Akira Nishikawa's Rust Compile Challenge."),
    ],
    "problems": [
        fill("Pick the fix so it counts to 3.", '''
fn main() {
    let __ = 0;
    while count < 3 {
        count += 1;
        println!("count={count}");
    }
}''', ["mut count", "count", "ref count", "const count"], ["mut count"],
             "`count` changes inside the loop, so it has to be `mut`.",
             "Which line changes `count`? A variable can only change if it says so.",
             output=["count=1", "count=2", "count=3"], wrap=False),
        fill("Pick the fix so the match works.", '''
fn square(x: Option<i64>) -> Option<i64> {
    match x {
        __(i) => Some(i * i),
        None => None,
    }
}

fn main() {
    println!("{}", square(Some(8)).unwrap_or(0));
}''', ["Some", "Ok", "Err", "None"], ["Some"],
             "An `Option` is either `Some` or `None`. `Ok` and `Err` belong to `Result`.",
             "Look at the type of `x`. Which two shapes can it have?", output=["64"], wrap=False),
        fill("Pick the fix so the list still prints after the loop.", '''
fn main() {
    let scores = vec![100, 92, 84];
    for score in __ {
        println!("{score}");
    }
    println!("{:?}", scores);
}''', ["&scores", "scores", "scores.into_iter()", "*scores"], ["&scores"],
             "Looping over `&scores` only borrows the list, so it's still there for the last line.",
             "Looping over `scores` itself moves the list into the loop. How do you just borrow it?",
             output=["100", "92", "84", "[100, 92, 84]"], wrap=False),
        fill("Pick the fix so every score goes up by 10.", '''
fn main() {
    let mut scores = vec![100, 92, 84];
    for score in scores.iter_mut() {
        __ += 10;
    }
    println!("{:?}", scores);
}''', ["*score", "score", "&score", "mut score"], ["*score"],
             "`iter_mut` hands you a `&mut` to each number. `*score` means the number itself, so `+= 10` changes it.",
             "`score` is a reference, not a number. How do you reach the value behind it?",
             output=["[110, 102, 94]"], wrap=False),
        fill("Pick the fix so it prints the zodiac animal for 2031.", '''
const ANIMALS: [&str; 12] = [
    "monkey", "rooster", "dog", "pig",
    "rat", "ox", "tiger", "rabbit",
    "dragon", "snake", "horse", "goat",
];

fn main() {
    let year: u32 = 2031;
    let i = year % 12;
    println!("{}", ANIMALS[i as __]);
}''', ["usize", "u32", "i64", "u8"], ["usize"],
             "Rust only lets you index an array with a `usize`, so `i` is turned into one with `as usize`.",
             "Only one number type is allowed inside `[ ]`. Which one is made for positions?",
             output=["pig"], wrap=False),
        err("Which line does the compiler reject?", '''
struct Point {
    x: i32,
    y: i32,
}

fn add(p1: Point, p2: Point) -> Point {
    p1.x += p2.x;
    p1.y += p2.y;
    p1
}

fn main() {
    let p = add(Point { x: 1, y: 3 }, Point { x: 2, y: 4 });
    println!("{} {}", p.x, p.y);
}''', 7, "E0594",
            "`p1` is a parameter without `mut`, so its fields can't change. The fix: `fn add(mut p1: Point, ...)`.",
            "Look for the first line that changes something. Was that thing allowed to change?"),
        fill("Pick the fix so it prints hello.", '''
fn main() {
    let a = Some(String::from("hello"));
    println!("{}", a.__);
}''', ["unwrap()", "clone()", "to_string()", "len()"], ["unwrap()"],
             "`a` is an `Option`, which `{}` can't print. `unwrap()` takes the String out of the `Some`.",
             "`{}` can print a String but not an Option. How do you get the String out?",
             output=["hello"], wrap=False),
        fill("Pick the fix so it prints the value at position 4.", '''
fn get(list: &[i32], index: __) -> Option<&i32> {
    list.get(index)
}

fn main() {
    let values = [1, 2, 5, 10, 15];
    println!("{:?}", get(&values, 4));
}''', ["usize", "i64", "u32", "i32"], ["usize"],
             "`get` takes a position, and positions are always `usize`.",
             "Same rule as indexing: which number type stands for a position?",
             output=["Some(15)"], wrap=False),
        err("Which line does the compiler reject?", '''
use std::fmt::Display;

struct Pair<T> { a: T, b: T }
struct Note { n: i32 }

trait Show { fn show(&self); }

impl<T: Display> Show for Pair<T> {
    fn show(&self) { println!("{} {}", self.a, self.b); }
}

fn main() {
    let p = Pair { a: 1, b: 2 };
    p.show();
    let q = Pair { a: Note { n: 1 }, b: Note { n: 2 } };
    q.show();
}''', 16, "E0599",
            "`show` only exists for a `Pair` whose `T` is `Display`. `Note` isn't, so `q` has no `show`.",
            "Look at the `impl` line: it only covers some kinds of `Pair`. Which pair isn't one of them?"),
        fill("Pick the fix so pop can change the list.", '''
fn main() {
    let mut a = vec![3, 2, 1];
    a.push(4);
    let b = __;
    println!("{:?}", b.pop());
}''', ["&mut a", "&a", "&a[0]", "*a"], ["&mut a"],
             "`pop` changes the list, so `b` needs a mutable borrow: `&mut a`.",
             "A plain `&` borrow can only look. `pop` needs to change the list.",
             output=["Some(4)"], wrap=False),
        err("Which line does the compiler reject?", '''
#[derive(Debug)]
struct Person {
    name: &str,
}

fn main() {
    let p = Person { name: "Mia" };
    println!("{:?}", p);
}''', 3, "E0106",
            "A struct holding a borrow has to say how long it lives: `struct Person<'a> { name: &'a str }`.",
            "`main` is fine. Which line holds a borrow without a lifetime?"),
        fill("Pick the fix so the struct can hold a borrowed name.", '''
struct Person<'a> {
    name: &__ str,
}

impl<'a> Person<'a> {
    fn name(&self) -> &str {
        self.name
    }
}

fn main() {
    let p = Person { name: "Mia" };
    println!("{}", p.name());
}''', ["'a", "'b", "'_", "mut"], ["'a"],
             "The struct declares `'a`, and the field uses it: `&'a str`.",
             "Use the lifetime the struct already names in `<' '>`.",
             output=["Mia"], wrap=False),
        fill("Pick the fix so the function can return text.", '''
fn hello() -> &__ str {
    "hello world"
}

fn main() {
    println!("{}", hello());
}''', ["'static", "'a", "'_", "mut"], ["'static"],
             "Text in quotes lives for the whole program. That lifetime is called `'static`.",
             "There's no input to borrow from. How long does text in quotes live?",
             output=["hello world"], wrap=False),
        fill("Pick the fix so say() works for any car.", '''
trait Car { fn speed(&self) -> i32; }

struct Van { speed: i32 }

impl Car for Van {
    fn speed(&self) -> i32 { self.speed }
}

struct Owner<T: Car> { car: T }

impl__ Owner<T> {
    fn say(&self) { println!("{}", self.car.speed()); }
}

fn main() {
    let o = Owner { car: Van { speed: 100 } };
    o.say();
}''', ["<T: Car>", "<T>", "<Van>", "<Car>"], ["<T: Car>"],
             "The struct only allows a `T` that is a `Car`, so the `impl` must promise the same: `impl<T: Car>`.",
             "Compare with the `struct Owner` line. What does it require of `T`?",
             output=["100"], wrap=False),
        err("Which line does the compiler reject?", '''
struct Pair<T, T> {
    a: T,
    b: T,
}

fn main() {
    let x = Pair { a: 1, b: "two" };
    println!("{} {}", x.a, x.b);
}''', 1, "E0403",
            "Two type parameters can't share a name. Call them `<T, U>`, and give `b` the type `U`.",
            "Look at the names inside `< >`."),
        fill("Pick the fix so a and b can be different types.", '''
struct Pair<T, U> {
    a: T,
    b: __,
}

fn main() {
    let x = Pair { a: 1, b: "two" };
    println!("{} {}", x.a, x.b);
}''', ["U", "T", "i32", "String"], ["U"],
             "`a` is a number and `b` is text, so they need different type parameters: `T` and `U`.",
             "`b` holds text in quotes. Which type covers it without forcing it to match `a`?",
             output=["1 two"], wrap=False),
        fill("Pick the fix so speed_of takes any car.", '''
trait Car { fn speed(&self) -> i32; }

struct Bike { speed: i32 }

impl Car for Bike {
    fn speed(&self) -> i32 { self.speed }
}

fn speed_of<T: __>(c: T) -> i32 {
    c.speed()
}

fn main() {
    println!("{}", speed_of(Bike { speed: 30 }));
}''', ["Car", "Display", "Clone", "Copy"], ["Car"],
             "`speed_of` calls `.speed()`, which only a `Car` has. `T: Car` promises it.",
             "Which trait gives `c` the `speed` method?",
             output=["30"], wrap=False),
        fill("Pick the fix so main can call hello.", '''
mod greet {
    __ fn hello() {
        println!("hello");
    }
}

fn main() {
    greet::hello();
}''', ["pub", "use", "mod", "mut"], ["pub"],
             "Things inside a `mod` are private. `pub` lets code outside call them.",
             "`hello` lives inside a module. What lets code outside that module use it?",
             output=["hello"], wrap=False),
        fill("Pick the fix so the sword can keep its name.", '''
struct Sword<'a> {
    name: __,
    damage: i32,
}

fn main() {
    let s = Sword { name: "Night Blade", damage: 10 };
    println!("{} hits for {}", s.name, s.damage);
}''', ["&'a str", "str", "&str", "String"], ["&'a str"],
             "A bare `str` has no fixed size, so a struct can't hold it. A borrow can: `&'a str`, using the struct's lifetime.",
             "The struct names a lifetime `'a`. Which type is a borrow that uses it?",
             output=["Night Blade hits for 10"], wrap=False),
        err("Which line does the compiler reject?", '''
use std::collections::HashMap;

fn add(m: &HashMap<String, String>) {
    m.insert(String::from("color"), String::from("red"));
}

fn main() {
    let map = HashMap::new();
    add(&map);
    println!("{:?}", map);
}''', 4, "E0596",
            "`m` is a plain `&` borrow, so it can't change the map. It needs `&mut HashMap<...>`, and `main` needs `let mut map` and `add(&mut map)`.",
            "Which line tries to change something it only borrowed to look at?"),
    ],
})

# ─────────────────────────────── 17 ───────────────────────────────
COURSE.append({
    'part': 1,
    'id': 'closures',
    'title': 'Closures',
    'summary': 'Captures, move, and passing closures to functions.',
    "cards": [
        card('Capture by borrowing',
             'Lesson 12 used closures as small functions. A closure can also borrow nearby values. No parameters? Write `||`. A borrow lasts as long as the closure needs it.',
             '''let word = String::from("hi");
let say = || println!("{word}");
say();
println!("{word}");'''),
        card('Fn, FnMut and FnOnce',
             'These traits describe calls. `Fn` can run through a shared borrow. `FnMut` may change captures. `FnOnce` may consume them. Every closure is FnOnce; Fn closures also satisfy FnMut. Ask for the trait that lets the most closures in: FnOnce if you call it once, FnMut if you call it more, Fn only if you must.',
             '''fn twice<F: FnMut()>(mut action: F) {
    action();
    action();
}
let mut count = 0;
twice(|| count += 1);
println!("{count}");''',
             'twice needs repeated calls, so FnOnce is not enough. FnMut also accepts closures that only read. A closure variable that changes captures needs `let mut`.'),
        card('Move captures into a returned closure',
             '`move` captures by value. A String moves; numbers copy. This closure must own word because the local variable ends when make_say returns. `impl Fn()` promises a callable value while hiding its concrete type.',
             '''fn make_say() -> impl Fn() {
    let word = String::from("hi");
    move || println!("{word}")
}
let say = make_say();
say();
say();''',
             "move does not mean 'call only once'. This closure only reads its owned word, so it implements Fn."),
        card('Consume a capture once',
             'Returning a captured String gives it away. That closure only implements FnOnce. A function that needs one call can accept it and return its result.',
             '''fn run<F: FnOnce() -> String>(f: F)
    -> String
{
    f()
}
let word = String::from("bye");
let take = move || word;
println!("{}", run(take));'''),
    ],
    "problems": [
        out('What does passing this closure print?',
             '''fn apply<F: FnMut(i32) -> i32>(mut f: F)
    -> i32
{
    f(2) + f(3)
}
fn main() {
    let offset = 4;
    println!("{}", apply(|n| n + offset));
}''',
             ['5', '9', '13', WONT], ['13'],
             'apply calls the supplied closure with 2 and 3. Adding the captured offset gives 6 + 7.',
             'Use the same captured offset in both calls.', wrap=False),
        out('What does this print?',
             '''let extra = 4;
let add = |n| n + extra;
println!("{}", add(3));
println!("{extra}");''',
             ['3', '4', '7', "won't compile"],
             ['7', '4'],
             'The closure borrows extra. It adds 4 without changing or taking it.',
             'A shared capture leaves the original available.'),
        out('What does this print?',
             '''let mut n = 1;
let mut step = || n *= 2;
step();
step();
println!("{n}");''',
             ['1', '2', '4', "won't compile"],
             ['4'],
             'Each FnMut call doubles the same captured n. Its mutable borrow ends after the last call.',
             'Track the same variable through both calls.'),
        err('Which line does the compiler reject?',
             '''fn main() {
    let mut n = 0;
    let tick = || n += 1;
    tick();
}''',
             4,
             'E0596',
             'rustc rejects the call because it needs mutable access to tick. Fix the declaration to `let mut tick`.',
             'Find the call that needs a mutable closure variable.'),
        err('Which line uses a moved value?',
             '''fn main() {
    let s = String::from("hi");
    let say = move || println!("{s}");
    println!("{s}");
    say();
}''',
             4,
             'E0382',
             'move gave the closure ownership of s.',
             'Find a use of s outside its new owner.'),
        fill('Return a closure that owns its local String.',
             '''fn greeting() -> impl Fn() -> usize {
    let text = String::from("hello");
    __ || text.len()
}
fn main() {
    println!("{}", greeting()());
}''',
             ['move', 'return', 'mut'],
             ['move'],
             'Without move, reading text.len() borrows text. That borrow cannot survive the function. move gives the closure the String.',
             'The local String must survive inside the returned closure.', output=['5'], wrap=False),
        out('This calls the closure twice. What happens?',
             '''let word = String::from("hi");
let take = move || word;
println!("{}", take());
println!("{}", take());''',
             ['hi', "won't compile"],
             ["won't compile"],
             'The first call moves the String out. This FnOnce closure is consumed and cannot be called again.',
             'Returning an owned String gives it away.'),
        order('Make it print 8.',
             ['fn main() {'],
             ['let base = 5;', 'let add = |n| base + n;', 'println!("{}", add(3));'],
             ['}'],
             ['8'],
             'Make the captured value, make the closure, then call it.',
             'Each name must exist before use.'),
    ],
})

# ─────────────────────────────── 18 ───────────────────────────────
COURSE.append({
    'part': 1,
    'id': 'smart-pointers',
    'title': 'Box, Rc and when you need them',
    'summary': 'One owner on the heap, or several owners on one thread.',
    "cards": [
        card('Box owns a value on the heap',
             '`Box<T>` keeps its value on the heap. The box is its single owner. Use `*` to read the value. Ordinary local values are fine unless you need this extra indirection.',
             '''let n = Box::new(7);
println!("{}", *n);'''),
        card('Give recursive types a known size',
             'An enum cannot contain itself directly: how big would it be? A box has a known size, so it can point to the next node.',
             '''enum List {
    End,
    Next(i32, Box<List>),
}
let end = Box::new(List::End);
let list = List::Next(1, end);
match list {
    List::Next(n, _) => println!("{n}"),
    List::End => println!("empty"),
}'''),
        card('Rc shares ownership on one thread',
             '`Rc` counts owners. `Rc::clone` makes another owner of the same value; it does not copy the value. The value is dropped when the last owner goes away.',
             '''use std::rc::Rc;
let name = Rc::new(String::from("tree"));
let other = Rc::clone(&name);
println!("{other}");
println!("{}", Rc::strong_count(&name));''',
             'Use a borrow for temporary access. Use Rc when several places must own one value. Rc does not give mutable access, and cannot be sent between threads.'),
    ],
    "problems": [
        fill('Put 9 in a box.',
             '''let n = __::new(9);
println!("{}", *n);''',
             ['Box', 'Vec', 'String'],
             ['Box'],
             '`Box::new` allocates one owned value.',
             'A vector holds a list; here we want one number.', output=['9']),
        out('What does this print?',
             '''let mut n = Box::new(2);
*n += 3;
println!("{}", *n);''',
             ['2', '3', '5', "won't compile"],
             ['5'],
             'The mutable box lets us change its number through `*n`.',
             'Dereferencing reaches the number inside the box.'),
        err('Which line uses a moved box?',
             '''fn main() {
    let first = Box::new(4);
    let second = first;
    println!("{}", *first);
    println!("{}", *second);
}''',
             4,
             'E0382',
             'A box has one owner. Assignment moves it into `second`.',
             'Box is not Copy, even when its number is.'),
        fill('Give this recursive enum a known size.',
             '''enum List {
    End,
    Next(__<List>),
}
fn main() {
    let end = Box::new(List::End);
    let _list = List::Next(end);
}''',
             ['Box', 'Option', 'Result'],
             ['Box'],
             'A Box points to the next node instead of storing it directly.',
             'Option would still contain the recursive value directly.', wrap=False),
        out('How many owners remain?',
             '''use std::rc::Rc;
let a = Rc::new(10);
let b = Rc::clone(&a);
{
    let c = Rc::clone(&b);
}
println!("{}", Rc::strong_count(&a));''',
             ['1', '2', '3', "won't compile"],
             ['2'],
             '`c` is dropped at the closing brace. Only `a` and `b` remain.',
             'Count owners that are still in scope.'),
        fill('Share ownership of the same String.',
             '''use std::rc::Rc;
let a = Rc::new(String::from("oak"));
let b = Rc::__(&a);
println!("{b}");
println!("{}", Rc::strong_count(&a));''',
             ['clone', 'new', 'strong_count'],
             ['clone'],
             'Rc::clone adds an owner of the same allocation.',
             'We want another Rc, not a count or a new allocation.', output=['oak', '2']),
        err('Which line tries to change a shared value?',
             '''use std::rc::Rc;
fn main() {
    let mut a = Rc::new(2);
    *a = 5;
}''',
             4,
             'E0594',
             'A mutable Rc variable does not make its shared value mutable.',
             'Rc gives shared access to the value inside.'),
        order('Make two owners, then print their count.',
             ['use std::rc::Rc;', 'fn main() {'],
             ['let a = Rc::new(7);', 'let b = Rc::clone(&a);', 'println!("{}", Rc::strong_count(&b));'],
             ['}'],
             ['2'],
             'Create the first owner before cloning it.',
             'The count must happen while both owners exist.'),
    ],
})

# ─────────────────────────────── 19 ───────────────────────────────
COURSE.append({
    'part': 1,
    'id': 'threads',
    'title': 'Threads, Arc and Mutex',
    'summary': 'Run work on another thread and share state safely.',
    "cards": [
        card('Spawn work, then join it',
             '`thread::spawn` runs a closure on another thread. `move` gives it owned data. `join` waits and returns a Result: the thread may have panicked.',
             '''use std::thread;
let word = String::from("hi");
let job = thread::spawn(move || word.len());
println!("{}", job.join().unwrap());''',
             'These tiny examples unwrap to stay short. Real code should decide how to handle a panic.'),
        card('Arc shares owners between threads',
             'Rc works on one thread. Arc counts owners safely between threads. It shares ownership, but does not let you change the value by itself.',
             '''use std::sync::Arc;
use std::thread;
let n = Arc::new(6);
let other = Arc::clone(&n);
let job = thread::spawn(move || *other + 1);
println!("{}", job.join().unwrap());
println!("{}", *n);'''),
        card('Mutex allows one user at a time',
             '`lock` waits for exclusive access. It returns a guard. Read or change through `*guard`; dropping it releases the lock. A scope keeps the lock short.',
             '''use std::sync::{Arc, Mutex};
use std::thread;
let count = Arc::new(Mutex::new(0));
let other = Arc::clone(&count);
let job = thread::spawn(move || {
    let mut guard = other.lock().unwrap();
    *guard += 1;
});
job.join().unwrap();
println!("{}", *count.lock().unwrap());''',
             'lock returns a Result because a previous holder may have panicked. Never join a thread while holding a lock it needs.'),
    ],
    "problems": [
        out('What does this print after the worker finishes?',
             '''use std::thread;
let task = thread::spawn(|| {
    String::from("done")
});
match task.join() {
    Ok(text) => println!("{text}"),
    Err(_) => println!("panic"),
}''',
             ['done', 'panic', "won't compile"],
             ['done'],
             'join waits for the worker. It returns Ok with the String produced by the closure.',
             'The worker returns normally, so follow the Ok branch.'),
        out('What does this print?',
             '''use std::thread;
let n = 5;
let job = thread::spawn(move || n * 2);
println!("{}", job.join().unwrap());
println!("{n}");''',
             ['5', '10', "won't compile"],
             ['10', '5'],
             'The closure gets a copy of the number. Joining gives 10; `n` is still 5.',
             'Numbers are Copy, even with move.'),
        err('Which line uses a moved String?',
             '''use std::thread;
fn main() {
    let s = String::from("hi");
    let job = thread::spawn(move || s.len());
    println!("{s}");
    job.join().unwrap();
}''',
             5,
             'E0382',
             'The thread owns the String after the move.',
             "Find the old owner's use after spawning."),
        fill('Share ownership across threads.',
             '''use std::sync::Arc;
use std::thread;
let n = Arc::new(8);
let other = Arc::__(&n);
let job = thread::spawn(move || *other);
println!("{}", job.join().unwrap());''',
             ['clone', 'new', 'strong_count'],
             ['clone'],
             'Arc::clone makes a second owner for the new thread.',
             'The thread needs an Arc to the same number.', output=['8']),
        out('What does this print after joining?',
             '''use std::sync::{Arc, Mutex};
use std::thread;
let n = Arc::new(Mutex::new(2));
let other = Arc::clone(&n);
let job = thread::spawn(move || {
    *other.lock().unwrap() += 3;
});
job.join().unwrap();
println!("{}", *n.lock().unwrap());''',
             ['2', '3', '5', "won't compile"],
             ['5'],
             'The thread adds 3 under the lock. join ensures it finishes before we read.',
             'The two Arcs share one Mutex and one number.'),
        fill('Get exclusive access to the number.',
             '''use std::sync::Mutex;
let n = Mutex::new(4);
{
    let mut guard = n.__().unwrap();
    *guard += 1;
}
println!("{}", *n.lock().unwrap());''',
             ['lock', 'clone', 'join'],
             ['lock'],
             'lock gives a guard. The brace drops it before the next lock.',
             'Only one guard can hold this lock at a time.', output=['5']),
        out('This sends an Rc to a thread. What happens?',
             '''use std::rc::Rc;
use std::thread;
let n = Rc::new(4);
let job = thread::spawn(move || *n);
println!("{}", job.join().unwrap());''',
             ['4', "won't compile"],
             ["won't compile"],
             'Rc cannot cross threads. Use Arc for thread-safe shared ownership.',
             "Rc's owner count is only safe on one thread."),
        order("Print the worker's result.",
             ['use std::thread;', 'fn main() {'],
             ['let job = thread::spawn(|| 6);', 'let n = job.join().unwrap();', 'println!("{n}");'],
             ['}'],
             ['6'],
             'Spawn, wait, then use the returned value.',
             'A thread handle is not its result.'),
    ],
})

# ─────────────────────────────── 20 ───────────────────────────────
COURSE.append({
    'part': 1,
    'id': 'custom-errors',
    'title': 'Your own error types',
    'summary': 'Name failures, print them, and convert them with From and ?.',
    "cards": [
        card('Give failures names',
             'An error enum lets callers match the reason for failure. Return it as the E in Result<T, E>.',
             '''#[derive(Debug)]
enum AgeError { Empty, Invalid }
fn age(text: &str) -> Result<i32, AgeError> {
    if text.is_empty() {
        return Err(AgeError::Empty);
    }
    Ok(18)
}'''),
        card('Display is the message for people',
             "Debug shows a type for developers. Display controls `{}`. Write the message into the supplied formatter with `write!`; return its fmt::Result. `'_` asks Rust to infer this lifetime, rather than naming it `'a`.",
             '''use std::fmt;
#[derive(Debug)]
struct BadAge;
impl fmt::Display for BadAge {
    fn fmt(
        &self,
        f: &mut fmt::Formatter<'_>,
    ) -> fmt::Result {
        write!(f, "invalid age")
    }
}
impl std::error::Error for BadAge {}
fn main() {
    println!("{}", BadAge);
}''',
             'The standard Error trait requires Debug and Display. For this simple type its impl can be empty.'),
        card('From connects error types',
             'Implement From<OldError> for your error type. Then `?` converts an error and returns early. On success, `?` gives the value inside Ok.',
             '''use std::num::ParseIntError;
#[derive(Debug)]
enum AgeError { Invalid(ParseIntError) }
impl From<ParseIntError> for AgeError {
    fn from(e: ParseIntError) -> Self {
        Self::Invalid(e)
    }
}
fn age(s: &str) -> Result<i32, AgeError> {
    let n = s.parse::<i32>()?;
    Ok(n)
}
fn main() {
    println!("{}", age("18").unwrap());
}''',
             'Without a matching From conversion, `?` cannot change the error type for you.'),
    ],
    "problems": [
        fill('Return the named failure.',
             '''enum InputError { Empty }
fn read(s: &str)
    -> Result<usize, InputError>
{
    if s.is_empty() {
        return __(InputError::Empty);
    }
    Ok(s.len())
}
fn main() {
    println!("{}", read("").is_err());
}''',
             ['Err', 'Ok', 'Some'],
             ['Err'],
             'Err carries the failure value.',
             'The return type is Result, not Option.', output=['true'], wrap=False),
        out('Which branch runs?',
             '''enum InputError { Empty, Negative }
let result: Result<i32, InputError> =
    Err(InputError::Negative);
match result {
    Ok(n) => println!("{n}"),
    Err(InputError::Empty) => {
        println!("empty");
    }
    Err(InputError::Negative) => {
        println!("negative");
    }
}''',
             ['0', 'empty', 'negative', "won't compile"],
             ['negative'],
             'The enum names the exact failure, so callers can match it.',
             'Follow the Err variant and the inner variant.'),
        fill('Send the error message to its formatter.',
             '''use std::fmt;
struct Missing;
impl fmt::Display for Missing {
    fn fmt(
        &self,
        out: &mut fmt::Formatter<'_>,
    ) -> fmt::Result {
        write!(__, "missing name")
    }
}
fn main() { println!("{}", Missing); }''',
             ['out', 'self', 'std::io::stdout()'],
             ['out'],
             'Display must write into the formatter it receives. Here that parameter is named out.',
             'Which value is the formatter passed to fmt?', output=['missing name'], wrap=False),
        out('What does Display print?',
             '''use std::fmt;
#[derive(Debug)]
struct Bad;
impl fmt::Display for Bad {
    fn fmt(
        &self,
        f: &mut fmt::Formatter<'_>,
    ) -> fmt::Result {
        write!(f, "try again")
    }
}
fn main() { println!("{}", Bad); }''',
             ['Bad', 'try again', "won't compile"],
             ['try again'],
             '{} uses Display. {:?} would use Debug.',
             'Read the message in write!.', wrap=False),
        fill('Choose the destination error type.',
             '''use std::num::ParseIntError;
#[derive(Debug)]
struct Bad;
impl From<ParseIntError> for __ {
    fn from(_: ParseIntError) -> Self { Bad }
}
fn read(s: &str) -> Result<i32, Bad> {
    Ok(s.parse::<i32>()?)
}
fn main() {
    println!("{}", read("7").unwrap());
}''',
             ['Bad', 'ParseIntError', 'i32'],
             ['Bad'],
             'The function returns Result<i32, Bad>, so the conversion must build Bad from the parse error.',
             'Look at the error type returned by read, and the value built by from.', output=['7'], wrap=False),
        out('What does this print?',
             '''use std::num::ParseIntError;
#[derive(Debug)]
struct Bad;
impl From<ParseIntError> for Bad {
    fn from(_: ParseIntError) -> Self { Bad }
}
fn read(s: &str) -> Result<i32, Bad> {
    let n = s.parse::<i32>()?;
    Ok(n + 1)
}
fn main() {
    println!("{}", read("oops").is_err());
}''',
             ['true', 'false', "won't compile"],
             ['true'],
             'Parsing fails. ? converts the error to Bad and returns before adding 1.',
             'An error takes the early return path.', wrap=False),
        err('Which line needs an error conversion?',
             '''#[derive(Debug)]
struct Bad;
fn read(s: &str) -> Result<i32, Bad> {
    let n = s.parse::<i32>()?;
    Ok(n)
}
fn main() {}''',
             4,
             'E0277',
             'Bad has no From<ParseIntError> implementation, so ? cannot convert the error.',
             "The parse error and the function's error have different types."),
        order('Return success after checking for empty input.',
             ['fn read(s: &str) -> Result<i32, String> {', 'if s.is_empty() {'],
             ['    return Err(String::from("empty"));', '}', 'let n = 8;', 'Ok(n)'],
             ['}', 'fn main() {', '    println!("{}", read("yes").unwrap());', '}'],
             ['8'],
             'Check for failure first. The tail expression returns the success value.',
             'Ok(n) must be last and n must exist first.'),
    ],
})

# ─────────────────────────────── 21 ───────────────────────────────
COURSE.append({
    'part': 1,
    'id': 'iterator-chains',
    'title': 'Iterator chains and impl Trait',
    'summary': 'Filter, transform and collect. Return an iterator without naming its type.',
    "cards": [
        card('A chain describes the work',
             'Lesson 12 chained map and sum. Now keep only some items with filter. into_iter consumes a collection and yields owned items. filter borrows each item to ask whether to keep it.',
             '''let nums = vec![1, 2, 3, 4];
let total: i32 = nums.into_iter()
    .filter(|n| *n > 2)
    .map(|n| n * 10)
    .sum();
println!("{total}");''',
             'filter borrows each item to ask the question, so its parameter is &i32 here. map receives the owned i32.'),
        card('Iterators are lazy',
             'Building a chain does no work yet. `collect` runs it and builds a collection. With iter(), items are borrowed; copied() turns borrowed Copy values into owned ones.',
             '''let nums = vec![2, 4, 6];
let picked: Vec<i32> = nums.iter()
    .copied().take(2).collect();
println!("{:?}", picked);
println!("{}", nums.len());''',
             'take(2) limits this chain to two items. The original vector is still available.'),
        card('Return impl Iterator',
             '`impl Iterator<Item = i32>` hides the concrete iterator type. Callers can still use iterator methods. The function must return one concrete type on all paths.',
             '''fn doubles() -> impl Iterator<Item = i32> {
    (1..4).map(|n| n * 2)
}
fn main() {
    let total: i32 = doubles().sum();
    println!("{total}");
}''',
             'This is not a box or a choice of types. Rust still knows the one exact type underneath.'),
    ],
    "problems": [
        fill('Keep only numbers above 2.',
             '''let total: i32 = vec![1, 3, 4].into_iter()
    .__(|n| *n > 2).sum();
println!("{total}");''',
             ['filter', 'map', 'take'],
             ['filter'],
             'filter keeps 3 and 4, which sum to 7.',
             'We want to keep items, not turn them into booleans.', output=['7']),
        out('What does the chain print?',
             '''let n: i32 = (1..5)
    .filter(|n| *n % 2 == 0)
    .map(|n| n * 3).sum();
println!("{n}");''',
             ['6', '12', '18', "won't compile"],
             ['18'],
             'The even numbers are 2 and 4. Their triples add to 18.',
             'Filter first, then transform the surviving items.'),
        fill('Build a vector from the iterator.',
             '''let nums: Vec<i32> = (1..4)
    .map(|n| n + 1).__();
println!("{:?}", nums);''',
             ['collect', 'sum', 'max'],
             ['collect'],
             'collect builds the Vec named by the type annotation.',
             'Which consumer builds a collection?', output=['[2, 3, 4]']),
        out('What does this print?',
             '''let steps = (0..3).map(|n| {
    println!("work");
    n + 1
});
println!("ready");''',
             ['work', 'ready', "won't compile"],
             ['ready'],
             'Nothing consumes steps, so the map closure never runs.',
             'An unused iterator is lazy.'),
        fill("Hide the iterator's concrete type.",
             '''fn nums() -> __ Iterator<Item = i32> {
    1..4
}
fn main() {
    println!("{}", nums().sum::<i32>());
}''',
             ['impl', 'dyn', 'enum'],
             ['impl'],
             'impl Iterator promises iterator methods while hiding its type.',
             'No box is needed for this one concrete return type.', output=['6'], wrap=False),
        out('What does take keep?',
             '''let nums = vec![3, 5, 7];
let total: i32 = nums.iter()
    .copied().take(2).sum();
println!("{total}");
println!("{}", nums.len());''',
             ['2', '3', '8', '15'],
             ['8', '3'],
             'take keeps 3 and 5. Iterating by borrow leaves all three originals.',
             'The chain limits its items; it does not shorten nums.'),
        out('What happens when these iterator types differ?',
             '''fn nums(short: bool)
    -> impl Iterator<Item = i32>
{
    if short {
        0..2
    } else {
        (0..2).map(|n| n + 1)
    }
}
fn main() {
    for n in nums(false) {
        println!("{n}");
    }
}''',
             ['0', '1', '2', "won't compile"],
             ["won't compile"],
             'A range and a mapped range have different concrete types. impl Trait needs one type.',
             'Both yield i32, but their iterator types differ.', wrap=False),
        order('Transform, collect, then print.',
             ['fn main() {'],
             ['let steps = (1..3).map(|n| n * 2);', 'let nums: Vec<i32> = steps.collect();', 'println!("{:?}", nums);'],
             ['}'],
             ['[2, 4]'],
             'The lazy chain is consumed by collect.',
             'Create each value before its first use.'),
    ],
})

# ─────────────────────────────── 22 ───────────────────────────────
COURSE.append({
    'part': 1,
    'id': 'tests-layout',
    'title': 'Tests and crate layout',
    'summary': 'Check behavior, put logic in a library, and keep main small.',
    "cards": [
        card('A test is a function with a check',
             '`#[test]` marks a test function. `cargo test` runs it. `assert_eq!` checks two values and panics if they differ. A test passes when it returns without panicking.',
             '''fn double(n: i32) -> i32 { n * 2 }
#[test]
fn doubles_three() {
    assert_eq!(double(3), 6);
}
fn main() {
    assert_eq!(double(0), 0);
}''',
             'A normal program does not run #[test] functions. Use cargo test to run them.'),
        card('Put unit tests beside the code',
             "`#[cfg(test)]` includes a module only during tests. `use super::*` brings the parent module's names into scope, including private helpers.",
             '''fn add(a: i32, b: i32) -> i32 { a + b }
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn adds_zero() {
        assert_eq!(add(4, 0), 4);
    }
}
fn main() {}'''),
        card('Library logic, thin main',
             'Cargo puts reusable logic in src/lib.rs. src/main.rs is a separate binary crate: read input, call the library, print a result. For package pocket-demo, import the library as pocket_demo.',
             '''// src/lib.rs in a Cargo project:
// pub fn double(n: i32) -> i32 { n * 2 }
// src/main.rs in that project:
// fn main() {
//     let n = pocket_demo::double(3);
//     println!("{n}");
// }
// Single-file version for practice:
mod logic {
    pub fn double(n: i32) -> i32 { n * 2 }
}
fn main() {
    println!("{}", logic::double(3));
}''',
             "Run cargo test from the project folder. Integration tests in tests/*.rs use the library's public API as a caller would."),
        card('Modules can live in files',
             'In lib.rs, `pub mod math;` loads math.rs (or math/mod.rs). Put `pub fn double` in that file. The library exposes it as pocket_demo::math::double. These exercises keep the same module inline.',
             '''// src/lib.rs: pub mod math;
// src/math.rs:
// pub fn double(n: i32) -> i32 { n * 2 }
// Equivalent inline module:
pub mod math {
    pub fn double(n: i32) -> i32 { n * 2 }
}
fn main() { assert_eq!(math::double(3), 6); }''',
             'A file does not become a module just by existing. A mod declaration connects it to the crate.'),
    ],
    "problems": [
        fill("Check the function's answer.",
             '''fn inc(n: i32) -> i32 { n + 1 }
fn main() {
    __!(inc(2), 3);
    println!("passed");
}''',
             ['assert_eq', 'assert', 'println'],
             ['assert_eq'],
             'assert_eq! checks that both values are equal.',
             'We need a check of two values, not a print.', output=['passed'], wrap=False),
        out('What prints after a passing check?',
             '''assert_eq!(2 + 3, 5);
println!("passed");''',
             ['5', 'passed', "won't compile"],
             ['passed'],
             'A passing assertion prints nothing and lets execution continue.',
             'The println runs after the assertion succeeds.'),
        fill('Expose the function to main.',
             '''mod math {
    __ fn double(n: i32) -> i32 { n * 2 }
}
fn main() {
    assert_eq!(math::double(4), 8);
    println!("passed");
}''',
             ['pub', 'mut', 'let'],
             ['pub'],
             'pub lets main call the function through the module path.',
             'Items are private unless you expose them.', output=['passed'], wrap=False),
        err('Which line calls a private function?',
             '''mod math {
    fn double(n: i32) -> i32 { n * 2 }
}
fn main() {
    assert_eq!(math::double(2), 4);
}''',
             5,
             'E0603',
             'The function needs pub for main to call it from outside math.',
             'Find the call that crosses the module boundary.'),
        out('What does a normal run print?',
             '''#[test]
fn checks_sum() { assert_eq!(2 + 2, 4); }
fn main() { println!("main"); }''',
             ['main', 'test', '4', "won't compile"],
             ['main'],
             'A normal run executes main. cargo test uses a separate test harness.',
             '#[test] does not add a call inside main.', wrap=False),
        fill("Reach the inline module's function.",
             '''mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }
}
fn main() {
    assert_eq!(__::add(2, 3), 5);
    println!("passed");
}''',
             ['math', 'main', 'super'],
             ['math'],
             "The module's name starts the path to its public function.",
             'Use the name after mod.', output=['passed'], wrap=False),
        fill('Check the expected length in this test.',
             '''#[test]
fn four_letters() {
    assert_eq!("rust".len(), __);
}
fn main() { println!("ready"); }''',
             ['4', '0', '5'],
             ['4'],
             'The test checks four letters. A normal run prints ready; cargo test runs the assertion.',
             'Choose the expected value that makes the assertion pass.', output=['ready'], wrap=False),
        out('What do these boundary checks print?',
             '''fn length(s: &str) -> usize { s.len() }
fn main() {
    assert_eq!(length(""), 0);
    assert_eq!(length("rust"), 4);
    println!("passed");
}''',
             ['0', '4', 'passed', "won't compile"],
             ['passed'],
             'Both checks pass, including the empty input. Assertions do not print their values.',
             'Only println produces output.', wrap=False),
        order('Keep main thin: call logic, check, print.',
             ['mod logic {', 'pub fn double(n: i32) -> i32 { n * 2 }', '}', 'fn main() {'],
             ['let n = logic::double(5);', 'assert_eq!(n, 10);', 'println!("{n}");'],
             ['}'],
             ['10'],
             'main uses the public logic function and checks its answer.',
             'n must be made before its check and print.'),
    ],
})

# Part 2 / CLI: pinned excerpts; std-only applications.
COURSE.append({'part': 2,
 'id': 'cli-structure',
 'title': 'A command-line tool: structure',
 'summary': 'Study ripgrep and clap: crate boundaries, named arguments, and exit status.',
 'cards': [{'type': 'real',
            'h': 'Small crates, one application',
            'p': 'A Cargo workspace builds related packages together; each member has its own '
                 'Cargo.toml. Ripgrep separates matching, searching and printing. Put reusable '
                 'behavior in libraries and let the binary coordinate them. This is a manifest, '
                 'not Rust code.',
            'code': '[workspace]\n'
                    'members = [\n'
                    '  "crates/globset",\n'
                    '  "crates/grep",\n'
                    '  "crates/cli",\n'
                    '  "crates/matcher",\n'
                    '  "crates/pcre2",\n'
                    '  "crates/printer",\n'
                    '  "crates/regex",\n'
                    '  "crates/searcher",\n'
                    '  "crates/ignore",\n'
                    ']',
            'repo': 'BurntSushi/ripgrep',
            'tag': '14.1.1',
            'path': 'Cargo.toml',
            'lines': (38, 49),
            'license': 'MIT',
            'note': 'Ripgrep is not a tiny main demo: its application layer is substantial. Copy '
                    'the dependency direction, not its size.',
            'own': False},
           {'type': 'real',
            'h': 'Arguments become a struct',
            'p': 'clap is an external crate. Its Parser derive generates parsing; `#[command]` '
                 'sets app metadata and `#[arg(short, long)]` accepts short/long flag forms. '
                 'Cli::parse reads the process arguments once, handling help and invalid input. A '
                 'bool field records whether a switch was set. A tuple groups values by position, '
                 'accessed with `.0`, `.1`, and so on; a struct names their roles. Handle help '
                 'before expensive work.',
            'code': 'use clap::Parser;\n'
                    '\n'
                    '#[derive(Parser)]\n'
                    '#[command(version, about, long_about = None)]\n'
                    'struct Cli {\n'
                    '    #[arg(short, long)]\n'
                    '    verbose: bool,\n'
                    '}\n'
                    '\n'
                    'fn main() {\n'
                    '    let cli = Cli::parse();\n'
                    '\n'
                    '    println!("verbose: {:?}", cli.verbose);\n'
                    '}',
            'repo': 'clap-rs/clap',
            'tag': 'v4.5.20',
            'path': 'examples/tutorial_derive/03_01_flag_bool.rs',
            'lines': (1, 14),
            'license': 'MIT',
            'note': 'The exercises use only std. Turn raw text into named fields before the core '
                    'sees it.',
            'own': False},
           {'type': 'real',
            'h': 'The shell needs an outcome',
            'p': "This is the tail of ripgrep's run function. It returns 0 for a match, 2 for an "
                 'error, 1 for no match. A no-match result is normal search behavior. Exit '
                 "meanings belong to the tool's contract.",
            'code': '    Ok(if matched && (args.quiet() || !messages::errored()) {\n'
                    '        ExitCode::from(0)\n'
                    '    } else if messages::errored() {\n'
                    '        ExitCode::from(2)\n'
                    '    } else {\n'
                    '        ExitCode::from(1)\n'
                    '    })\n'
                    '}',
            'repo': 'BurntSushi/ripgrep',
            'tag': '14.1.1',
            'path': 'crates/core/main.rs',
            'lines': (94, 101),
            'license': 'MIT',
            'note': '`std::process::ExitCode` can be returned from main; SUCCESS is zero, FAILURE '
                    'is a portable failure, and ExitCode::from(u8) selects a code. Returning a '
                    'nonzero code is different from printing a number.',
            'own': False},
           {'h': 'Acquire input at the boundary',
            'p': '`std::env::args()` yields owned String arguments, including the executable name '
                 'first; `.skip(1)` omits it. `.next()` returns the next item as Option. '
                 '`into_iter()` consumes a collection to make an iterator. Simulate arguments in '
                 'exercises so tests do not depend on the actual command line. eprintln! writes '
                 'diagnostics to stderr; println! writes results to stdout.',
            'code': 'fn main() {\n'
                    '    let count = std::env::args().skip(1).count();\n'
                    '    eprintln!("received {count} arguments");\n'
                    '}',
            'note': '`count()` consumes an iterator and returns its item count. Pure functions '
                    'take data and return data: keep argument access, file access and printing in '
                    'main, around a reusable library call.'}],
 'problems': [{'type': 'fill',
               'prompt': 'The parser accepts a count; keep the core numeric. Fill the config field '
                         'type.',
               'code': 'struct Config { copies: __ }\n'
                       'fn parse(s: &str) -> Config {\n'
                       '    Config { copies: s.parse().unwrap() }\n'
                       '}\n'
                       'fn main() {\n'
                       '    let cfg = parse("3");\n'
                       '    println!("{}", cfg.copies * 4);\n'
                       '}',
               'bank': ['i32', 'String', 'bool'],
               'answer': ['i32'],
               'good': 'The count is converted once into an integer field.',
               'bad': 'Which type lets the core multiply without parsing again?',
               'output': ['12'],
               'wrap': False},
              {'type': 'better',
               'prompt': 'Both store a label and a quiet switch. Which representation makes '
                         'callers less likely to confuse the settings?',
               'a': 'fn settings() -> (String, bool) {\n'
                    '    (String::from("scan"), true)\n'
                    '}\n'
                    'fn main() {\n'
                    '    let c = settings();\n'
                    '    println!("{} {}", c.0, c.1);\n'
                    '}',
               'b': 'struct Args { label: String, quiet: bool }\n'
                    'fn settings() -> Args {\n'
                    '    Args {\n'
                    '        label: String::from("scan"),\n'
                    '        quiet: true,\n'
                    '    }\n'
                    '}\n'
                    'fn main() {\n'
                    '    let c = settings();\n'
                    '    println!("{} {}", c.label, c.quiet);\n'
                    '}',
               'answer': 'b',
               'lint': None,
               'good': 'Named fields carry meaning at each use. A tuple does work, but readers '
                       'must remember each position.',
               'bad': 'Judge clarity for callers, not whether either sample works.',
               'wrap': False},
              {'type': 'output',
               'prompt': 'These strings simulate env::args. Which argument reaches the parser?',
               'code': 'let raw = vec!["finder", "--quiet", "x"];\n'
                       'let mut args = raw.into_iter().skip(1);\n'
                       'println!("{}", args.next().unwrap());',
               'bank': ['finder', '--quiet', 'src'],
               'answer': ['--quiet'],
               'good': 'skip(1) removes the executable name, not the first user option.',
               'bad': 'next takes one item from the remaining iterator.',
               'wrap': True},
              {'type': 'fill',
               'prompt': 'Return success after checking the result. This run must print done and '
                         'exit successfully.',
               'code': 'use std::process::ExitCode;\n'
                       'fn main() -> ExitCode {\n'
                       '    let written = 2;\n'
                       '    if written > 0 {\n'
                       '        println!("done");\n'
                       '        ExitCode::__\n'
                       '    } else {\n'
                       '        ExitCode::FAILURE\n'
                       '    }\n'
                       '}',
               'bank': ['SUCCESS', 'FAILURE'],
               'answer': ['SUCCESS'],
               'good': 'SUCCESS tells the shell that work completed.',
               'bad': 'The checker runs the program too: a failure exit does not count as success.',
               'output': ['done'],
               'wrap': False},
              {'type': 'error',
               'prompt': 'The core accepts parsed data. Which line mistakenly sends raw text '
                         'instead?',
               'code': 'struct Config { limit: i32 }\n'
                       'fn run(c: Config) -> i32 { c.limit * 2 }\n'
                       'fn main() {\n'
                       '    let raw = "5";\n'
                       '    println!("{}", run(raw));\n'
                       '}',
               'line': 5,
               'error_code': 'E0308',
               'good': 'run requires Config, so the boundary must construct one first.',
               'bad': 'Look at the argument type required by run.',
               'wrap': False},
              {'type': 'order',
               'prompt': 'Wire a reusable library call to the output at the edge.',
               'head': ['mod logic {',
                        '    pub fn area(n: i32) -> i32 { n * n }',
                        '}',
                        'fn main() {'],
               'pool': ['let side = 7;', 'let result = logic::area(side);', 'println!("{result}");'],
               'tail': ['}'],
               'output': ['49'],
               'good': 'Input, library calculation, then presentation.',
               'bad': "Each stage consumes the previous stage's value."},
              {'type': 'better',
               'prompt': 'A real scan is expensive. Both stand-ins print usage for help. Which '
                         'keeps scanning behind the normal-work branch?',
               'a': 'fn scan() -> i32 { (1..10).sum() }\n'
                    'fn main() {\n'
                    '    let help = true;\n'
                    '    if help {\n'
                    '        println!("usage");\n'
                    '    } else {\n'
                    '        println!("{}", scan());\n'
                    '    }\n'
                    '}',
               'b': 'fn scan() -> i32 { (1..10).sum() }\n'
                    'fn main() {\n'
                    '    let help = true;\n'
                    '    let count = scan();\n'
                    '    if help {\n'
                    '        println!("usage");\n'
                    '    } else {\n'
                    '        println!("{count}");\n'
                    '    }\n'
                    '}',
               'answer': 'a',
               'lint': None,
               'good': 'Dispatching help first avoids running the scan for a request that only '
                       'needs instructions. Both versions produce the requested output.',
               'bad': 'Trace whether scan runs before the help branch.',
               'wrap': False},
              {'type': 'output',
               'prompt': 'This tool uses ripgrep-style status meanings. It found no matches and '
                         'had no error. What status number does this helper choose?',
               'code': 'fn status(found: bool, failed: bool) -> u8 {\n'
                       '    if failed { 2 }\n'
                       '    else if found { 0 }\n'
                       '    else { 1 }\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{}", status(false, false));\n'
                       '}',
               'bank': ['0', '1', '2'],
               'answer': ['1'],
               'good': 'No match is a distinct normal outcome; an error would be 2. This prints '
                       'the choice to make it testable; main would return ExitCode::from(choice).',
               'bad': 'Follow the branch for neither found nor failed.',
               'wrap': False}]})

COURSE.append({'part': 2,
 'id': 'cli-rules',
 'title': 'A command-line tool: rules',
 'summary': 'Parse once, keep errors useful, and test a pure core.',
 'cards': [{'type': 'real',
            'h': 'Application errors collect context',
            'p': 'anyhow::Result is an external-crate result used to propagate different error '
                 'types with useful context for a person. This application function dispatches a '
                 'parsed result; it is not a library error contract. The special mode covers '
                 'requests such as help.',
            'code': 'fn run(result: crate::flags::ParseResult<HiArgs>) -> anyhow::Result<ExitCode> '
                    '{\n'
                    '    use crate::flags::{Mode, ParseResult};\n'
                    '\n'
                    '    let args = match result {\n'
                    '        ParseResult::Err(err) => return Err(err),\n'
                    '        ParseResult::Special(mode) => return special(mode),\n'
                    '        ParseResult::Ok(args) => args,\n'
                    '    };',
            'repo': 'BurntSushi/ripgrep',
            'tag': '14.1.1',
            'path': 'crates/core/main.rs',
            'lines': (77, 84),
            'license': 'MIT',
            'note': 'An anyhow-style main reports failures from many layers. A library usually '
                    'returns a concrete error type so callers can decide what to do, instead of '
                    'interpreting message strings. Our std exercises use Result and typed enums.',
            'own': False},
           {'type': 'real',
            'h': 'Library errors keep their identity',
            'p': 'globset stores the original pattern and an ErrorKind. Its callers can inspect '
                 'structured failure information. Deriving Debug helps diagnostics; Eq and '
                 'PartialEq enable comparisons. ErrorKind is an enum defined just below this '
                 'excerpt.',
            'code': '/// Represents an error that can occur when parsing a glob pattern.\n'
                    '#[derive(Clone, Debug, Eq, PartialEq)]\n'
                    'pub struct Error {\n'
                    '    /// The original glob provided by the caller.\n'
                    '    glob: Option<String>,\n'
                    '    /// The kind of error.\n'
                    '    kind: ErrorKind,\n'
                    '}',
            'repo': 'BurntSushi/ripgrep',
            'tag': '14.1.1',
            'path': 'crates/globset/src/lib.rs',
            'lines': (142, 149),
            'license': 'MIT',
            'note': 'Keep variants for failures callers need to distinguish. From converts a '
                    'lower-level error into a library error; ? uses that conversion. '
                    'Human-readable context belongs at the reporting boundary.',
            'own': False},
           {'type': 'real',
            'h': 'Parse and validate once',
            'p': 'The value_parser macro selects a u16 parser, and range(1..) rejects zero. u16 is '
                 'an unsigned 16-bit integer. The core receives a valid port, not a String to '
                 'parse repeatedly. These macros are clap APIs; no external crates appear in our '
                 'problems.',
            'code': 'use clap::Parser;\n'
                    '\n'
                    '#[derive(Parser)]\n'
                    '#[command(version, about, long_about = None)]\n'
                    'struct Cli {\n'
                    '    /// Network port to use\n'
                    '    #[arg(value_parser = clap::value_parser!(u16).range(1..))]\n'
                    '    port: u16,\n'
                    '}\n'
                    '\n'
                    'fn main() {\n'
                    '    let cli = Cli::parse();\n'
                    '\n'
                    '    println!("PORT = {}", cli.port);\n'
                    '}',
            'repo': 'clap-rs/clap',
            'tag': 'v4.5.20',
            'path': 'examples/tutorial_derive/04_02_parse.rs',
            'lines': (1, 15),
            'license': 'MIT',
            'note': 'Reject invalid input before running work. Do not silently substitute a valid '
                    'setting for invalid user input unless the CLI contract explicitly asks for '
                    'that.',
            'own': False},
           {'h': 'A pure core is easy to test',
            'p': 'Keep I/O at the edges: main reads and writes, while the core accepts borrowed '
                 'data and returns a value or typed error. Use &str for text the core only reads; '
                 '&String unnecessarily requires an owned String at the call site. A borrowed '
                 'config lets multiple operations read it without moving it.',
            'code': 'fn remaining(total: i32, used: i32) -> i32 {\n'
                    '    total - used\n'
                    '}\n'
                    '#[test]\n'
                    'fn no_use() {\n'
                    '    assert_eq!(remaining(9, 0), 9);\n'
                    '}\n'
                    'fn main() {\n'
                    '    let left = remaining(9, 2);\n'
                    '    println!("{left}");\n'
                    '}',
            'note': 'Clippy is a compiler companion that flags working code with avoidable '
                    'problems. clippy::ptr_arg flags &String parameters when &str is enough. A '
                    'test should check a boundary case, not depend on the process arguments or '
                    'filesystem.'}],
 'problems': [{'type': 'better',
               'prompt': 'Both calculate the total for two batches. Which keeps parsing at the '
                         'boundary as the number of operations grows?',
               'a': 'struct Config { size: i32 }\n'
                    'fn batch(c: &Config, n: i32) -> i32 {\n'
                    '    c.size * n\n'
                    '}\n'
                    'fn main() {\n'
                    '    let c = Config {\n'
                    '        size: "6".parse().unwrap(),\n'
                    '    };\n'
                    '    let total = batch(&c, 2) + batch(&c, 3);\n'
                    '    println!("{total}");\n'
                    '}',
               'b': 'fn batch(raw: &str, n: i32) -> i32 {\n'
                    '    let size: i32 = raw.parse().unwrap();\n'
                    '    size * n\n'
                    '}\n'
                    'fn main() {\n'
                    '    let first = batch("6", 2);\n'
                    '    let total = first + batch("6", 3);\n'
                    '    println!("{total}");\n'
                    '}',
               'answer': 'a',
               'lint': None,
               'good': 'One conversion produces a typed config shared by operations. Repeated '
                       'parsing does the sample job, but couples every operation to input syntax.',
               'bad': 'Count conversions as more operations are added.',
               'wrap': False},
              {'type': 'fill',
               'prompt': 'Keep the parser error typed. Which library error variant lets ? convert '
                         'a failed integer parse?',
               'code': 'use std::num::ParseIntError;\n'
                       '#[derive(Debug)]\n'
                       'enum ArgError { Number(ParseIntError) }\n'
                       'impl From<ParseIntError> for ArgError {\n'
                       '    fn from(e: ParseIntError) -> Self {\n'
                       '        Self::__(e)\n'
                       '    }\n'
                       '}\n'
                       'fn count(s: &str) -> Result<i32, ArgError> {\n'
                       '    Ok(s.parse()?)\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{}", count("8").unwrap());\n'
                       '    match count("bad") {\n'
                       '        Err(ArgError::Number(_)) => {\n'
                       '            println!("bad count");\n'
                       '        }\n'
                       '        Ok(n) => println!("{n}"),\n'
                       '    }\n'
                       '}',
               'bank': ['Number', 'Missing', 'Ok'],
               'answer': ['Number'],
               'good': 'The variant retains the source error; From lets ? return an ArgError.',
               'bad': 'The conversion must construct the enum, not a different Result.',
               'output': ['8', 'bad count'],
               'wrap': False},
              {'type': 'output',
               'prompt': 'A caller can recover by matching a typed reason. What does the boundary '
                         'print?',
               'code': 'enum InputError { Missing, Invalid }\n'
                       'fn parse(s: &str)\n'
                       '    -> Result<i32, InputError>\n'
                       '{\n'
                       '    if s.is_empty() {\n'
                       '        return Err(InputError::Missing);\n'
                       '    }\n'
                       '    Err(InputError::Invalid)\n'
                       '}\n'
                       'fn main() {\n'
                       '    match parse("") {\n'
                       '        Ok(n) => println!("{n}"),\n'
                       '        Err(InputError::Missing) => {\n'
                       '            println!("usage");\n'
                       '        }\n'
                       '        Err(InputError::Invalid) => {\n'
                       '            println!("invalid");\n'
                       '        }\n'
                       '    }\n'
                       '}',
               'bank': ['usage', 'invalid', '0'],
               'answer': ['usage'],
               'good': 'The library preserves the reason. Main selects guidance without comparing '
                       'message text.',
               'bad': 'The early return determines the variant.',
               'wrap': False},
              {'type': 'smell',
               'prompt': 'Which parameter needlessly requires an owned text type? Find '
                         'clippy::ptr_arg.',
               'code': 'fn width(s: &String) -> usize {\n'
                       '    s.len()\n'
                       '}\n'
                       'fn main() {\n'
                       '    let name = String::from("abc");\n'
                       '    println!("{}", width(&name));\n'
                       '}',
               'line': 1,
               'lint': 'clippy::ptr_arg',
               'fixed': 'fn width(s: &str) -> usize {\n'
                        '    s.len()\n'
                        '}\n'
                        'fn main() {\n'
                        '    let name = String::from("abc");\n'
                        '    println!("{}", width(&name));\n'
                        '}',
               'good': '&str accepts borrowed text from a String or a literal; the core needs no '
                       'owned-string capability.',
               'bad': 'Look at what the function actually does with its parameter.',
               'wrap': False},
              {'type': 'better',
               'prompt': 'The CLI prints a checksum; a future GUI must display it too. Which '
                         'design makes the calculation reusable without capturing stdout?',
               'a': 'fn checksum(nums: &[i32]) {\n'
                    '    let sum: i32 = nums.iter().sum();\n'
                    '    println!("{sum}");\n'
                    '}\n'
                    'fn main() { checksum(&[2, 7]); }',
               'b': 'fn checksum(nums: &[i32]) -> i32 {\n'
                    '    nums.iter().sum()\n'
                    '}\n'
                    'fn main() {\n'
                    '    let sum = checksum(&[2, 7]);\n'
                    '    println!("{sum}");\n'
                    '}',
               'answer': 'b',
               'lint': None,
               'good': 'Returning a value lets each interface choose how to present it. Printing '
                       "in the helper works for today's CLI but couples the core to stdout.",
               'bad': 'Which version lets a GUI use the result as data?',
               'wrap': False},
              {'type': 'order',
               'prompt': 'Reject negative input before calculating. Arrange the parser body.',
               'head': ['fn positive(n: i32)', '    -> Result<i32, String>', '{'],
               'pool': ['if n < 0 {',
                        '    return Err(String::from("negative"));',
                        '}',
                        'Ok(n * 2)'],
               'tail': ['}', 'fn main() {', '    println!("{:?}", positive(3));',
                        '    println!("{:?}", positive(-3));', '}'],
               'output': ['Ok(6)', 'Err("negative")'],
               'good': 'Validation happens before the core transformation, and invalid input stays '
                       'an error.',
               'bad': 'Ok must be the final expression after the rejection guard.'},
              {'type': 'error',
               'prompt': 'The same config must serve two operations. Which line tries to reuse a '
                         'moved config?',
               'code': 'struct Config { path: String }\n'
                       'fn run(c: Config) {\n'
                       '    println!("{}", c.path);\n'
                       '}\n'
                       'fn main() {\n'
                       '    let c = Config {\n'
                       '        path: String::from("input"),\n'
                       '    };\n'
                       '    run(c);\n'
                       '    run(c);\n'
                       '}',
               'line': 10,
               'error_code': 'E0382',
               'good': 'The first run takes ownership. Borrow &Config when operations only read '
                       'it.',
               'bad': 'The config contains a String and is not Copy.',
               'wrap': False},
              {'type': 'fill',
               'prompt': 'Test the pure core at the empty-input boundary. Fill the expected value.',
               'code': 'fn total_bytes(s: &str, n: usize)\n'
                       '    -> usize\n'
                       '{\n'
                       '    s.len() * n\n'
                       '}\n'
                       '#[test]\n'
                       'fn empty_input() {\n'
                       '    assert_eq!(total_bytes("", 4), __);\n'
                       '}\n'
                       'fn main() { println!("checked"); }',
               'bank': ['0', '4', '1'],
               'answer': ['0'],
               'good': 'The test checks empty input without files or process arguments; even four '
                       'copies of empty text contain zero bytes.',
               'bad': 'A boundary test must assert the actual contract.',
               'output': ['checked'],
               'wrap': False}]})

# Part 3: R2/R3 insert lessons before this block; keep review ids stable.
# Cards introduce extra APIs with different examples from the problems.

# Part 3 / 31
COURSE.append({'part': 2,
 'id': 'server-structure',
 'title': 'A web server: structure',
 'summary': 'Routes, extractors, shared state, and the service/storage boundary.',
 'cards': [{'type': 'real',
            'h': 'The router chooses a handler',
            'p': 'A server receives requests and returns responses. A router maps a method (GET '
                 'reads, POST submits) and URL route to a handler function. These axum examples '
                 'are reading knowledge, not programs for our checker. A growing application '
                 'separates handler → service → storage: HTTP translation → business rules → data '
                 'access. Small examples sometimes combine layers.',
            'code': '    // build our application with a route\n'
                    '    let app = Router::new()\n'
                    '        // `GET /` goes to `root`\n'
                    '        .route("/", get(root))\n'
                    '        // `POST /users` goes to `create_user`\n'
                    '        .route("/users", post(create_user));',
            'repo': 'tokio-rs/axum',
            'tag': 'axum-v0.7.9',
            'path': 'examples/readme/src/main.rs',
            'lines': (20, 25),
            'license': 'MIT',
            'note': None,
            'own': False},
           {'type': 'real',
            'h': 'Extractors turn a request into data',
            'p': 'Json(payload) is an axum extractor: it decodes a JSON request body into a typed '
                 'value before the handler runs. Path extracts URL parameters; State supplies '
                 'shared application state. IntoResponse turns a returned value into an HTTP '
                 'response. Keep handlers thin: extract, call a service, convert its result. A '
                 'service should not need HTTP types.',
            'code': 'async fn create_user(\n'
                    '    // this argument tells axum to parse the request body\n'
                    '    // as JSON into a `CreateUser` type\n'
                    '    Json(payload): Json<CreateUser>,\n'
                    ') -> impl IntoResponse {\n'
                    '    // insert your application logic here\n'
                    '    let user = User {\n'
                    '        id: 1337,\n'
                    '        username: payload.username,\n'
                    '    };\n'
                    '\n'
                    '    // this will be converted into a JSON response\n'
                    '    // with a status code of `201 Created`\n'
                    '    (StatusCode::CREATED, Json(user))\n'
                    '}',
            'repo': 'tokio-rs/axum',
            'tag': 'axum-v0.7.9',
            'path': 'examples/readme/src/main.rs',
            'lines': (40, 54),
            'license': 'MIT',
            'note': None,
            'own': False},
           {'type': 'real',
            'h': 'Share ownership, protect mutation',
            'p': 'SharedState is an alias for Arc<RwLock<AppState>>. Arc shares one state, not '
                 'independent copies. RwLock allows multiple readers or one writer; Mutex allows '
                 'one holder. This tiny example reads storage in the handler; a larger app can '
                 'move lookup behind a service. A handler may return Result: here a missing key '
                 'becomes NOT_FOUND (404).',
            'code': 'type SharedState = Arc<RwLock<AppState>>;\n'
                    '\n'
                    '#[derive(Default)]\n'
                    'struct AppState {\n'
                    '    db: HashMap<String, Bytes>,\n'
                    '}\n'
                    '\n'
                    'async fn kv_get(\n'
                    '    Path(key): Path<String>,\n'
                    '    State(state): State<SharedState>,\n'
                    ') -> Result<Bytes, StatusCode> {\n'
                    '    let db = &state.read().unwrap().db;\n'
                    '\n'
                    '    if let Some(value) = db.get(&key) {\n'
                    '        Ok(value.clone())\n'
                    '    } else {\n'
                    '        Err(StatusCode::NOT_FOUND)\n'
                    '    }\n'
                    '}',
            'repo': 'tokio-rs/axum',
            'tag': 'axum-v0.7.9',
            'path': 'examples/key-value-store/src/main.rs',
            'lines': (84, 102),
            'license': 'MIT',
            'note': None,
            'own': False},
           {'h': 'Practice the boundaries with std',
            'p': 'The problems simulate requests and responses with structs, not HTTP. A storage '
                 'trait defines data access; a service uses it to enforce a rule. Thread + '
                 'Arc<Mutex<_>> exercises shared ownership only. It does not test async '
                 'scheduling. A response status is a number here: 200 success, 400 bad input, 404 '
                 'missing, 500 internal failure. Three spellings you will meet: &impl Stock is '
                 'a reference to any type with that trait; &*guard borrows the value inside a '
                 'lock guard; 404_i32 is 404 written as an i32.',
            'code': 'trait Stock { fn available(&self) -> i32; }\n'
                    'struct Shelf;\n'
                    'impl Stock for Shelf {\n'
                    '    fn available(&self) -> i32 { 12 }\n'
                    '}\n'
                    'fn can_ship(s: &impl Stock) -> bool {\n'
                    '    s.available() > 0\n'
                    '}\n'
                    'println!("{}", can_ship(&Shelf));',
            'note': None}],
 'problems': [{'type': 'fill',
               'prompt': 'Forward the request limit, not a fixed value.',
               'code': 'struct Request { limit: i32 }\n'
                       'struct Response { count: i32 }\n'
                       'fn handle(r: Request) -> Response {\n'
                       '    Response { count: __ }\n'
                       '}\n'
                       'fn main() {\n'
                       '    let r = Request { limit: 7 };\n'
                       '    println!("{}", handle(r).count);\n'
                       '}',
               'bank': ['r.limit', '0', '1'],
               'answer': ['r.limit'],
               'good': 'A handler translates the actual input into the response.',
               'bad': 'Which value comes from this request?',
               'output': ['7'],
               'wrap': False},
              {'type': 'better',
               'prompt': 'Both compute available stock. Which keeps the service independent of '
                         'HTTP?',
               'a': 'struct Response { count: i32 }\n'
                    'fn stock() -> Response {\n'
                    '    Response { count: 8 }\n'
                    '}\n'
                    'fn main() {\n'
                    '    println!("{}", stock().count);\n'
                    '}',
               'b': 'struct Response { count: i32 }\n'
                    'fn stock() -> i32 { 8 }\n'
                    'fn handle() -> Response {\n'
                    '    Response { count: stock() }\n'
                    '}\n'
                    'fn main() {\n'
                    '    println!("{}", handle().count);\n'
                    '}',
               'answer': 'b',
               'lint': None,
               'good': 'B leaves response construction at the boundary; stock returns domain data.',
               'bad': 'Which stock function could a CLI call without knowing Response?',
               'wrap': False},
              {'type': 'output',
               'prompt': 'One route selects one handler. What is printed?',
               'code': 'fn route(method: &str) -> i32 {\n'
                       '    match method {\n'
                       '        "GET" => 200,\n'
                       '        "POST" => 201,\n'
                       '        _ => 405,\n'
                       '    }\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{}", route("POST"));\n'
                       '    println!("{}", route("DELETE"));\n'
                       '}',
               'bank': ['200', '201', '404', '405'],
               'answer': ['201', '405'],
               'good': 'The method chooses the branch; unsupported methods get 405.',
               'bad': 'Follow the matching method, then the fallback.',
               'wrap': False},
              {'type': 'fill',
               'prompt': 'Make the service read through its storage contract.',
               'code': 'trait Store { fn count(&self) -> i32; }\n'
                       'struct Memory;\n'
                       'impl Store for Memory {\n'
                       '    fn count(&self) -> i32 { 6 }\n'
                       '}\n'
                       'fn remaining(s: &impl Store) -> i32 {\n'
                       '    __ - 2\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{}", remaining(&Memory));\n'
                       '}',
               'bank': ['s.count()', '0', '2'],
               'answer': ['s.count()'],
               'good': 'The service applies its reservation rule to the stored count.',
               'bad': 'Which expression reads storage?',
               'output': ['4'],
               'wrap': False},
              {'type': 'error',
               'prompt': 'Which line tries to send Rc state to a worker?',
               'code': 'use std::rc::Rc;\n'
                       'use std::thread;\n'
                       'fn main() {\n'
                       '    let total = Rc::new(4);\n'
                       '    let job = thread::spawn(move || *total);\n'
                       '    println!("{}", job.join().unwrap());\n'
                       '}',
               'line': 5,
               'error_code': 'E0277',
               'good': 'Rc cannot cross a thread boundary; Arc supports shared ownership between '
                       'threads.',
               'bad': 'Find where the closure and its captured Rc cross into a thread.',
               'wrap': False},
              {'type': 'order',
               'prompt': 'Build a request, handle it, then print the returned count.',
               'head': ['struct Request { count: i32 }',
                        'fn handle(r: Request) -> i32 { r.count }',
                        'fn main() {'],
               'pool': ['    let request = Request { count: 9 };',
                        '    let count = handle(request);',
                        '    println!("{count}");'],
               'tail': ['}'],
               'output': ['9'],
               'good': 'Each step needs the previous value.',
               'bad': 'A response cannot be printed before it exists.'},
              {'type': 'output',
               'prompt': 'A worker updates shared request state. What does main print?',
               'code': 'use std::sync::{Arc, Mutex};\n'
                       'use std::thread;\n'
                       'fn main() {\n'
                       '    let hits = Arc::new(Mutex::new(2));\n'
                       '    let worker_hits = Arc::clone(&hits);\n'
                       '    let job = thread::spawn(move || {\n'
                       '        *worker_hits.lock().unwrap() += 3;\n'
                       '    });\n'
                       '    job.join().unwrap();\n'
                       '    println!("{}", *hits.lock().unwrap());\n'
                       '}',
               'bank': ['2', '3', '5', '8'],
               'answer': ['5'],
               'good': 'Both owners reach the same Mutex. Joining finishes the update before '
                       'reading.',
               'bad': 'Arc::clone does not clone the protected count.',
               'wrap': False},
              {'type': 'better',
               'prompt': 'Both return the total. Which names the request fields so a caller can '
                         'judge their roles?',
               'a': 'struct Request { saved: i32, added: i32 }\n'
                    'fn total(r: Request) -> i32 {\n'
                    '    r.saved + r.added\n'
                    '}\n'
                    'fn main() {\n'
                    '    let r = Request { saved: 3, added: 4 };\n'
                    '    println!("{}", total(r));\n'
                    '}',
               'b': 'fn total(r: (i32, i32)) -> i32 {\n'
                    '    r.0 + r.1\n'
                    '}\n'
                    'fn main() {\n'
                    '    println!("{}", total((3, 4)));\n'
                    '}',
               'answer': 'a',
               'lint': None,
               'good': 'Named fields describe the contract; positional fields require remembering '
                       'their meaning.',
               'bad': 'Which caller explains what each number represents?',
               'wrap': False}]})

COURSE.append({'part': 2,
 'id': 'server-rules',
 'title': 'A web server: rules',
 'summary': 'Read async code; keep locks short and convert typed errors at the boundary.',
 'cards': [{'type': 'real',
            'h': 'A command delegates to storage',
            'p': 'mini-redis is a TCP server, not HTTP, but the same boundary applies: its Get '
                 'command asks Db for data and then writes a protocol response. Read async fn as a '
                 'function that returns a future: work that can be driven to completion. Calling '
                 'it does not run its body immediately. At .await, the current task waits for a '
                 'future; if it is not ready, the runtime can run other tasks on that worker.',
            'code': '    pub(crate) async fn apply(self, db: &Db, dst: &mut Connection) -> '
                    'crate::Result<()> {\n'
                    '        // Get the value from the shared database state\n'
                    '        let response = if let Some(value) = db.get(&self.key) {\n'
                    '            // If a value is present, it is written to the client in "bulk"\n'
                    '            // format.\n'
                    '            Frame::Bulk(value)\n'
                    '        } else {\n'
                    '            // If there is no value, `Null` is written.\n'
                    '            Frame::Null\n'
                    '        };\n'
                    '\n'
                    '        debug!(?response);\n'
                    '\n'
                    '        // Write the response back to the client\n'
                    '        dst.write_frame(&response).await?;\n'
                    '\n'
                    '        Ok(())\n'
                    '    }',
            'repo': 'tokio-rs/mini-redis',
            'tag': 'v0.3.0',
            'path': 'src/cmd/get.rs',
            'lines': (64, 81),
            'license': 'MIT',
            'note': None,
            'own': False},
           {'type': 'real',
            'h': 'Return data without the guard',
            'p': 'Db::get locks, copies a Bytes handle, and returns owned data. The guard ends '
                 'with this function, before apply reaches its network .await. Bytes is an '
                 'external crate type with a cheap shared-data clone. Keep a synchronous lock '
                 'short; holding it across .await may deadlock or delay unrelated requests, and '
                 'can make a future unsuitable for axum. Even an async mutex can cause long waits '
                 'if held during unrelated I/O.',
            'code': '    pub(crate) fn get(&self, key: &str) -> Option<Bytes> {\n'
                    '        // Acquire the lock, get the entry and clone the value.\n'
                    '        //\n'
                    '        // Because data is stored using `Bytes`, a clone here is a shallow\n'
                    '        // clone. Data is not copied.\n'
                    '        let state = self.shared.state.lock().unwrap();\n'
                    '        state.entries.get(key).map(|entry| entry.data.clone())\n'
                    '    }',
            'repo': 'tokio-rs/mini-redis',
            'tag': 'v0.3.0',
            'path': 'src/db.rs',
            'lines': (121, 128),
            'license': 'MIT',
            'note': None,
            'own': False},
           {'type': 'real',
            'h': 'One conversion for application errors',
            'p': 'This match is inside AppError::into_response. Invalid JSON uses its rejection '
                 'status; a library failure is logged and becomes a generic 500 response. Typed '
                 'errors retain meaning inside the app, then one boundary decides status and '
                 'public message. Avoid copying this decision into every handler.',
            'code': '        let (status, message) = match self {\n'
                    '            AppError::JsonRejection(rejection) => {\n'
                    "                // This error is caused by bad user input so don't log it\n"
                    '                (rejection.status(), rejection.body_text())\n'
                    '            }\n'
                    '            AppError::TimeError(err) => {\n'
                    '                // Because `TraceLayer` wraps each request in a span that '
                    'contains the request\n'
                    "                // method, uri, etc we don't need to include those details "
                    'here\n'
                    '                tracing::error!(%err, "error from time_library");\n'
                    '\n'
                    "                // Don't expose any details about the error to the client\n"
                    '                (\n'
                    '                    StatusCode::INTERNAL_SERVER_ERROR,\n'
                    '                    "Something went wrong".to_owned(),\n'
                    '                )\n'
                    '            }\n'
                    '        };\n'
                    '\n'
                    '        (status, AppJson(ErrorResponse { message })).into_response()',
            'repo': 'tokio-rs/axum',
            'tag': 'axum-v0.7.9',
            'path': 'examples/error-handling/src/main.rs',
            'lines': (166, 184),
            'license': 'MIT',
            'note': None,
            'own': False},
           {'h': 'Do not block an async worker',
            'p': 'Reading knowledge: synchronous disk calls, thread::sleep, and long CPU loops '
                 'occupy the worker instead of yielding. Prefer async I/O, or move synchronous '
                 'work to tokio::task::spawn_blocking and await its result. Our std problems can '
                 'prove lock lifetime and error mapping, not runtime responsiveness. '
                 'Result::unwrap_or supplies a fallback on Err. std::sync::Mutex::try_lock '
                 'attempts acquisition without waiting and returns Result; .is_ok() tests for Ok. '
                 'This lets an exercise observe whether a lock was released.',
            'code': 'use std::sync::Mutex;\n'
                    'let gate = Mutex::new(11);\n'
                    '{\n'
                    '    let held = gate.lock().unwrap();\n'
                    '    println!("{}", *held);\n'
                    '}\n'
                    'println!("{}", gate.try_lock().is_ok());',
            'note': None}],
 'problems': [{'type': 'fill',
               'prompt': 'Map a missing record to 404 in this one conversion.',
               'code': 'enum Failure { Missing, Busy }\n'
                       'fn status(e: Failure) -> i32 {\n'
                       '    match e {\n'
                       '        Failure::Missing => __,\n'
                       '        Failure::Busy => 503,\n'
                       '    }\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{}", status(Failure::Missing));\n'
                       '    println!("{}", status(Failure::Busy));\n'
                       '}',
               'bank': ['400', '404', '500'],
               'answer': ['404'],
               'good': 'The typed reason selects the public status at the boundary.',
               'bad': 'Missing is different from invalid input or an internal failure.',
               'output': ['404', '503'],
               'wrap': False},
              {'type': 'better',
               'prompt': 'Both return 500. Which preserves an error reason inside the service?',
               'a': 'enum Failure { Unavailable }\n'
                    'fn load() -> Result<i32, Failure> {\n'
                    '    Err(Failure::Unavailable)\n'
                    '}\n'
                    'fn main() {\n'
                    '    let status = match load() {\n'
                    '        Ok(_) => 200,\n'
                    '        Err(Failure::Unavailable) => 500,\n'
                    '    };\n'
                    '    println!("{status}");\n'
                    '}',
               'b': 'fn load() -> Result<i32, i32> {\n'
                    '    Err(500)\n'
                    '}\n'
                    'fn main() {\n'
                    '    let status = match load() {\n'
                    '        Ok(_) => 200,\n'
                    '        Err(status) => status,\n'
                    '    };\n'
                    '    println!("{status}");\n'
                    '}',
               'answer': 'a',
               'lint': None,
               'good': 'A returns a domain reason; only the boundary knows its HTTP meaning.',
               'bad': 'Which service could a non-HTTP caller interpret by reason?',
               'wrap': False},
              {'type': 'output',
               'prompt': 'Is the lock free after this snapshot is taken?',
               'code': 'use std::sync::Mutex;\n'
                       'fn main() {\n'
                       '    let rows = Mutex::new(6);\n'
                       '    let snapshot = {\n'
                       '        let guard = rows.lock().unwrap();\n'
                       '        *guard\n'
                       '    };\n'
                       '    println!("{snapshot}");\n'
                       '    println!("{}", rows.try_lock().is_ok());\n'
                       '}',
               'bank': ['6', 'true', 'false'],
               'answer': ['6', 'true'],
               'good': 'The block returns the copied count and drops the guard. This is a '
                       'synchronous lifetime check.',
               'bad': 'The snapshot is an integer, not a guard.',
               'wrap': False},
              {'type': 'error',
               'prompt': 'Which line returns a reference tied to a local lock guard?',
               'code': 'use std::sync::Mutex;\n'
                       'fn read(rows: &Mutex<i32>) -> &i32 {\n'
                       '    let guard = rows.lock().unwrap();\n'
                       '    &*guard\n'
                       '}\n'
                       'fn main() {}',
               'line': 4,
               'error_code': 'E0515',
               'good': 'The guard is local; return owned data rather than a borrow that would '
                       'outlive the guard.',
               'bad': 'The caller cannot retain access after this local guard is dropped.',
               'wrap': False},
              {'type': 'order',
 'prompt': 'Reserve two units and read the remaining stock under the same guard.',
 'head': ['use std::sync::Mutex;', 'fn main() {', '    let stock = Mutex::new(6);'],
 'pool': ['    let mut guard = stock.lock().unwrap();',
          '    *guard -= 2;',
          '    let remaining = *guard;',
          '    println!("{remaining}");'],
 'tail': ['}'],
 'output': ['4'],
 'good': 'The same guard protects the read-modify-read sequence. Reading before subtraction would '
         'report stale stock.',
 'bad': 'The reservation must change the protected count before taking its result.'},
              {'type': 'smell',
               'prompt': 'Find the needless clone of a Copy status number.',
               'code': 'let status = 404_i32;\n'
                       'let response = status.clone();\n'
                       'println!("{response}");',
               'line': 2,
               'lint': 'clippy::clone_on_copy',
               'fixed': 'let status = 404_i32;\nlet response = status;\nprintln!("{response}");',
               'good': 'Integers copy on assignment; clone adds no ownership benefit.',
               'bad': 'Which value already implements Copy?',
               'wrap': True},
              {'type': 'better',
               'prompt': 'Both charge a reservation fee. Which keeps the handler thin as the rule '
                         'grows?',
               'a': 'struct Request { units: i32 }\n'
                    'fn handle(r: Request) -> i32 {\n'
                    '    let n = r.units;\n'
                    '    let fee = if n > 5 { 2 } else { 1 };\n'
                    '    r.units + fee\n'
                    '}\n'
                    'fn main() {\n'
                    '    let r = Request { units: 7 };\n'
                    '    println!("{}", handle(r));\n'
                    '}',
               'b': 'struct Request { units: i32 }\n'
                    'fn reserve(units: i32) -> i32 {\n'
                    '    let fee = if units > 5 { 2 } else { 1 };\n'
                    '    units + fee\n'
                    '}\n'
                    'fn handle(r: Request) -> i32 {\n'
                    '    reserve(r.units)\n'
                    '}\n'
                    'fn main() {\n'
                    '    let r = Request { units: 7 };\n'
                    '    println!("{}", handle(r));\n'
                    '}',
               'answer': 'b',
               'lint': None,
               'good': 'B puts the business rule in reserve, usable without Request.',
               'bad': 'Which rule can another interface reuse?',
               'wrap': False},
              {'type': 'fill',
               'prompt': 'Propagate storage failure before adding the service adjustment.',
               'code': '#[derive(Debug)]\n'
                       'enum Failure { Offline }\n'
                       'fn read() -> Result<i32, Failure> {\n'
                       '    Err(Failure::Offline)\n'
                       '}\n'
                       'fn total() -> Result<i32, Failure> {\n'
                       '    let count = read()__;\n'
                       '    Ok(count + 1)\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{:?}", total());\n'
                       '}',
               'bank': ['?', '.unwrap()', '.unwrap_or(0)'],
               'answer': ['?'],
               'good': '? returns the storage error before success-only work; the alternatives '
                       'panic or conceal the failure.',
               'bad': 'A failed storage read must stay a failure.',
               'output': ['Err(Offline)'],
               'wrap': False}]})

COURSE.append({'part': 2,
 'id': 'server-own',
 'title': 'Your own server',
 'summary': 'Judge the AI-built Websidian server against the same rules.',
 'cards': [{'type': 'real',
            'h': 'Keep: the hub offloads blocking work',
            'p': 'Websidian is your AI-built axum server. Main composes feature routers; apps hold '
                 'feature behavior, readers gather data, and store owns writes. Its hub gathers '
                 'data through readers and '
                 'caches the response. Here answer runs on the blocking pool, then the async '
                 'handler awaits the result and constructs a response. Unlike axum’s tiny '
                 'in-memory example, this boundary is appropriate for synchronous readers. Keep '
                 'it. This excerpt is display-only; no code in your server was run or changed. In '
                 'std exercises, format! builds a String using the same placeholders as println!, '
                 'without printing.',
            'code': 'pub fn router(app: PathBuf) -> Router {\n'
                    '    let cache: Cache = Arc::default();\n'
                    "    let serve = |route: &'static str| {\n"
                    '        let (app, cache) = (app.clone(), cache.clone());\n'
                    '        get(move || async move {\n'
                    '            let r = tokio::task::spawn_blocking(move || answer(&app, route, '
                    '&cache)).await.unwrap_or_else(|e| Err(e.to_string()));\n'
                    '            match r {\n'
                    '                Ok(body) => ([(header::CONTENT_TYPE, "application/json")], '
                    'body).into_response(),\n'
                    "                // Any reader may fail: answer, don't drop.\n"
                    '                Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, '
                    'Json(json!({"error": e}))).into_response(),\n'
                    '            }\n'
                    '        })\n'
                    '    };',
            'repo': None,
            'tag': '911d8146d36be95d5022ba651cf340078e6073bf',
            'path': 'src/hub.rs',
            'lines': (70, 82),
            'license': 'Owner permission',
            'note': None,
            'own': True},
           {'type': 'real',
            'h': 'Keep: the inbox router delegates',
            'p': 'These route closures select operations; helpers such as raw and save do the work '
                 'and answer formats the result. State extracts one shared app value, similar to '
                 'axum’s state example. Keep the clear routing table and shared ownership. This '
                 'alone does not make the synchronous helper calls safe for an async worker. URL '
                 'routes here identify API operations, not files.',
            'code': '    Router::new()\n'
                    '        .route("/api/inbox", get(|State(a): App| async move { '
                    'Json(listing(&a)) }))\n'
                    '        .route("/api/staged", get(|State(a): App, uri: Uri| async move { '
                    'staged(&a, &uri) }))\n'
                    '        .route("/api/raw", get(|State(a): App, uri: Uri| async move { '
                    'answer(raw(&a, &uri)) }))\n'
                    '        .route("/api/drop", post(|State(a): App, h: HeaderMap, b: Bytes| '
                    'async move { answer(drop(&a, &h, &b)) }))\n'
                    '        .route("/api/note", post(|State(a): App, b: Bytes| async move { '
                    'answer(note(&a, &b)) }))\n'
                    '        .route("/api/save", post(|State(a): App, b: Bytes| async move { '
                    'answer(save(&a, &b)) }))\n'
                    '        .route("/api/move", post(|State(a): App, b: Bytes| async move { '
                    'answer(move_(&a, &b)) }))\n'
                    '        .route("/api/mkdir", post(|State(a): App, b: Bytes| async move { '
                    'answer(mkdir(&a, &b)) }))\n'
                    '        .route("/api/unstage", post(|State(a): App, b: Bytes| async move { '
                    'answer(unstage(&a, &b)) }))\n'
                    '        .layer(DefaultBodyLimit::disable())                     // a dropped '
                    'video is as big as it is\n'
                    '        .with_state(Arc::new(app))',
            'repo': None,
            'tag': '911d8146d36be95d5022ba651cf340078e6073bf',
            'path': 'src/inbox.rs',
            'lines': (534, 545),
            'license': 'Owner permission',
            'note': None,
            'own': True},
           {'type': 'real',
            'h': 'Improve: move synchronous work off workers',
            'p': 'These Knowledge closures call listing and graph directly inside async bodies. '
                 'Reading their implementations shows synchronous filesystem and SQLite work. '
                 'async move does not turn that work into async I/O. Follow the hub’s '
                 'blocking-pool boundary, keeping handler → service → storage. No .await here '
                 'means this is blocking work on a worker, not a demonstrated lock-across-await '
                 'bug.',
            'code': '        .route("/api/knowledge", get(move || async move { answer(listing(&a, '
                    '&root(&a)).map(Some)) }))\n'
                    '        .route("/api/knowledge/graph", get(move || async move { '
                    'answer(graph(&b, &root(&b)).map(Some)) }))\n'
                    '        .route("/api/knowledge/", get(|| async { answer(Ok(None)) }))',
            'repo': None,
            'tag': '911d8146d36be95d5022ba651cf340078e6073bf',
            'path': 'src/knowledge.rs',
            'lines': (485, 487),
            'license': 'Owner permission',
            'note': None,
            'own': True},
           {'type': 'real',
            'h': 'Improve: central conversion, safer public errors',
            'p': 'Good: answer centralizes success, missing entries and internal errors, like '
                 'axum’s IntoResponse example. Improve: it exposes the SQLite error text to the '
                 'client. Keep the detail in server diagnostics and return a stable generic '
                 'message. A typed application error would separate storage details from the '
                 'public contract.',
            'code': 'fn answer(r: rusqlite::Result<Option<Value>>) -> (StatusCode, Json<Value>) {\n'
                    '    match r {\n'
                    '        Ok(Some(v)) => (StatusCode::OK, Json(v)),\n'
                    '        Ok(None) => (StatusCode::NOT_FOUND, Json(json!({"error": "no such '
                    'entry"}))),\n'
                    '        Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"error": '
                    'format!("sqlite: {e}")}))),\n'
                    '    }\n'
                    '}',
            'repo': None,
            'tag': '911d8146d36be95d5022ba651cf340078e6073bf',
            'path': 'src/knowledge.rs',
            'lines': (453, 459),
            'license': 'Owner permission',
            'note': None,
            'own': True},
           {'type': 'real',
            'h': 'Improve: narrow the cache lock',
            'p': 'After checking a cached stamp, answer keeps the map guard while calling a '
                 'reader; the rest of the function also assembles data before inserting it. This '
                 'serializes unrelated cache entries. Copy a hit inside a short scope; rebuild a '
                 'miss outside the global map lock. Use per-entry coordination and recheck '
                 'freshness to avoid duplicate or stale rebuilds. This is a synchronous contention '
                 'finding, not evidence of a guard crossing .await. Be fair when you review: a '
                 'comment in this file says the single lock is a chosen shortcut, to split if the '
                 'wait is ever felt. For a one-user server that is a reasonable trade, so this is '
                 'an option, not a bug.',
            'code': '    let stamp = stamp(app)?;\n'
                    '    let mut cache = cache.lock().unwrap_or_else(|e| e.into_inner());\n'
                    '    if let Some((s, body)) = cache.get(route) && *s == stamp { return '
                    'Ok(body.clone()) }\n'
                    '    let notes = readers::read("pages", app, None).unwrap()?;\n'
                    '    let body = if route == "/api/notes" { notes.to_string() } else {\n'
                    '        let (meta, unknown) = meta::assemble(app, '
                    'notes.as_array().unwrap())?;',
            'repo': None,
            'tag': '911d8146d36be95d5022ba651cf340078e6073bf',
            'path': 'src/hub.rs',
            'lines': (48, 53),
            'license': 'Owner permission',
            'note': None,
            'own': True}],
 'problems': [{'type': 'better',
               'prompt': 'Both print a cached count. Which releases the map lock before formatting '
                         'the response?',
               'a': 'use std::sync::Mutex;\n'
                    'fn main() {\n'
                    '    let cache = Mutex::new(7);\n'
                    '    let guard = cache.lock().unwrap();\n'
                    '    let body = format!("count={}", *guard);\n'
                    '    println!("{body}");\n'
                    '}',
               'b': 'use std::sync::Mutex;\n'
                    'fn main() {\n'
                    '    let cache = Mutex::new(7);\n'
                    '    let count = {\n'
                    '        let guard = cache.lock().unwrap();\n'
                    '        *guard\n'
                    '    };\n'
                    '    let body = format!("count={count}");\n'
                    '    println!("{body}");\n'
                    '}',
               'answer': 'b',
               'lint': None,
               'good': 'B copies the needed value, releases the guard, then formats. This proves a '
                       'std scope, not an async property.',
               'bad': 'Formatting does not need exclusive access to the cache.',
               'wrap': False},
              {'type': 'fill',
               'prompt': 'Keep storage details out of this public error body.',
               'code': 'fn public_error(detail: &str) -> &str {\n'
                       '    let _ = detail;\n'
                       '    __\n'
                       '}\n'
                       'fn main() {\n'
                       '    let body = public_error("db failed");\n'
                       '    println!("{body}");\n'
                       '}',
               'bank': ['detail', '"internal error"', '"db failed"'],
               'answer': ['"internal error"'],
               'good': 'The boundary returns a stable message instead of backend details.',
               'bad': 'The caller should not see the supplied detail.',
               'output': ['internal error'],
               'wrap': False},
              {'type': 'output',
               'prompt': 'A service rejects invalid input before storage changes. What is printed?',
               'code': 'fn save(rows: &mut Vec<i32>, n: i32)\n'
                       '    -> Result<(), String>\n'
                       '{\n'
                       '    if n < 0 {\n'
                       '        return Err(String::from("invalid"));\n'
                       '    }\n'
                       '    rows.push(n);\n'
                       '    Ok(())\n'
                       '}\n'
                       'fn main() {\n'
                       '    let mut rows = vec![3];\n'
                       '    println!("{:?}", save(&mut rows, -1));\n'
                       '    println!("{}", rows.len());\n'
                       '}',
               'bank': ['Err("invalid")', 'Ok(())', '1', '2'],
               'answer': ['Err("invalid")', '1'],
               'good': 'Validation returns before mutation, so the stored row count stays one.',
               'bad': 'Does the rejected request reach push?',
               'wrap': False},
              {'type': 'error',
               'prompt': 'Which line tries to move shared app state into two owners?',
               'code': 'use std::sync::Arc;\n'
                       'fn main() {\n'
                       '    let state = Arc::new(String::from("ok"));\n'
                       '    let inbox = state;\n'
                       '    let knowledge = state;\n'
                       '    println!("{inbox} {knowledge}");\n'
                       '}',
               'line': 5,
               'error_code': 'E0382',
               'good': 'Assignment moves the Arc handle. Arc::clone creates a second handle to the '
                       'same app state.',
               'bad': 'Sharing the inner data still requires a handle for each owner.',
               'wrap': False},
              {'type': 'order',
               'prompt': 'Run the boundary conversion after the service, then print the response.',
               'head': ['fn load() -> Option<i32> { None }',
                        'fn status(n: Option<i32>) -> i32 {',
                        '    match n { Some(_) => 200, None => 404 }',
                        '}',
                        'fn main() {'],
               'pool': ['    let result = load();',
                        '    let response = status(result);',
                        '    println!("{response}");'],
               'tail': ['}'],
               'output': ['404'],
               'good': 'The service returns domain data; the boundary converts it exactly once.',
               'bad': 'The converter must receive the service result before printing.'},
              {'type': 'better',
               'prompt': 'Both count saved rows. Which hides storage representation behind its '
                         'API?',
               'a': 'struct Store { rows: Vec<i32> }\n'
                    'impl Store {\n'
                    '    fn count(&self) -> usize {\n'
                    '        self.rows.len()\n'
                    '    }\n'
                    '}\n'
                    'fn saved(s: &Store) -> usize { s.count() }\n'
                    'fn main() {\n'
                    '    let s = Store { rows: vec![2, 4] };\n'
                    '    println!("{}", saved(&s));\n'
                    '}',
               'b': 'struct Store { rows: Vec<i32> }\n'
                    'fn saved(s: &Store) -> usize {\n'
                    '    s.rows.len()\n'
                    '}\n'
                    'fn main() {\n'
                    '    let s = Store { rows: vec![2, 4] };\n'
                    '    println!("{}", saved(&s));\n'
                    '}',
               'answer': 'a',
               'lint': None,
               'good': 'A exposes a storage operation; changing the representation need not change '
                       'saved.',
               'bad': 'Which service reaches into the underlying vector?',
               'wrap': False},
              {'type': 'fill',
               'prompt': 'The test must cover the missing-record response, not just success.',
               'code': 'fn status(found: bool) -> i32 {\n'
                       '    if found { 200 } else { 404 }\n'
                       '}\n'
                       '#[test]\n'
                       'fn missing_record() {\n'
                       '    assert_eq!(status(__), 404);\n'
                       '}\n'
                       'fn main() {\n'
                       '    println!("{}", status(false));\n'
                       '}',
               'bank': ['true', 'false'],
               'answer': ['false'],
               'good': 'The checker also runs the test harness: false exercises the missing-record '
                       'branch.',
               'bad': 'Which input represents a record that is absent?',
               'output': ['404'],
               'wrap': False},
              {'type': 'output',
               'prompt': 'The handler uses a service result to choose its response. What does it '
                         'print?',
               'code': 'fn find(id: i32) -> Option<i32> {\n'
                       '    if id == 3 { Some(12) } else { None }\n'
                       '}\n'
                       'struct Response { status: i32, count: i32 }\n'
                       'fn handle(id: i32) -> Response {\n'
                       '    match find(id) {\n'
                       '        Some(count) => Response {\n'
                       '            status: 200, count,\n'
                       '        },\n'
                       '        None => Response {\n'
                       '            status: 404, count: 0,\n'
                       '        },\n'
                       '    }\n'
                       '}\n'
                       'fn main() {\n'
                       '    let r = handle(3);\n'
                       '    println!("{} {}", r.status, r.count);\n'
                       '}',
               'bank': ['200 12', '404 0', '200 3', '404 12'],
               'answer': ['200 12'],
               'good': 'The found value becomes response data; status describes the outcome.',
               'bad': 'Keep the requested id distinct from the returned count.',
               'wrap': False}]})

COURSE.append({
    'part': 3,
    'id': 'smells',
    'title': "Clippy's top smells",
    'summary': 'Working code can still ask for too much. Let Clippy help.',
    "cards": [
        card(
            h='Read what the code promises',
            p='Rust checks types and borrowing; Clippy flags suspicious patterns in working code. Read a function signature and its callers before accepting a warning. The example uses contains, a collection method that returns a bool for membership.',
            code='''let colors = ["red", "blue"];
let found = colors.contains(&"red");
println!("{found}");''',
            note='A lint is evidence about one pattern, not proof that the whole design is right.',
        ),
        card(
            h='Copies and panics need a reason',
            p='Clone when an independent value is needed. Unwrap is appropriate only when an invariant proves success. get returns an Option instead of panicking for a missing index; a caller can then decide what failure means. parse turns text into a requested type and returns a Result: invalid input gives Err. parse::<u32>() chooses u32 explicitly; parse() can infer the type from context. String::push appends one character.',
            code='''let sizes = [10, 20];
let requested = sizes.get(5);
println!("{requested:?}");''',
            note='Judgement calls compare stated requirements. Equal output on one valid input does not check the failure policy.',
        ),
    ],
    "problems": [
        smell(
            prompt='Which line asks for a vector when a slice would do?',
            code='''fn first(values: &Vec<i32>) -> i32 {
    values[0]
}

fn main() {
    let values = vec![7, 8];
    println!("{}", first(&values));
}''',
            line=1,
            lint='clippy::ptr_arg',
            fixed='''fn first(values: &[i32]) -> i32 {
    values[0]
}

fn main() {
    let values = vec![7, 8];
    println!("{}", first(&values));
}''',
            good='`&[i32]` accepts a borrowed view. This function only reads a number; it needs no vector methods.',
            bad='Look at the parameter type. Does it need a whole vector?',
            wrap=False,
        ),
        better(
            prompt='A caller owns a list of words but only wants to read the number of words. Which API avoids transferring or copying ownership?',
            a='''fn count(words: Vec<String>) -> usize {
    words.len()
}
fn main() {
    let words = vec![String::from("fern")];
    println!("{}", count(words.clone()));
    println!("{}", words.len());
}''',
            b='''fn count(words: &[String]) -> usize {
    words.len()
}
fn main() {
    let words = vec![String::from("fern")];
    println!("{}", count(&words));
    println!("{}", words.len());
}''',
            answer='b',
            lint=None,
            good='The slice contract reads existing words; the owned-vector contract makes this caller clone all of them just to count. Unlike the first puzzle, this is an ownership decision, not a &Vec lint.',
            bad='Does counting consume the words?',
            wrap=False,
        ),
        smell(
            prompt='Which line unnecessarily requires an owned string type?',
            code='''fn width(text: &String) -> usize {
    text.len()
}
fn main() {
    let text = String::from("rust");
    println!("{}", width(&text));
}''',
            line=1,
            lint='clippy::ptr_arg',
            fixed='''fn width(text: &str) -> usize {
    text.len()
}
fn main() {
    let text = String::from("rust");
    println!("{}", width(&text));
}''',
            good='Reading bytes needs only &str, which also accepts string literals.',
            bad='Look at what width actually does with its argument.',
            wrap=False,
        ),
        smell(
            prompt='Which line manually compares a boolean to true?',
            code='''let ready = true;
println!("{}", ready == true);''',
            line=2,
            lint='clippy::bool_comparison',
            fixed='''let ready = true;
println!("{ready}");''',
            good='ready already is the answer: a bool.',
            bad='Which expression compares a bool with another bool?',
            wrap=True,
        ),
        smell(
            prompt='Which line spells out a boolean result with branches?',
            code='''fn allowed(n: i32) -> bool {
    if n > 0 {
        true
    } else {
        false
    }
}
fn main() {
    println!("{}", allowed(2));
}''',
            line=2,
            lint='clippy::needless_bool',
            fixed='''fn allowed(n: i32) -> bool {
    n > 0
}
fn main() {
    println!("{}", allowed(2));
}''',
            good='The comparison itself returns bool; no branches are needed.',
            bad='Which line turns a bool into the same bool?',
            wrap=False,
        ),
        better(
            prompt='User input may be invalid. Which version reports that rather than panicking?',
            a='''fn main() {
    let input = "12";
    match input.parse::<u32>() {
        Ok(n) => println!("{n}"),
        Err(_) => println!("invalid number"),
    }
}''',
            b='''fn main() {
    let input = "12";
    let n = input.parse::<u32>().unwrap();
    println!("{n}");
}''',
            answer='a',
            lint=None,
            good='A has a failure branch. The sample input succeeds in both; try thinking about oops as input.',
            bad='One successful example does not justify assuming every input parses.',
            wrap=False,
        ),
        better(
            prompt='The caller needs the original after a read-only check. Which avoids allocating a copy?',
            a='''fn main() {
    let text = String::from("rust");
    println!("{}", text.len());
    println!("{text}");
}''',
            b='''fn main() {
    let text = String::from("rust");
    let copy = text.clone();
    println!("{}", copy.len());
    println!("{text}");
}''',
            answer='a',
            lint=None,
            good='len borrows text; no independent String is needed.',
            bad='Does measuring text consume or change it?',
            wrap=False,
        ),
        fill(
            prompt='Preserve the failure from validate instead of unwrapping or replacing it. Which operator lets the caller receive Err?',
            code='''fn validate(
    n: i32,
) -> Result<i32, &'static str> {
    if n < 0 {
        Err("negative")
    } else {
        Ok(n)
    }
}
fn doubled(
    n: i32,
) -> Result<i32, &'static str> {
    let valid = validate(n)__;
    Ok(valid * 2)
}
fn main() {
    println!("{:?}", doubled(-1));
}''',
            bank=['?', '.unwrap()', '.unwrap_or(0)', '.len()'],
            answer=['?'],
            good="? forwards the original Err to this function's caller; it does not convert a failure into a normal value or panic.",
            bad='The caller must still receive the error, not a fallback result.',
            output=['Err("negative")'],
            wrap=False,
        ),
    ],
})

# Part 3 / 32
COURSE.append({
    'part': 3,
    'id': 'borrow-fights',
    'title': 'Fighting the borrow checker the wrong way',
    'summary': 'Shorten borrows and express ownership before adding copies or shared mutation.',
    "cards": [
        card(
            h='Shared ownership is a choice',
            p='Rc shares ownership on one thread. RefCell<T> checks borrowing at runtime: borrow reads, borrow_mut writes, and conflicting live borrows panic. Rc<RefCell<T>> is useful when multiple owners really must mutate one value.',
            code='''use std::cell::RefCell;
let cells = RefCell::new(vec![1]);
{
    let mut edit = cells.borrow_mut();
    edit.push(2);
}
println!("{:?}", cells.borrow());''',
            note='A block ends the edit borrow before the read. A local value with one owner usually needs only mut; do not add sharing automatically.',
        ),
        card(
            h='Find the last use of a borrow',
            p='A borrow ends after its last use, which may be earlier than the end of the block. Trace uses in order before copying a collection to silence a borrow error.',
            code='''let mut banner = String::from("hello");
let view = &banner;
println!("{view}");
banner.push('!');
println!("{banner}");''',
            note='No borrowed view is read after the change here. Later problems need information to survive a change; decide exactly what information that is.',
        ),
        real(
            h='Real code borrows slices',
            p='Rayon runs work in parallel. Here its slice method borrows a slice. It does not ask callers to own a vector.',
            code='''impl<T: Sync> ParallelSlice<T> for [T] {
    #[inline]
    fn as_parallel_slice(&self) -> &[T] {
        self
    }
}''',
            repo='rayon-rs/rayon',
            tag='v1.10.0',
            path='src/slice/mod.rs',
            lines=(203, 208),
            license='MIT',
            note="`Sync` means references to a value can be shared safely across threads. This excerpt is for reading; it needs Rayon's crate to compile. `impl<T: Sync> ParallelSlice<T> for [T]` implements the Rayon trait for slices whose element type T is Sync. `#[inline]` is an optional compiler hint to inline a function, not a promise or a correctness requirement.",
            own=False,
        ),
    ],
    "problems": [
        better(
            prompt='Only count bytes, then print the original. Which API avoids cloning at the call?',
            a='''fn size(s: &str) -> usize {
    s.len()
}
fn main() {
    let s = String::from("oak");
    println!("{}", size(&s));
    println!("{s}");
}''',
            b='''fn size(s: String) -> usize {
    s.len()
}
fn main() {
    let s = String::from("oak");
    println!("{}", size(s.clone()));
    println!("{s}");
}''',
            answer='a',
            lint=None,
            good='A expresses a read-only borrow. B forces the caller to copy merely to keep ownership.',
            bad='Does size need ownership or only a view?',
            wrap=False,
        ),
        better(
            prompt='The caller will never use the original again. Which transfers ownership without a copy?',
            a='''fn main() {
    let s = String::from("oak");
    let saved = s.clone();
    println!("{saved}");
}''',
            b='''fn main() {
    let s = String::from("oak");
    let saved = s;
    println!("{saved}");
}''',
            answer='b',
            lint=None,
            good='Moving the String transfers its allocation; cloning allocates another one unnecessarily here.',
            bad='Is any later use of s required?',
            wrap=False,
        ),
        better(
            prompt='One local counter has one owner. Which avoids runtime borrow checks?',
            a='''use std::cell::RefCell;
use std::rc::Rc;
fn main() {
    let n = Rc::new(RefCell::new(0));
    *n.borrow_mut() += 1;
    println!("{}", n.borrow());
}''',
            b='''fn main() {
    let mut n = 0;
    n += 1;
    println!("{n}");
}''',
            answer='b',
            lint=None,
            good='A single owner can use mut. Rc<RefCell<_>> adds sharing and runtime checks this requirement does not need.',
            bad='How many independent owners need to mutate n?',
            wrap=False,
        ),
        better(
            prompt='Keep the first length while growing the vector. Which avoids copying its strings?',
            a='''fn main() {
    let mut words =
        vec![String::from("oak")];
    let first_len = words[0].len();
    words.push(String::from("elm"));
    println!(
        "{} {}",
        first_len,
        words.len()
    );
}''',
            b='''fn main() {
    let mut words =
        vec![String::from("oak")];
    let snapshot = words.clone();
    let first = &snapshot[0];
    words.push(String::from("elm"));
    println!(
        "{} {}",
        first.len(),
        words.len()
    );
}''',
            answer='a',
            lint=None,
            good='Only the length must survive the push; a usize is enough. Rust rejects retaining a reference into words across push when that reference is used afterward, because push may reallocate.',
            bad='What is the smallest value the final print actually needs?',
            wrap=False,
        ),
        better(
            prompt='Change the first label in place. Which avoids cloning and replacing it?',
            a='''fn main() {
    let mut words =
        vec![String::from("oak")];
    words[0].push('!');
    println!("{}", words[0]);
}''',
            b='''fn main() {
    let mut words =
        vec![String::from("oak")];
    let mut first = words[0].clone();
    first.push('!');
    words[0] = first;
    println!("{}", words[0]);
}''',
            answer='a',
            lint=None,
            good='The vector already permits mutation, so mutate the String directly.',
            bad='Is there a second owner that needs the old text?',
            wrap=False,
        ),
        better(
            prompt='Both preserve the first label after replacing it in the list. Which snapshot copies only the label that must survive, rather than also copying unrelated labels?',
            a='''fn main() {
    let mut words = vec![
        String::from("oak"),
        String::from("pine"),
    ];
    let saved = words.clone();
    words[0] = String::from("elm");
    println!("{}", saved[0]);
}''',
            b='''fn main() {
    let mut words = vec![
        String::from("oak"),
        String::from("pine"),
    ];
    let saved = words[0].clone();
    words[0] = String::from("elm");
    println!("{saved}");
}''',
            answer='b',
            lint=None,
            good='Both saved values are used after replacement and still print oak. Cloning only words[0] preserves the needed owned text; cloning the whole vector also allocates copies of pine and any other unrelated labels.',
            bad='Inspect what is cloned and what is actually read after replacement.',
            wrap=False,
        ),
        err(
            prompt='Which line mutates the owner while a borrow is still needed?',
            code='''fn main() {
    let mut words =
        vec![String::from("oak")];
    let first = &words[0];
    words.push(String::from("elm"));
    println!("{first}");
}''',
            line=5,
            error_code='E0502',
            good='push needs an exclusive borrow, but first is still used afterward. Save a length or finish using first before push.',
            bad='A push may reallocate the vector. Which line asks to change it?',
        ),
        out(
            prompt='The else branch still uses first. Does that prevent the push on the other branch, and what is printed?',
            code='''let mut words =
    vec![String::from("oak")];
let first = &words[0];
let count = if first.len() > 2 {
    words.push(String::from("elm"));
    words.len()
} else {
    first.len()
};
println!("{count}");''',
            bank=['2', '3', "won't compile"],
            answer=['2'],
            good='It compiles and prints 2. On the path with push, first is last read in the condition. The later read in else is on a path where push does not run.',
            bad='Trace borrow uses on each branch separately.',
            wrap=True,
        ),
    ],
})

# Part 3 / 33
COURSE.append({
    'part': 3,
    'id': 'structure-smells',
    'title': 'Structure smells',
    'summary': 'Review responsibilities, types, dispatch and lock scope against a concrete need.',
    "cards": [
        card(
            h='Trace responsibilities and dependencies',
            p='A god struct gathers unrelated reasons to change. Ask which fields each operation actually needs. Small modules should let callers use one responsibility without constructing unrelated application state. format! builds a String rather than printing it.',
            code='''let row = format!("item {}", 7);
println!("{row}");''',
            note='For a closed vocabulary use an enum; a newtype gives a primitive value a distinct type: `struct Depth(u32)` wraps a u32, accessed as `.0`. Review these choices against the requested contract, not a rule to split everything. `type Label = String` introduces an alternate name for an existing type. `()` is the unit value/type: it carries no data.',
        ),
        card(
            h='Choose when the concrete type is known',
            p='dyn Trait hides a concrete implementation behind a trait interface and dispatches at runtime. Box<dyn Trait> owns such a value on the heap. Generics keep a concrete type chosen at compile time; an enum describes a closed set of alternatives.',
            code='''trait Sound {
    fn sound(&self) -> &str;
}
struct Bell;
impl Sound for Bell {
    fn sound(&self) -> &str {
        "ding"
    }
}
let bell: Box<dyn Sound> =
    Box::new(Bell);
println!("{}", bell.sound());''',
            note='Runtime heterogeneity can justify dyn. Neither dyn nor generics is always the better design.',
        ),
        card(
            h='A lock lasts as long as its guard',
            p='A Mutex guard releases its lock when its scope ends. drop(value) ends ownership immediately, so drop(guard) releases a lock early. Keep a read-modify-write transaction under one guard when atomicity matters.',
            code='''use std::sync::Mutex;
let gate = Mutex::new(false);
let mut guard = gate.lock().unwrap();
*guard = true;
drop(guard);
println!("{}", gate.lock().unwrap());''',
            note='Locking the same Mutex twice on the same thread while its first guard is live may deadlock or panic; std leaves the behavior unspecified. Choose guard scope deliberately; shortening it is not always correct.',
        ),
        card(
            h='Async review: not executed here',
            p='Async Rust needs a runtime outside these std-only exercises. Blocking I/O or thread sleep on an executor thread can stall other tasks. Use runtime async APIs or its blocking-work facility. A guard held across .await can block peers or deadlock; take a snapshot first only if the operation allows stale state.',
            code='''// Review questions for async code:
// Where can this operation suspend?
// Is a lock guard still live there?
// Does the API block its calling thread?''',
            note='These async claims are reading guidance, not compiled async examples or checked scheduling behavior.',
        ),
    ],
    "problems": [
        better(
            prompt='Both purchase flows record one audit entry. Which design also lets a quote screen reuse pricing without creating or mutating audit storage?',
            a='''struct Shop {
    rate: i32,
    audit: Vec<i32>,
}
impl Shop {
    fn estimate(
        &mut self,
        units: i32,
    ) -> i32 {
        let total = self.rate * units;
        self.audit.push(total);
        total
    }
    fn buy(&mut self, units: i32) -> i32 {
        self.estimate(units)
    }
}
fn main() {
    let mut shop = Shop {
        rate: 3,
        audit: vec![],
    };
    println!("{}", shop.buy(2));
    println!("{}", shop.audit.len());
}''',
            b='''fn price(rate: i32, units: i32) -> i32 {
    rate * units
}
struct Shop {
    rate: i32,
    audit: Vec<i32>,
}
impl Shop {
    fn buy(&mut self, units: i32) -> i32 {
        let total = price(self.rate, units);
        self.audit.push(total);
        total
    }
}
fn main() {
    let mut shop = Shop {
        rate: 3,
        audit: vec![],
    };
    println!("{}", shop.buy(2));
    println!("{}", shop.audit.len());
}''',
            answer='b',
            lint=None,
            good='Both preserve purchases and audit history. The plain price function needs no audit store; Shop::buy records the purchase. The combined estimate in the other design records an entry even when reused just to show a quote.',
            bad='Follow what happens if a quote screen calls estimate but never buys.',
            wrap=False,
        ),
        better(
            prompt='Both run the built-in command. Outside crates will add commands with new behavior. Which host API supports those implementations without editing the host?',
            a='''pub trait Command {
    fn run(&self) -> i32;
}
struct Builtin;
impl Command for Builtin {
    fn run(&self) -> i32 {
        7
    }
}
pub fn execute(
    cmd: Box<dyn Command>,
) -> i32 {
    cmd.run()
}
fn main() {
    println!(
        "{}",
        execute(Box::new(Builtin))
    );
}''',
            b='''pub enum Command {
    Builtin,
}
pub fn execute(cmd: Command) -> i32 {
    match cmd {
        Command::Builtin => 7,
    }
}
fn main() {
    println!(
        "{}",
        execute(Command::Builtin)
    );
}''',
            answer='a',
            lint=None,
            good='An extension can implement the public Command trait and pass its own boxed type to execute. An outside crate cannot add a variant to the host enum. The enum is a reasonable closed-world prototype, but this requirement has an open implementation set.',
            bad='Imagine adding a third-party command whose run method performs entirely different work.',
            wrap=False,
        ),
        better(
            prompt='Both print two numbers. Another caller needs to print a text label and a numeric count without converting them to owned strings. Which signature supports that caller?',
            a='''use std::fmt::Display;
fn show<L: Display, R: Display>(
    left: L,
    right: R,
) {
    println!("{left}={right}");
}
fn main() {
    show(3, 4);
}''',
            b='''use std::fmt::Display;
fn show<T: Display>(left: T, right: T) {
    println!("{left}={right}");
}
fn main() {
    show(3, 4);
}''',
            answer='a',
            lint=None,
            good='Separate type parameters let show("items", 4) choose a different concrete type for each argument. Reusing T forces both arguments to have one type, even though both separately implement Display. No heap or type erasure is needed in either current sample.',
            bad='Substitute &str and i32 for the two argument types. Must they be the same T?',
            wrap=False,
        ),
        better(
            prompt='A wire protocol currently has Add and Sub. If it gains Multiply, the dispatcher must fail to compile until that case is handled. Which design gives that reminder while supporting both current operations?',
            a='''trait Op {
    fn run(&self, n: i32) -> i32;
}
struct Add;
struct Sub;
impl Op for Add {
    fn run(&self, n: i32) -> i32 {
        n + 1
    }
}
impl Op for Sub {
    fn run(&self, n: i32) -> i32 {
        n - 1
    }
}
fn apply(op: Box<dyn Op>, n: i32) -> i32 {
    op.run(n)
}
fn main() {
    println!("{}", apply(Box::new(Add), 2));
    println!("{}", apply(Box::new(Sub), 2));
}''',
            b='''enum Op {
    Add,
    Sub,
}
fn apply(op: Op, n: i32) -> i32 {
    match op {
        Op::Add => n + 1,
        Op::Sub => n - 1,
    }
}
fn main() {
    println!("{}", apply(Op::Add, 2));
    println!("{}", apply(Op::Sub, 2));
}''',
            answer='b',
            lint=None,
            good='An enum match must handle every variant, so adding Multiply makes an incomplete apply fail to compile. The trait-based implementation supports both operations too, but adding another implementer does not require updating a central dispatcher.',
            bad='Which representation tells the compiler the full set of operations?',
            wrap=False,
        ),
        better(
            prompt='Slow work must not hold the shared lock. Which releases it first? (std stand-in for work around .await.)',
            a='''use std::sync::Mutex;
fn slow(n: i32) {
    println!("{n}");
}
fn main() {
    let state = Mutex::new(3);
    let snapshot =
        { *state.lock().unwrap() };
    slow(snapshot);
}''',
            b='''use std::sync::Mutex;
fn slow(n: i32) {
    println!("{n}");
}
fn main() {
    let state = Mutex::new(3);
    let guard = state.lock().unwrap();
    slow(*guard);
    drop(guard);
}''',
            answer='a',
            lint=None,
            good='The snapshot version copies the number while holding a temporary guard. That guard is dropped at the end of the let statement, before slow is called. The other version explicitly drops its guard only after slow returns. This snapshot is valid because slow does not require an atomic update.',
            bad='When does each guard get dropped?',
            wrap=False,
        ),
        better(
            prompt='Both sell one available unit in this run. With competing buyers, which version prevents two buyers from both acting on the last unit being available?',
            a='''use std::sync::Mutex;
fn main() {
    let stock = Mutex::new(1);
    let available =
        { *stock.lock().unwrap() > 0 };
    let mut guard = stock.lock().unwrap();
    if available {
        *guard -= 1;
    }
    println!("{}", *guard);
}''',
            b='''use std::sync::Mutex;
fn main() {
    let stock = Mutex::new(1);
    let mut guard = stock.lock().unwrap();
    if *guard > 0 {
        *guard -= 1;
    }
    println!("{}", *guard);
}''',
            answer='b',
            lint=None,
            good='The successful design checks availability while holding the same guard used to decrement. In the other version, a buyer may observe availability, release the temporary guard, and then decrement after another buyer has already sold that unit.',
            bad='Can the truth of available change before the guard used for decrement is acquired?',
            wrap=False,
        ),
        better(
            prompt='Loaded content must exist exactly when state is Ready. Which encodes that relationship?',
            a='''struct Load {
    ready: bool,
    text: Option<String>,
}
fn main() {
    let s = Load {
        ready: true,
        text: Some(String::from("ok")),
    };
    if s.ready {
        println!("{}", s.text.unwrap());
    }
}''',
            b='''enum Load {
    Pending,
    Ready(String),
}
fn main() {
    let s = Load::Ready(String::from("ok"));
    match s {
        Load::Ready(text) => {
            println!("{text}")
        }
        Load::Pending => (),
    }
}''',
            answer='b',
            lint=None,
            good='B cannot represent ready=true with no content. A admits that combination and would panic when printed.',
            bad='Can each type express ready with missing text?',
            wrap=False,
        ),
        better(
            prompt='Both label the counts with domain names. Which API rejects swapping an already typed byte count with an item count at compile time?',
            a='''struct Items(usize);
struct Bytes(usize);
fn show(items: Items, bytes: Bytes) {
    println!("{} {}", items.0, bytes.0);
}
fn main() {
    show(Items(2), Bytes(8));
}''',
            b='''type Items = usize;
type Bytes = usize;
fn show(items: Items, bytes: Bytes) {
    println!("{items} {bytes}");
}
fn main() {
    show(2, 8);
}''',
            answer='a',
            lint=None,
            good='The tuple structs create distinct types. The type aliases are plausible documentation but still denote the same usize type, so a caller can swap them without a compiler error.',
            bad='Trace whether Items and Bytes are new types or just alternate names for usize.',
            wrap=False,
        ),
    ],
})

# Part 3 / 34
COURSE.append({
    'part': 3,
    'id': 'ai-review',
    'title': '"AI wrote this"',
    'summary': 'Read the whole short program, locate its smell, then choose the repair.',
    "cards": [
        card(
            h='Read the whole program before flagging a line',
            p='Trace the input, data lifetime and output first. A clone may be justified; an unwrap may be justified by a checked invariant. The review prompts intentionally do not name the lint. Flag the one line for which Clippy provides evidence, then assess repair attempts.',
            code='''let input = Some(6);
let n = match input {
    Some(n) => n,
    None => 0,
};
println!("{}", n * 2);''',
            note='One lint per program is a checker limit; it does not mean a real review should stop after one finding.',
        ),
        card(
            h='A repair can hide a symptom',
            p='An allow attribute silences a lint for the attached code; it does not change the API or behavior. is_empty() asks whether a collection has no elements. A plausible repair may compile and match the sample while failing the requested contract.',
            code='''#[allow(unused_variables)]
let reserved = 9;
let bytes = "";
println!("{}", bytes.is_empty());''',
            note='After each line-selection question, choose between two changed programs. Use the stated repair requirement; the preceding lint fix alone does not settle the choice.',
        ),
    ],
    "problems": [
        smell(
            prompt='Which line would you flag in review?',
            code='''fn total(values: &Vec<i32>) -> i32 {
    values.iter().sum()
}
fn main() {
    let mut batch = vec![2, 3];
    let saved = batch.clone();
    batch.push(4);
    println!("{}", total(&batch));
    println!("{saved:?}");
}''',
            line=1,
            lint='clippy::ptr_arg',
            fixed='''fn total(values: &[i32]) -> i32 {
    values.iter().sum()
}
fn main() {
    let mut batch = vec![2, 3];
    let saved = batch.clone();
    batch.push(4);
    println!("{}", total(&batch));
    println!("{saved:?}");
}''',
            good='Clippy flags clippy::ptr_arg. Read the repair choices against the next requirement.',
            bad='Trace each line; distinguish a real contract restriction from legitimate ownership or control flow.',
            wrap=False,
        ),
        better(
            prompt='Repair request: sum a borrowed array or vector without copying it. Which changed API meets that requirement?',
            a='''fn total(values: Vec<i32>) -> i32 {
    values.iter().sum()
}
fn main() {
    let mut batch = vec![2, 3];
    let saved = batch.clone();
    batch.push(4);
    println!("{}", total(batch.clone()));
    println!("{saved:?}");
}''',
            b='''fn total(values: &[i32]) -> i32 {
    values.iter().sum()
}
fn main() {
    let mut batch = vec![2, 3];
    let saved = batch.clone();
    batch.push(4);
    println!("{}", total(&batch));
    println!("{saved:?}");
}''',
            answer='b',
            lint=None,
            good='The slice repair accepts a borrowed array or vector. Taking Vec by value and cloning at the call hides the pointer lint by imposing an unnecessary ownership requirement. The separate saved clone is justified: it preserves the old batch before push.',
            bad='Try an array caller, and count allocations required just to sum.',
            wrap=False,
        ),
        smell(
            prompt='Which line would you flag in review?',
            code='''fn main() {
    let mut tasks = vec!["job"];
    let completed = tasks.pop();
    if tasks.len() == 0 {
        println!("idle");
    }
    println!("{completed:?}");
}''',
            line=4,
            lint='clippy::len_zero',
            fixed='''fn main() {
    let mut tasks = vec!["job"];
    let completed = tasks.pop();
    if tasks.is_empty() {
        println!("idle");
    }
    println!("{completed:?}");
}''',
            good='Clippy flags clippy::len_zero. Read the repair choices against the next requirement.',
            bad='Trace each line; distinguish a real contract restriction from legitimate ownership or control flow.',
            wrap=False,
        ),
        better(
            prompt='Repair request: express emptiness directly, without suppressing a warning. Which changed program does that?',
            a='''fn main() {
    let mut tasks = vec!["job"];
    let completed = tasks.pop();
    #[allow(clippy::len_zero)]
    if tasks.len() == 0 {
        println!("idle");
    }
    println!("{completed:?}");
}''',
            b='''fn main() {
    let mut tasks = vec!["job"];
    let completed = tasks.pop();
    if tasks.is_empty() {
        println!("idle");
    }
    println!("{completed:?}");
}''',
            answer='b',
            lint=None,
            good='is_empty states the predicate directly. The allow repair suppresses the same expression instead of addressing it; popping and inspecting completed are valid work, not the flagged line.',
            bad='Both are changed programs and match the sample. Which meets the stated contract beyond that sample?',
            wrap=False,
        ),
        smell(
            prompt='Which line would you flag in review?',
            code='''fn permitted(level: u32) -> bool {
    if level >= 2 {
        true
    } else {
        false
    }
}
fn main() {
    let limits = [3];
    let limit = limits[0];
    println!("{}", permitted(limit));
}''',
            line=2,
            lint='clippy::needless_bool',
            fixed='''fn permitted(level: u32) -> bool {
    level >= 2
}
fn main() {
    let limits = [3];
    let limit = limits[0];
    println!("{}", permitted(limit));
}''',
            good='Clippy flags clippy::needless_bool. Read the repair choices against the next requirement.',
            bad='Trace each line; distinguish a real contract restriction from legitimate ownership or control flow.',
            wrap=False,
        ),
        better(
            prompt='Repair request: remove the redundant branches but preserve permission at the threshold, including level 2. Which repair?',
            a='''fn permitted(level: u32) -> bool {
    level >= 2
}
fn main() {
    let limits = [3];
    let limit = limits[0];
    println!("{}", permitted(limit));
}''',
            b='''fn permitted(level: u32) -> bool {
    level > 2
}
fn main() {
    let limits = [3];
    let limit = limits[0];
    println!("{}", permitted(limit));
}''',
            answer='a',
            lint=None,
            good='The >= repair includes level 2. The > repair also removes branches and passes the sample at 3, but changes boundary behavior. Neither option is the original branching program.',
            bad='Both are changed programs and match the sample. Which meets the stated contract beyond that sample?',
            wrap=False,
        ),
        smell(
            prompt='Which line would you flag in review?',
            code='''fn main() {
    let stages = ["queued", "done"];
    let ready = stages.contains(&"done");
    if ready == true {
        println!("send");
    }
}''',
            line=4,
            lint='clippy::bool_comparison',
            fixed='''fn main() {
    let stages = ["queued", "done"];
    let ready = stages.contains(&"done");
    if ready {
        println!("send");
    }
}''',
            good='Clippy flags clippy::bool_comparison. Read the repair choices against the next requirement.',
            bad='Trace each line; distinguish a real contract restriction from legitimate ownership or control flow.',
            wrap=False,
        ),
        better(
            prompt='Repair request: send if any stage is done, even if later stages are queued. Both repairs work for this sample. Which preserves the rule for reordered stages?',
            a='''fn main() {
    let stages = ["queued", "done"];
    let ready = stages.contains(&"done");
    if ready {
        println!("send");
    }
}''',
            b='''fn main() {
    let stages = ["queued", "done"];
    let ready = stages.contains(&"done");
    if stages[stages.len() - 1] == "done" {
        println!("send");
    }
}''',
            answer='a',
            lint=None,
            good='The membership predicate finds done anywhere. The last-stage repair is a plausible assumption about ordered progress, but loses an earlier done when a later queued stage exists. Empty input also makes its index invalid.',
            bad='Try ["done", "queued"] rather than assuming done always comes last.',
            wrap=False,
        ),
    ],
})

# Part 3 / 35
COURSE.append({
    'part': 3,
    'id': 'steer-ai',
    'title': 'Steering AI',
    'summary': 'Ask for contracts, errors and ownership first; judge the resulting before/after code.',
    "cards": [
        card(
            h='Ask for types before implementation',
            p='Describe what can be represented, not just which sample should print. Ask for type signatures and module boundaries first; review them before requesting the implementation. Here a coordinate always has both components.',
            code='''struct Position {
    x: i32,
    y: i32,
}
let point = Position {
    x: 2,
    y: 5,
};
println!("{} {}", point.x, point.y);''',
            note="A types-first request should name illegal states or confused quantities. Do not accept a type merely because its example compiles. `crate::` starts a path at the current crate root, so one module can call another module's public function.",
        ),
        card(
            h='Specify failure and ownership policies',
            p='Ask which layer handles failure and which values are borrowed, moved or copied. Result<T, E> exposes success and failure separately; a typed error can carry useful context. Rc::clone shares an allocation rather than copying its contents.',
            code='''enum OpenError {
    Missing,
    Denied,
}
let attempt: Result<(), OpenError> =
    Err(OpenError::Denied);
match attempt {
    Ok(()) => println!("opened"),
    Err(OpenError::Missing) => {
        println!("gone")
    }
    Err(OpenError::Denied) => {
        println!("denied")
    }
}''',
            note='Require an explanation for shared mutation or a clone. Borrowing is not the right answer when the requested value must be independent.',
        ),
        card(
            h='Ask for evidence at boundaries',
            p='u8::MAX and u32::MAX are the largest values of those types. checked_add returns Some(sum), or None on integer overflow. Test failure behavior distinctly from valid zero; a fallback can hide the distinction. assert_eq! checks equality and fails the run if values differ.',
            code='''let value = u8::MAX;
let result = value.checked_add(2);
assert_eq!(result, None);''',
            note='Use boundary examples the implementation could get wrong. The following tasks ask for contracts and evidence, not a vague promise of idiomatic code.',
        ),
    ],
    "problems": [
        better(
            prompt="Ask: 'Put the shared range rule in one small module and reuse it from both entry points; changing the rule should require one edit.' Which implementation follows that request?",
            a='''mod rules {
    pub fn valid(n: i32) -> bool {
        n > 0
    }
}
mod cli {
    pub fn accept(n: i32) -> bool {
        crate::rules::valid(n)
    }
}
mod api {
    pub fn accept(n: i32) -> bool {
        crate::rules::valid(n)
    }
}
fn main() {
    println!("{}", cli::accept(2));
    println!("{}", api::accept(2));
}''',
            b='''mod cli {
    pub fn accept(n: i32) -> bool {
        n > 0
    }
}
mod api {
    pub fn accept(n: i32) -> bool {
        n > 0
    }
}
fn main() {
    println!("{}", cli::accept(2));
    println!("{}", api::accept(2));
}''',
            answer='a',
            lint=None,
            good='Both entry points currently accept the same numbers. The rules module owns one definition; the other implementation separates files conceptually but duplicates the policy, so a future boundary change must be made in two places.',
            bad='If the rule changes to allow zero, how many definitions must change?',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Return a typed error that callers can match, not a magic sentinel.' Which response?",
            a='''#[derive(Debug)]
enum ParseError {
    Invalid,
}
fn parse(
    s: &str,
) -> Result<u32, ParseError> {
    match s.parse() {
        Ok(n) => Ok(n),
        Err(_) => Err(ParseError::Invalid),
    }
}
fn main() {
    println!("{}", parse("4").unwrap());
}''',
            b='''fn parse(s: &str) -> u32 {
    s.parse().unwrap_or(0)
}
fn main() {
    println!("{}", parse("4"));
}''',
            answer='a',
            lint=None,
            good='A distinguishes failure from a valid zero. The sample main unwraps known valid input; a real input boundary should match the Result.',
            bad='Can a caller tell invalid input apart from the number zero?',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Test empty input and a nonempty list where every value is negative, to catch a maximum accidentally initialized to zero.' (`.max()` gives the biggest item of an iterator as an Option; None when it is empty.) Which suite exercises both named edge cases?",
            a='''fn largest(values: &[i32]) -> Option<i32> {
    match values.iter().max() {
        Some(n) => Some(*n),
        None => None,
    }
}
fn main() {
    assert_eq!(largest(&[]), None);
    assert_eq!(largest(&[-5, 0]), Some(0));
    println!("checked");
}''',
            b='''fn largest(values: &[i32]) -> Option<i32> {
    match values.iter().max() {
        Some(n) => Some(*n),
        None => None,
    }
}
fn main() {
    assert_eq!(largest(&[]), None);
    assert_eq!(largest(&[-5, -2]), Some(-2));
    println!("checked");
}''',
            answer='b',
            lint=None,
            good='Both suites test empty and nonempty input. Only [-5, -2] is all-negative, so an incorrect zero starting maximum would fail it; the mixed [-5, 0] case would still pass. This is a named edge-case review, not another ownership signature drill.',
            bad='Does the supposed negative test actually exclude zero?',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Separate calculation from printing so I can test it without capturing stdout.' Which response?",
            a='''fn sum(values: &[i32]) {
    println!(
        "{}",
        values.iter().sum::<i32>()
    );
}
fn main() {
    sum(&[2, 3]);
}''',
            b='''fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}
fn main() {
    println!("{}", sum(&[2, 3]));
}''',
            answer='b',
            lint=None,
            good='B returns a value from the pure core; main owns printing. Tests can assert sum(&[2,3]) == 5 directly.',
            bad='Which calculation function exposes its result to a test?',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Return an independent snapshot of shared mutable text, so later edits do not change the saved value.' Which response meets that contract?",
            a='''use std::cell::RefCell;
use std::rc::Rc;
fn snapshot(
    source: &Rc<RefCell<String>>,
) -> Rc<RefCell<String>> {
    Rc::new(RefCell::new(
        source.borrow().clone(),
    ))
}
fn main() {
    let source = Rc::new(RefCell::new(
        String::from("oak"),
    ));
    let saved = snapshot(&source);
    println!("{}", saved.borrow());
}''',
            b='''use std::cell::RefCell;
use std::rc::Rc;
fn snapshot(
    source: &Rc<RefCell<String>>,
) -> Rc<RefCell<String>> {
    Rc::clone(source)
}
fn main() {
    let source = Rc::new(RefCell::new(
        String::from("oak"),
    ));
    let saved = snapshot(&source);
    println!("{}", saved.borrow());
}''',
            answer='a',
            lint=None,
            good='Cloning the inner String creates independent contents. Rc::clone only adds an owner of the same RefCell. Both show oak initially; a later source.borrow_mut().push would change the shared-clone result too.',
            bad='Which clone duplicates text, and which only shares its owner?',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Expose only the double operation from this module; callers must not be able to set the multiplier.' Which response keeps that public boundary?",
            a='''mod math {
    pub fn scale(
        n: i32,
        factor: i32,
    ) -> i32 {
        n * factor
    }
    pub fn double(n: i32) -> i32 {
        scale(n, 2)
    }
}
fn main() {
    println!("{}", math::double(3));
}''',
            b='''mod math {
    fn scale(n: i32, factor: i32) -> i32 {
        n * factor
    }
    pub fn double(n: i32) -> i32 {
        scale(n, 2)
    }
}
fn main() {
    println!("{}", math::double(3));
}''',
            answer='b',
            lint=None,
            good='Keeping scale private exposes the requested operation without exposing an arbitrary factor. Both versions compute double identically; the distinction is what external callers can request.',
            bad='Inspect pub on each function, not just the main call.',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Do not overflow at the boundary; return None when addition is impossible.' Which response?",
            a='''fn next(n: u32) -> Option<u32> {
    Some(n + 1)
}
fn main() {
    println!("{:?}", next(4));
}''',
            b='''fn next(n: u32) -> Option<u32> {
    n.checked_add(1)
}
fn main() {
    println!("{:?}", next(4));
}''',
            answer='b',
            lint=None,
            good='B returns None at u32::MAX. A wraps or panics depending on build settings. Ask for a boundary test; the sample 4 cannot distinguish them.',
            bad='Which operation defines overflow explicitly?',
            wrap=False,
        ),
        better(
            prompt="Ask: 'Write tests that distinguish invalid input from valid zero, even if the parser regresses to returning Ok(0) on errors.' Which test suite catches that regression?",
            a='''fn parse(
    s: &str,
) -> Result<u32, &'static str> {
    match s.parse() {
        Ok(n) => Ok(n),
        Err(_) => Err("invalid"),
    }
}
fn main() {
    assert_eq!(parse("0"), Ok(0));
    assert_eq!(
        parse("oops"),
        Err("invalid")
    );
    println!("checked");
}''',
            b='''fn parse(
    s: &str,
) -> Result<u32, &'static str> {
    match s.parse() {
        Ok(n) => Ok(n),
        Err(_) => Err("invalid"),
    }
}
fn main() {
    assert_eq!(parse("0"), Ok(0));
    assert_eq!(
        parse("oops").unwrap_or(0),
        0
    );
    println!("checked");
}''',
            answer='a',
            lint=None,
            good='The exact Err assertion fails if the parser silently returns Ok(0). The fallback assertion exercises invalid input but collapses both outcomes to zero, so that regression passes. Both suites also test valid zero.',
            bad='Would replacing the error branch with Ok(0) make either test fail?',
            wrap=False,
        ),
    ],
})

# Tokens a lesson must not use before the lesson that teaches them (1-based lesson number).
GATES = [
    (r"\bi32\b|\bf64\b|\bbool\b|\btrue\b|\bfalse\b|\bas\b", 2),
    (r"\breturn\b|->", 3),
    (r"\bif\b|\belse\b|\bloop\b|\bbreak\b|\bwhile\b|\bfor\b|\.\.|\+=|-=|==|&&|\|\|", 4),
    (r"\bString\b|\bstr\b|::|push_str|\.len\(\)|(?<!&)&(?!&)", 5),
    (r"\.clone\(\)", 6),
    (r"&mut\b|\busize\b", 7),
    (r"\bstruct\b|\bimpl\b|\bself\b|\bSelf\b", 8),
    (r"\bVec\b|vec!|\.push\(|\[", 9),
    (r"\benum\b|\bmatch\b|=>|\b_\b", 10),
    (r"\bOption\b|\bSome\b|\bNone\b|\bResult\b|\bOk\b|\bErr\b|\?|\.get\(|unwrap", 11),
    (r"\btrait\b|\|[a-z][a-z, ]*\||\.iter\(\)|\.map\(|\.sum\(|\.max\(", 12),
    (r"\bfn\s+\w+<|\bimpl<|\bstruct\s+\w+<|'[a-z]\b(?!')|PartialOrd|\bDisplay\b|\bClone\b|\bCopy\b", 13),
    (r"\bmod\b|\buse\b|#\[derive|\bpub\b|\{:\?\}|PartialEq|\bEq\b|\bDebug\b|\bu8\b", 14),
    (r"HashMap|\.insert\(|\.entry\(|or_insert", 15),
    # Basic closures/map/sum/max remain in lesson 12; these are deeper tools.
    (r"\bmove\s*\||\bFn(?:Mut|Once)?\b|\bimpl\s+Fn(?:Mut|Once)?\b|Box\s*<\s*dyn\s+Fn", 17),
    (r"\b(?:Box|Rc|Weak)\b", 18),
    (r"\b(?:Arc|Mutex|RwLock|thread|Send|Sync)\b", 19),
    (r"\b(?:From|Into|ParseIntError)\b|impl\s+(?:\w+::)*Display\b|std::error::Error|\.into\s*\(|\b(?:write|writeln)\s*!", 20),
    (r"(?:->|:|&)\s*(?:&\s*)?impl\s+(?!Fn(?:Mut|Once)?\b)|\bIterator\b|\.(?:filter|filter_map|collect|take|copied|enumerate|flat_map|rev|zip|fold|skip)\s*\(", 21),
    (r"#\s*\[\s*(?:test|cfg\s*\(\s*test)|\bassert(?:_eq|_ne)?!", 22),
]
