"""The course, as written. `build.py` checks every problem with rustc and writes `course.json`.

Text fields take `backticks` for inline code. Code is a triple-quoted string.
Problem types:
  fill   - `__` marks each gap; `answer` fills them in order; wrong bank options must not work.
  error  - a whole program; `line` (1-based) is the line the compiler rejects; `code` is its error code.
  output - `answer` is what the program prints, one entry per line; ["won't compile"] if it doesn't.
  order  - `pool` lines in the right order; the build finds every other order that also works.
`wrap=True` puts the code inside `fn main() { }` when it's compiled (the learner sees it unwrapped).
"""

WONT = "won't compile"


def card(h, p, code, note=None):
    return {"h": h, "p": p, "code": code, "note": note}


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
    "id": "variables", "title": "Variables",
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
    "id": "types", "title": "Numbers and types",
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
    "id": "functions", "title": "Functions",
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
    "id": "control", "title": "Decisions and loops",
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
    "id": "text", "title": "Text",
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
    "id": "ownership", "title": "Ownership",
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
    "id": "borrowing", "title": "Borrowing",
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
    "id": "structs", "title": "Structs and methods",
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
    "id": "lists", "title": "Lists",
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
    "id": "enums", "title": "Enums and match",
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
    "id": "errors", "title": "Missing values and errors",
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
    "id": "traits", "title": "Traits and iterators",
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
    "id": "generics", "title": "Generics and lifetimes",
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
    "id": "modules", "title": "Modules, use and derive",
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
    "id": "hashmaps", "title": "Maps",
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
]
