# Rune — Windows Build Guide

Manual release workflow for a single maintainer.  
No CI/CD required. Run every step from a Windows machine.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| pip | latest | bundled with Python |
| PyInstaller | 6.x | `pip install pyinstaller` |
| git | any | [git-scm.com](https://git-scm.com/) |
| gh CLI | any | [cli.github.com](https://cli.github.com/) (optional, for upload step) |

Verify before building:

```
python --version
pyinstaller --version
```

---

## Step 1 — Run the test suite

Tests must pass before building. Run from the `rune-lang/` directory:

```
cd rune-lang
python -m unittest rune.tests.test_interpreter -v
```

Expected: `Ran 42 tests ... OK`

**Do not build if any test fails.**

---

## Step 2 — Build the executable

Run from the `rune-lang/rune/` directory:

```
cd rune-lang\rune
pyinstaller packaging\rune.spec --clean
```

The `--clean` flag removes cached artifacts from any previous build.

Output:

```
rune\dist\rune.exe    ← standalone executable
rune\build\           ← intermediate files (can be deleted)
```

Build time: 15–60 seconds depending on machine.

---

## Step 3 — Verify the executable

Run these checks before packaging:

```
dist\rune.exe --version
dist\rune.exe --help
dist\rune.exe run examples\hello_world.rune
dist\rune.exe tokenize examples\hello_world.rune
dist\rune.exe ast examples\hello_world.rune
dist\rune.exe repl
```

Expected output for `--version`: `Rune 0.2.0`  
Expected output for `run hello_world.rune`: `Hello, World!`  
For `repl`: interactive prompt should appear; type `exit` to quit.

---

## Step 4 — Assemble the release artifact

Run from the `rune-lang\rune\` directory.  
Replace `0.2.0` with the actual release version throughout.

```bat
set VERSION=0.2.0
set ARTIFACT=rune-v%VERSION%-windows-x64

mkdir release\%ARTIFACT%
copy dist\rune.exe      release\%ARTIFACT%\
copy LICENSE            release\%ARTIFACT%\
copy packaging\README.txt  release\%ARTIFACT%\
xcopy examples          release\%ARTIFACT%\examples\ /E /I
```

Verify the structure:

```
release\rune-v0.2.0-windows-x64\
├── rune.exe
├── LICENSE
├── README.txt
└── examples\
    ├── hello_world.rune
    ├── variables.rune
    ├── conditions.rune
    ├── functions.rune
    ├── loops.rune
    └── closures.rune
```

---

## Step 5 — Create the ZIP archive

```bat
cd release
powershell Compress-Archive -Path %ARTIFACT% -DestinationPath %ARTIFACT%.zip
```

Output: `release\rune-v0.2.0-windows-x64.zip`

---

## Step 6 — Tag the release in git

```
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

---

## Step 7 — Create the GitHub release

Option A — GitHub CLI (recommended):

```
gh release create v0.2.0 release\rune-v0.2.0-windows-x64.zip ^
  --title "Rune v0.2.0" ^
  --notes "See docs/changelog.md for full release notes."
```

Option B — GitHub web UI:

1. Go to the repository → Releases → Draft a new release
2. Choose tag `v0.2.0`
3. Upload `rune-v0.2.0-windows-x64.zip`
4. Publish the release

---

## Updating the version for a new release

Two files must be kept in sync manually:

| File | Line |
|------|------|
| `pyproject.toml` | `version = "0.x.0"` |
| `cli/main.py` | `VERSION = "0.x.0"` |

Update both before building. A future improvement is to consolidate into
`rune/version.py` (see `docs/roadmap.md`).

---

## Cleaning up

```bat
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q release
```

Keep `packaging/` — the spec file and this guide live there.
