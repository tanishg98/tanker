# Vault & credentials

Tanker keeps service credentials in `~/.claude/vault/credentials.json` with 0600 perms. Provisioner agents read directly from this file. Tanker never logs values, never includes them in commits, never echoes them in chat.

## Schema

```json
{
  "github": { "token": "ghp_..." },
  "vercel": { "token": "..." },
  "supabase": { "access_token": "..." },
  "railway": { "token": "..." },
  "anthropic": { "api_key": "..." },
  "openai": { "api_key": "..." },
  "stripe": { "secret_key": "..." },
  "resend": { "api_key": "..." },
  "sentry": { "auth_token": "..." },
  "plausible": { "api_key": "..." }
}
```

## Add or update

```bash
/vault-add <service>
# prompts for the value, writes with 0600
```

## Read (manually)

```bash
jq -r '.github.token' ~/.claude/vault/credentials.json
```

## Why a flat file

- Simple — no extra service to install.
- Local — values never leave the machine.
- Inspectable — easy to audit, easy to clean up.

## Don't

- Don't `git add ~/.claude/vault/credentials.json`. It lives outside any repo.
- Don't echo values in chat. Tanker's provisioner agents read with `jq` and pass via env vars only.
- Don't share. Each operator has their own vault.

## Per-project credentials

Some workflows need per-project keys (e.g. a Supabase project per Tanker run). The vault uses a namespacing convention:

```json
{
  "supabase": { "access_token": "..." },
  ".supabase.todo-magic-kanban": { "project_ref": "abcd1234", "anon_key": "...", "service_key": "..." }
}
```

`supabase-provisioner` writes per-project keys with the `.<service>.<slug>` convention. This keeps the global access token separate from project-specific secrets.
