NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Coding Standards

## Code Style

The current codebase can be used as a guide for formatting conventions.
Additional guidelines are provided below.

### Universal formatting rules

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.



The following applies to **all** source files (Rust, Python, Cython, shell, etc.):

- Use **spaces only**, never hard tab characters.
- Lines should generally stay below **100 characters**; wrap thoughtfully when necessary.
- Prefer American English spelling (`color`, `serialize`, `behavior`).

### Shell script portability

Shell scripts in this repository use **bash** (not POSIX sh) and must be portable across **Linux** and **macOS**. User-facing scripts (e.g., `scripts/cli/install.sh`) must also work on **Windows** via Git Bash or WSL.

**Shebang**: Always use `#!/usr/bin/env bash` for portability.

**Common pitfalls**: GNU and BSD utilities differ between Linux and macOS:

| Command              | Linux (GNU)       | macOS (BSD)       | Portable solution                        |
|----------------------|-------------------|-------------------|------------------------------------------|
| `sed -i`             | `sed -i 's/…'`    | `sed -i '' 's/…'` | Use backup extension: `sed -i.bak 's/…'` |
| `stat` (file size)   | `stat -c%s file`  | `stat -f%z file`  | Detect with `stat --version`             |
| `sha256sum`          | `sha256sum file`  | N/A               | Use `shasum -a 256` or detect            |
| `readlink -f`        | Works             | N/A               | Avoid, or use `realpath`                 |
| `grep -P` (PCRE)     | Works             | N/A               | Use `-E` (extended regex) instead        |
| `date` (nanoseconds) | `date +%N`        | N/A               | Use `$RANDOM` for cache-busting          |

**Bash version**: macOS ships with bash 3.2; avoid bash 4+ features in user-facing scripts:

| Feature                           | Bash version | Alternative                      |
|-----------------------------------|--------------|----------------------------------|
| Associative arrays (`declare -A`) | 4.0+         | Use files or simple arrays       |
| `readarray` / `mapfile`           | 4.0+         | Use `while read` loops           |
| `${var,,}` / `${var^^}` (case)    | 4.0+         | Use `tr '[:upper:]' '[:lower:]'` |

**CI scripts** (`scripts/ci/*`) run on Linux runners, so bash 4+ and GNU tools are acceptable there.

### Comment conventions

1. Generally leave **one blank line above** every comment block or docstring so it is visually separated from code.
2. Use *sentence case* – capitalize the first letter, keep the rest lowercase unless proper nouns or acronyms.
3. Do not use double spaces after periods.
4. **Single-line comments** *must not* end with a period *unless* the line ends with a URL or inline Markdown link – in those cases leave the punctuation exactly as the link requires.
5. **Multi-line comments** should separate sentences with commas (not period-per-line). The final line *should* end with a period.
6. Keep comments concise; favor clarity and only explain the non-obvious – *less is more*.
7. Avoid emoji symbols in text.

### Doc comment mood

**Rust** doc comments should be written in the **indicative mood** – e.g. *"Returns a cached client."*

This convention aligns with the prevailing style of the Rust ecosystem and makes generated
documentation feel natural to end-users.

### Terminology and phrasing

1. **Error messages**: Avoid using ", got" in error messages. Use more descriptive alternatives like ", was", ", received", or ", found" depending on context.
   - ❌ `"Expected string, got {type(value)}"`
   - ✅ `"Expected string, was {type(value)}"`

2. **Spelling**: Use "hardcoded" (single word) rather than "hard-coded" or "hard coded" – this is the more modern and accepted spelling.

3. **Error variable naming**: Use single-letter `e` for caught errors/exceptions:
   - Rust: `Err(e)` not `Err(err)` or `Err(error)`, and `|e|` not `|err|` in closures
   - Python: `except SomeError as e:` not `as err:` or `as error:`

### Naming conventions

1. **Internal fields**: Abbreviations are acceptable for private/internal fields (e.g., `_price_prec`, `_size_prec`) to keep hot-path code concise.

