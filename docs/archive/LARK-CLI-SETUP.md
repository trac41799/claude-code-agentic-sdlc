# lark-cli Setup Guide — Full Access (Windows, v1.0.65)

A step-by-step guide to give **lark-cli** (Feishu/Lark CLI) complete access across every domain
(docs, drive, sheets, base, calendar, im, task, vc, mail, minutes, whiteboard, wiki, okr,
approval, event, contact, …) on this machine.

All commands below are verified against the locally installed CLI (`lark-cli ... --help`).
Run everything in **PowerShell**.

## Prerequisites

| # | Requirement | Where / how |
|---|-------------|-------------|
| 1 | Feishu/Lark developer account | A Feishu (China) or Lark (International) account that can create a self-built (enterprise) app |
| 2 | A developer app with **App ID** + **App Secret** | Feishu Developer Console (see Step 1) |
| 3 | **Bot capability enabled** (needed for `im`/message domains) | Console → app → *Add capability* → *Bot* |
| 4 | Scopes enabled + **app version published** | Console → *Permissions* and *Version Management & Release* (see Step 1 notes) |
| 5 | lark-cli installed | Confirmed at `C:\Users\mrtra\AppData\Roaming\npm\lark-cli` (package `@larksuite/cli`), v1.0.65 |
| 6 | Hermes home | `HERMES_HOME = C:\Users\mrtra\AppData\Local\hermes` (auto-detected) |
| 7 | Web access to the auth URL during Step 4 | Any browser |

> Current state (verified): `lark-cli auth status` → `config/not_configured`,
> `"hermes context detected but lark-cli is not bound to it"`.
> The Hermes `.env` currently has **no** `FEISHU_APP_ID` / `FEISHU_APP_SECRET` lines.

---

## Step 0 — Sanity-check the install

```powershell
lark-cli --help          # should print the command tree (domains incl. all)
lark-cli doctor          # health check: cli_version, update, config_file
```

Expected: `cli_version: 1.0.65` (a newer 1.0.91 is available via `lark-cli update` — do this later if you want),
`config_file: fail` until you complete Step 3.

---

## Step 1 — Create / get a Feishu developer app

Pick the console for your region:

- **International (Lark):** <https://open.larkoffice.com/app>
- **China (Feishu):** <https://open.feishu.cn/app> (开发者后台)

1. **Create an enterprise self-built app**
   - Click **Create App** / **创建企业自建应用** (enterprise internal app), give it a name (e.g. `lark-cli`), select a scope (usually default), create.
