# Core Values (Hackathon-Adapted)

These principles are calibrated for a 6-hour sprint with 3 experienced developers. They prioritize shipping over polish.

## 1. Parsimony (Amplified)

Absolute minimum viable everything. Every line of code, every abstraction, every file must earn its existence. If you're debating whether to add something, don't.

- One way to do things, not two
- No "just in case" code
- No config systems beyond env vars and a dict
- Three similar functions > one clever abstraction

## 2. Pragmatic Readability

Clean enough to debug under pressure. Not clean enough to publish in a textbook.

- Type hints on function signatures — skip on obvious locals
- Descriptive names for functions and variables
- Skip docstrings on self-evident functions
- Comments only for "why", never for "what"
- If a teammate can't understand your code in 30 seconds, it's too clever

## 3. Front-Load Specs, Lightweight During Sprint

ADRs and interface specs are prepared pre-hackathon. They provide the context. During the 6-hour sprint:

- Document decisions in commit messages
- Complex logic gets a one-line comment
- Don't stop coding to write docs
- CLAUDE.md is the living reference — update it if the plan changes

## 4. Fail Fast, Fix Fast

Don't defensive-program. Let errors surface loudly.

- No silent `except: pass`
- No returning `None` when you should raise
- No retry loops on first implementation — add them only when you hit a real flaky failure
- Crash early, read the traceback, fix the root cause
- A loud error is better than a silent wrong answer

## 5. Coordinate, Don't Block

Never wait on a teammate. The 6 hours are non-renewable.

- Need a module that doesn't exist? Stub the interface and keep going
- Hit a merge conflict? Shout, resolve, move on
- Disagree on an approach? Pick one, note the other, revisit if time permits
- Checkpoints are for syncing, not for getting permission

## 6. Ship the Demo

Everything exists to serve the demo. If a feature isn't in the demo flow, it doesn't exist.

- The 3-beat demo (baseline → first encounter → after learning) is the product
- The benchmark curve is the evidence
- If it works in the demo, it works
- Polish the demo path, not the edge cases
