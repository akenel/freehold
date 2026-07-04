# Social logins — Google, GitHub, Facebook (and a note on Telegram)

Freehold's shared Keycloak brokers social logins as **identity providers**. They
ship in every realm but **disabled with an empty client id**, so a fresh clone
shows no broken buttons. You turn on only what you configure.

## How it works

1. Create an OAuth app on the provider (Google / GitHub / Facebook).
2. Put its **client id + secret** in `.env`.
3. Run `make idp` — it writes the secret into Keycloak's file vault (never
   committed) and stamps the client id in + flips the provider **enabled** in the
   realm JSONs, for all three realms.
4. `up` (fresh box) or re-import. The button appears on the login screen.

Client **ids** are public (fine to commit in your own fork); client **secrets**
live only in `.env` → the vault.

## Redirect URIs to register

One OAuth app per provider is simplest — give it all the realm redirect URIs it
needs. The pattern is:

```
https://auth.wolfhold.app/realms/<realm>/broker/<alias>/endpoint
```

So register these (add the `localhost` ones too if you test social login in dev):

| Provider (alias) | Redirect URIs |
|---|---|
| Google (`google`) | `https://auth.wolfhold.app/realms/kc-prd/broker/google/endpoint`<br>`…/realms/kc-stg/broker/google/endpoint` · `…/realms/kc-sbx/broker/google/endpoint`<br>`https://localhost:8443/realms/kc-sbx/broker/google/endpoint` (dev) |
| GitHub (`github`) | same paths with `/broker/github/endpoint` |
| Facebook (`facebook`) | same paths with `/broker/facebook/endpoint` |

## Provider setup, in short

**Google** — [Google Cloud Console](https://console.cloud.google.com) → APIs &
Services → Credentials → *Create OAuth client ID* → Web application. Add the
redirect URIs above. Copy the client id + secret into `GOOGLE_CLIENT_ID` /
`GOOGLE_CLIENT_SECRET`.

**GitHub** — Settings → Developer settings → *OAuth Apps* → New. Authorization
callback URL = the `…/broker/github/endpoint` for the realm you use most (GitHub
allows one callback per app, so for multiple realms make one app per realm, or
use its wildcard-less matching). `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`.

**Facebook** — [developers.facebook.com](https://developers.facebook.com) → create
an app → *Facebook Login* → Valid OAuth Redirect URIs. Note Facebook requires a
privacy-policy URL and app review before the `email` scope works for the public.
`FACEBOOK_CLIENT_ID` / `FACEBOOK_CLIENT_SECRET`.

Then:

```
make idp
docker compose up -d          # fresh box; or down && up to re-import realms
```

## Telegram — the exception

Telegram is **not** an OAuth2/OIDC provider — it authenticates via its own Login
Widget (a signed payload verified with your bot token), so Keycloak has no
built-in broker for it. Options, in order of effort:

- **Custom Keycloak extension** — a community Telegram SPI `.jar` dropped into the
  Keycloak image (adds a real "Login with Telegram" button). Most faithful.
- **App-side widget** — render Telegram's widget on our own page and exchange the
  verified payload for a Keycloak session via a custom endpoint.

Either is a separate, chunkier task than the built-in three. Say the word and I'll
scope the extension approach (it means baking a jar into `keycloak/` + a build
step, so it's a real addition, not a config toggle).