2. **Enable the Bot capability** (required for `im`, and message-related features)
   - App → *Add capability* → **Bot / 机器人** → add. (If you don't need IM, this is optional but harmless.)
3. **Get App ID + App Secret**
   - Open the app → **Credentials & Basic Info / 凭证与基础信息**.
   - Copy `App ID` (format `cli_xxxxxxxx`) and `App Secret`.
   - **Treat the App Secret like a password — never paste it into chat or commits.**
4. **Enable scopes** (optional but recommended for "everything")
   - App → **Permissions / 权限管理** → add the API scopes you want (or let the CLI request them during authorization — see Step 4 note).
5. **Publish a version** (required for the bot and any scope changes to take effect)
   - App → **Version Management & Release / 版本管理与发布** → *Create Version / 创建版本* → set availability (e.g. *Available to all members / 全员可用*) → **Release / 发布**.
   - For a personal/self-built app you usually just release it to your org; no review is needed for internal apps.

> **Note on scope requirements:** `lark-cli auth login --domain all` requests a large set of scopes at
> authorization time. The granting page only offers scopes the app has been released with. If some scopes
> were not enabled in the console, login may succeed partially (or ask for them on a later run — see Step 4
> "missed scopes"). If a domain command later fails with `permission_violations`, re-enable the listed
> scopes in the console (use the `console_url` from the error) or run an incremental `auth login --scope`.

---

## Step 2 — Put credentials into the Hermes `.env`

**File to edit:** `C:\Users\mrtra\AppData\Local\hermes\.env`
(it currently has no Feishu lines — the CLI reads `FEISHU_APP_ID` / `FEISHU_APP_SECRET` from here).

**Open it safely** (notepad is fine; no special encoding needed):

```powershell
notepad "C:\Users\mrtra\AppData\Local\hermes\.env"
```

**Add these two lines** at the end of the file (replace the values):

```dotenv
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Optional: if you're on Lark International rather than Feishu, also set the domain brand
(`FEISHU_DOMAIN` is read by the CLI) — otherwise omit it:

```dotenv
FEISHU_DOMAIN=lark
```

**Save and close.** Then verify the file was picked up (the `.env` is read by lark-cli at bind time):

```powershell
Select-String -Path "C:\Users\mrtra\AppData\Local\hermes\.env" -Pattern "FEISHU_APP" -SimpleMatch
```

> Security: never commit this file or paste its secrets anywhere. If you don't want a plaintext secret in a
> `.env`, you can instead create a separate app and run `lark-cli config init --app-id <id>` interactively —
> but inside a Hermes context the supported path is **bind** (Step 3).

---

## Step 3 — Bind lark-cli to the Hermes app

```powershell
lark-cli config bind --source hermes --identity user-default
```

- `--source hermes` is usually auto-detected from `HERMES_HOME`; pass it explicitly for clarity.
- `--identity user-default` is **required** for personal-resource access (your calendar, drive, docs,
  mail, whiteboard, …). Default is `bot-only` (safer but cannot see your personal resources).
- If the CLI warns about a risky identity transition (bot-only → user-default), add `--force` **only**
  after you've confirmed you really want user identity:
  ```powershell
  lark-cli config bind --source hermes --identity user-default --force
  ```
- If it fails with "missing FEISHU_APP_ID" or similar, go back to Step 2 — the `.env` wasn't populated.

**What to expect:** a success JSON. If this is your first login, the CLI may immediately ask you to
authorize (jump to Step 4).

**Verify the bind (still not authorized yet, but config is now present):**

```powershell
lark-cli config show
lark-cli auth status --json --verify
```

You should now see `config/ok` (auth itself still needs Step 4).

---

## Step 4 — Authorize FULL access (`--domain all`)

Use the **split flow** so nothing blocks waiting on the browser. Do it in two parts.

### 4a. Start the authorization (returns URL + device code)

```powershell
lark-cli auth login --domain all --no-wait --json
```

- `--domain all` requests every domain (approval, apps, attendance, base, calendar, contact, docs,
  drive, event, im, mail, markdown, mindnotes, minutes, note, okr, sheets, slides, task, vc, wiki, all).
- Output JSON contains `verification_url` and `device_code`. **Keep `device_code` — you'll need it below.**
- Don't let the terminal/agent lose the code; if it does, just rerun this command (each run mints a fresh code).

**Open the URL in your browser** (or scan a QR — PNG output requires a relative path inside the current
directory):

```powershell
# option A: just open it
Start-Process "<paste verification_url here>"

# option B: render a PNG QR code in the current folder, then open it
lark-cli auth qrcode "<paste verification_url here>" --output qr.png
Start-Process ".\qr.png"

# option C: ASCII QR straight to the terminal (no file)
lark-cli auth qrcode "<paste verification_url here>" --ascii
```

In the browser: sign in as yourself, review the scope list, and click **Authorize / 同意授权**.

> Treat `verification_url` as an opaque string — don't modify/re-encode it.

### 4b. Complete the authorization (after you've authorized in the browser)

```powershell
lark-cli auth login --device-code <device_code>
```

This polls and finishes the login. A success message/JSON confirms you're authorized.

**Missed scopes?** `auth login` is **incremental/accumulative** — rerun with the missing scope(s) or domain
(no need to repeat `--domain all`):

```powershell
lark-cli auth login --scope "drive:file:download" --no-wait --json
lark-cli auth login --domain im --domain task --no-wait --json
```

---

## Step 5 — Verify everything end-to-end (safe, read-only)

```powershell
# 1. Token + identity status (network check)
lark-cli auth status --json --verify

# 2. Effective identity
lark-cli whoami

# 3. Scopes actually granted to the app/user
lark-cli auth scopes --format pretty

# 4. Check one specific scope
lark-cli auth check --scope "calendar:calendar:readonly"

# 5. Real read calls
lark-cli calendar +agenda                              # today's calendar (user identity)
lark-cli drive files list                              # your Drive root listing
lark-cli docs +fetch --doc "<any doc URL you own>"     # fetch a doc's content

# 6. Whiteboard CLI smoke test (separate toolchain, verifies the board pipeline)
npx -y @larksuite/whiteboard-cli@^0.2.12 -v
```

If any command prints `permission_violations` with a `console_url`, see the troubleshooting table.

---

## Step 6 — Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `config/not_configured` — "hermes context detected but lark-cli is not bound to it" | No bind done yet | Complete Step 3 (`config bind`) |
| `config bind` fails / "missing FEISHU_APP_ID" | `.env` has no (or empty) `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | Add both lines (Step 2), re-check with `Select-String`, re-run bind |
| Bind warns about identity transition | Moving bot-only → user-default in flag mode | Only add `--force` if you confirmed user identity is what you want |
| Auth returns `permission_violations` + `console_url` | Scope not enabled/released in the developer console, or not yet granted to you | Open `console_url`, enable the listed scopes, publish a new app version, then run incremental `lark-cli auth login --scope "<scope>"` (or `--domain <domain>`) |
| Authorization page doesn't list some scopes | App version not published with those scopes | Console → Version Management → create+release a new version, retry login |
| Command exits with code `10`, JSON `confirmation_required` | High-risk-write gate (`Risk: high-risk-write` needs explicit consent) | Show the action to the user; only after they agree, re-run with `--yes`. To preview first, use `--dry-run` |
| `auth status --verify` shows token expired / `tokenStatus` bad | Token expired or revoked (server-side) | Re-run `lark-cli auth login --domain all` (or the affected domain) — login accumulates |
| Bot identity can't see your personal resources | `--as bot` has no user access | Use `--as user` (or set `config default-as user` after confirming), and ensure identity is `user-default` |
| JSON output polluted by `_notice.update` / skills notice | Update notifier appended to output | Prefix commands with the no-notifier vars (Step 7) |
| `unsafe file path` error | `--output`/`--file` only accept relative paths inside cwd | Pass a relative path, or pipe data via stdin |
| Binding to wrong app | Old/another app config is current | `lark-cli config show` to inspect; only re-bind when the underlying app actually changes. To only change identity policy on the same app use `lark-cli config strict-mode` (no re-bind) |
| Want to start over / remove everything | — | `lark-cli config remove` (clears tokens + config). `lark-cli auth logout --json` clears only the local login |

---

## Step 7 — Windows-specific gotchas

**Suppress update/skills notifiers** (keeps JSON clean for scripts). PowerShell syntax:

```powershell
$env:LARKSUITE_CLI_NO_UPDATE_NOTIFIER="1"
$env:LARKSUITE_CLI_NO_SKILLS_NOTIFIER="1"
lark-cli auth status --json --verify
```

(The env-var names are verified in the installed binary. `LARKSUITE_CLI_APP_ID` /
`LARKSUITE_CLI_APP_SECRET` also exist if you ever need to override credentials via env instead of `.env`.)

**Quoting paths.** The shim is `C:\Users\mrtra\AppData\Roaming\npm\lark-cli.ps1` (PowerShell) with a
`.cmd` twin; since it's on PATH you can just type `lark-cli`. If you ever reference the full path, quote it
and use the call operator:

```powershell
& "C:\Users\mrtra\AppData\Roaming\npm\lark-cli.cmd" auth status
```

**Long-running / polling commands.**
- `lark-cli auth login` **without** `--no-wait` blocks until you authorize — that's normal.
- `--device-code` also polls until completion.
- `npx` smoke tests and `lark-cli update` can take a while on first run (they download). Don't kill them.
- If your terminal window is shared with an agent, prefer `--no-wait --json` for auth so you can deliver
  the URL/QR to yourself, authorize, then finish with `--device-code`.

**Machine/job note:** `device_code` and `verification_url` are single-use and expire. If a flow times out,
just re-run `auth login --no-wait --json` to mint a fresh pair.

**Updating later:** `lark-cli update` updates both the CLI and its embedded AI skills
(don't use a bare npm update).
