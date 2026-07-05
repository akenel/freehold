# Email — SMTP2GO by default (free), any SMTP works

Keycloak sends the transactional mail — **forgot-password** and verify-email —
over plain SMTP. Freehold defaults to **SMTP2GO** (free tier: 1,000 emails/month,
custom sender domains allowed), which covers a small app's needs for $0. Any SMTP
provider works though (Resend, Brevo, Amazon SES, your own postfix) — you only
change the `SMTP_*` vars.

The config is provider-agnostic: host/port/user/from live in `.env` (→ stamped
into the realms by `make apply`); the password lives in the SOPS/vault (never in
git) as `${vault.smtppass}`.

## SMTP2GO setup, click for click

**1. Get an account** (the signup gotcha: it rejects free-mail addresses).
   - SMTP2GO's signup demands an email **at a domain you own** (`Error code 6`
     otherwise). If you don't have a mailbox on your domain, add a **free email
     forward** at your registrar — e.g. Porkbun → your-domain → Email Forwarding →
     `admin@your-domain` → your gmail — and sign up with `admin@your-domain`.

**2. Create an SMTP user.** Dashboard → **Sending → SMTP Users → Add SMTP User**.
   Note the **username** and **password** it gives you (that password is
   `SMTP_PASSWORD`).

**3. Verify a sender.** Dashboard → **Sending → Verified Senders / Sender Domains**.
   Add your domain (e.g. `wolfhold.app`) and add the DNS records it shows at your
   registrar (SPF / DKIM / a CNAME or two). Once green, `no-reply@your-domain`
   can send. (Or verify a single sender email if you don't want to do DNS yet.)

**4. Wire it into Freehold.**
   ```bash
   make secrets-edit ENV=sandbox      # or edit .env directly for a local test
   #   SMTP_USER=<your smtp2go username>
   #   SMTP_PASSWORD=<your smtp2go password>
   #   SMTP_FROM=no-reply@your-verified-domain   (SMTP_FROM_NAME=Wolfhold)
   make secrets ENV=sandbox           # decrypt → .env → vault + stamp realms
   docker compose up -d               # fresh box; or down && up to re-import
   ```

## Defaults (in `.env.example`)

```
SMTP_HOST=mail.smtp2go.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_SSL=false
SMTP_USER=          # from your provider
SMTP_PASSWORD=      # from your provider (goes to the vault, not git)
SMTP_FROM=no-reply@wolfhold.app     # MUST be a verified sender/domain
SMTP_FROM_NAME=Wolfhold
```

## Using a different provider

Just change the four transport vars — e.g. Resend (`smtp.resend.com` / user
`resend` / port 465 / `SMTP_SSL=true`), Brevo (`smtp-relay.brevo.com` / 587),
SES, etc. `make apply` stamps whatever you set into all three realms.

## Verify it actually sends

`make apply` vaults the password + sets the sender on the running Keycloak (no
restart needed), then hit any login screen → **Forgot password?**. If mail doesn't
arrive, 99% of the time the **sender domain isn't verified** at the provider —
check that first.
