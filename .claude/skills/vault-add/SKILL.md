---
name: vault-add
description: Add or update a credential in the local tanker vault at ~/.claude/vault/credentials.json. Use when a provisioner subagent reports a missing key, or when the user wants to register a new service token. Reads the schema, prompts for the value securely, writes with 0600 perms, never logs the value.
triggers:
  - /vault-add
args: "[service name — github | vercel | railway | supabase | cloudflare | anthropic | openai | stripe | resend | sentry | plausible | custom]"
---

# Vault Add

You are registering a credential in the local vault. Your job is to take a token from the user and write it to `~/.claude/vault/credentials.json` without ever echoing the value back, logging it, or exposing it in a tool argument that could leak.

---

## Phase 0 — Verify vault exists

```bash
test -f ~/.claude/vault/credentials.json || { mkdir -p ~/.claude/vault && chmod 700 ~/.claude/vault && echo '{}' > ~/.claude/vault/credentials.json && chmod 600 ~/.claude/vault/credentials.json; }
ls -la ~/.claude/vault/credentials.json
```

Confirm permissions are `0600`. If not, fix:
```bash
chmod 600 ~/.claude/vault/credentials.json
```

---

## Phase 1 — Identify what to add

If the user gave a service name in args, use it. Otherwise, ask:

> Which service? (github, vercel, railway, supabase, cloudflare, anthropic, openai, stripe, resend, sentry, plausible, or custom)

For each service, list the keys you'll need:

| Service | Required keys | Where to get |
|---|---|---|
| github | `pat`, `user` | github.com/settings/tokens (scopes: `repo`, `workflow`, `delete_repo`) |
| vercel | `token`, `team_id` (optional) | vercel.com/account/tokens |
| railway | `token` | railway.app/account/tokens |
| supabase | `access_token`, `org_id` | supabase.com/dashboard/account/tokens |
| cloudflare | `api_token`, `account_id` | dash.cloudflare.com/profile/api-tokens |
| anthropic | `api_key` | console.anthropic.com/settings/keys |
| openai | `api_key` | platform.openai.com/api-keys |
| stripe | `test_secret`, `test_publishable` | dashboard.stripe.com/test/apikeys |
| resend | `api_key` | resend.com/api-keys |
| sentry | `auth_token`, `org` | sentry.io/settings/account/api/auth-tokens |
| plausible | `api_key` | plausible.io/settings#api-keys |

Print the table row for the chosen service so the user knows what to provide and where to get it.

---

## Phase 2 — Get the value WITHOUT echoing it

**Critical:** never paste the token into the conversation. Tell the user to open the file directly:

> Open `~/.claude/vault/credentials.json` in your editor (`code ~/.claude/vault/credentials.json` or `vim`) and add the keys yourself, then come back. I'll verify but never read the value.

Wait for confirmation.

**Alternative — guided write via shell:** if the user prefers, run this with a `read -s` (silent input) prompt — the value never enters the chat transcript:

```bash
read -s -p "Paste [service] [key] (input hidden): " VAL && echo
jq --arg val "$VAL" '.[\"<service>\"][\"<key>\"] = $val' ~/.claude/vault/credentials.json > /tmp/vault.json && mv /tmp/vault.json ~/.claude/vault/credentials.json && chmod 600 ~/.claude/vault/credentials.json && unset VAL
```

(Replace `<service>` and `<key>` literally before running.)

---

## Phase 3 — Verify, never expose

After write, verify the key exists without printing the value:

```bash
jq 'has("<service>") and (.["<service>"] | has("<key>"))' ~/.claude/vault/credentials.json
```

Should print `true`. Do NOT cat the file. Do NOT print the value.

For services with a quick-check API, do a non-destructive auth check:
- github: `gh auth status` (after `export GH_TOKEN=$(jq -r .github.pat ~/.claude/vault/credentials.json)`)
- vercel: `curl -sf -H "Authorization: Bearer $(jq -r .vercel.token ~/.claude/vault/credentials.json)" https://api.vercel.com/v2/user >/dev/null && echo OK`
- supabase: `curl -sf -H "Authorization: Bearer $(jq -r .supabase.access_token ~/.claude/vault/credentials.json)" https://api.supabase.com/v1/organizations >/dev/null && echo OK`
- railway: `curl -sf -H "Authorization: Bearer $(jq -r .railway.token ~/.claude/vault/credentials.json)" -H "Content-Type: application/json" -d '{"query":"{ me { email } }"}' https://backboard.railway.app/graphql/v2 >/dev/null && echo OK`

---

## Rules

- **Never read, log, print, or include the credential value in any tool argument.** Read it through `jq` only when handing off to a service call.
- **Never commit the vault file.** It must be in `~/.claude/`, not in any project repo.
- **0600 perms always.** Re-check after every write.
- **No echoes in shell.** When using `read`, always use `-s` flag.
- **No tokens in commit messages, PR bodies, GitHub Actions workflows.** Use platform secret stores for CI.

---

## Handoff

> **Done.** Credential added. The provisioner agent that needed it can now run.