2. **User-facing API**: Use full, descriptive names for public properties, function parameters, return types, and metric names/labels (e.g., `price_precision`, `size_precision`). This prevents abbreviated terminology from leaking into dashboards or alerts.

3. **Error messages and logs**: Use full words for clarity (e.g., "price precision" not "price prec"). The user should never see abbreviated terminology.

### Formatting

1. For longer lines of code, and when passing more than a couple of arguments, you should take a new line which aligns at the next logical indent (rather than attempting a hanging 'vanity' alignment off an opening parenthesis). This practice conserves space to the right, keeps important code more central in view, and survives function/method name changes.

2. The closing parenthesis should be located on a new line, aligned at the logical indent.

3. Multiple hanging parameters or arguments should end with a trailing comma:

```python
long_method_with_many_params(
    some_arg1,
    some_arg2,
    some_arg3,  # <-- trailing comma
)
```

## Commit messages

Commit messages use a capitalized, imperative subject naming the affected surface, optionally
followed by a body explaining the change.

### Subject line

- Open with a capitalized imperative verb, so the subject describes what the commit does when applied.
  `Add`, `Fix`, `Improve`, `Refine`, `Update`, `Remove`, `Refactor`, and `Standardize` cover most of the history.
- Name the affected surface (crate, adapter, subsystem, or type) so the log stays scannable.
- Keep the subject at 10 characters or more so it can name the affected surface clearly.
- Aim for 60 characters or fewer for clear GitHub rendering and concise text. The commit-message
  hook warns without failing when the subject exceeds this target. The project plans to enforce
  this limit in the future.
- Do not end the subject with a period.
- Do not put an issue or pull request number in the subject. GitHub appends the pull request number
  on squash merge, and any other reference belongs in the body. The commit-message hook rejects a
  subject containing `#<number>` in any position.

```text
Add Decimal constructors to Instrument trait
Fix non-atomic order event application
Refine cross-platform wheel validation
Remove stale security audit exceptions
```

Avoid these shapes:

```text
feat(bybit): add due_post_only flag        # Conventional Commits type and scope
fix: bug                                   # lowercase, unspecific, too short
Fixed the Bybit post-only rejection flag.  # past tense, trailing period
Update stuff                               # says nothing about the surface
Fix the post-only flag (#4544)             # pull request number added by hand
Fix PR #4544 review feedback               # issue or pull request number in the subject
```

### Conventional Commits

Do NOT use [Conventional Commits](https://www.conventionalcommits.org/) syntax for commit messages or pull
request titles. Many editors and AI assistants emit that format by default, but no commit in this
repository's history uses it, and the type and scope ceremony duplicates what the subject already carries.
Pull request titles matter here too, because a squash merge turns the PR title into the commit subject.

### Body

The body is optional, but anything beyond a trivial change should say why the change was made rather than
restate the diff.

- Separate the body from the subject with a blank line.
- Keep body lines to 79 characters or fewer to align with PEP 8 and traditional Git tooling.
- Use prose paragraphs or bullet points, whichever suits the change. Bullets may keep the same imperative
  voice as the subject, and do not need terminating periods.
- Include informative hyperlinks where they help a future reader.

### Issue references

- Reference issues from the body, typically on a final line: `Resolves #4534` when the commit closes the
  issue, or `Related to #4547` when it is partial work.
- GitHub appends the pull request number to the subject on squash merge, producing subjects such as
  `Fix TWAP child-order sizing and interval validation (#4544)`. Do not add that suffix by hand, and
  do not reference a pull request or issue anywhere else in the subject either.
- Aim to keep the pull request title short enough for the appended suffix to leave the squash-merged
  subject at 60 characters or fewer.

### Automated gate

Commit message rules are enforced by an in-repo checker. The `check-commit-message`
hook registered in `.pre-commit-config.yaml` (stages: `commit-msg`) runs
`python3 -B scripts/ci/check_commit_message.py`, which validates the pending commit subject, body,
and AI attribution. The same script also runs in CI over the pull request commit range with
`--ci-range`.
