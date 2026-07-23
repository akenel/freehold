# Freehold — Caddy with the Porkbun DNS plugin.
#
# The stock caddy image can't do DNS-01, so it can't get WILDCARD certs. This
# builds Caddy with `caddy-dns/porkbun` so it can answer the ACME DNS-01 challenge
# by writing a TXT record via Porkbun's API — which is what lets us mint ONE
# *.wolfhold.app cert for every subdomain (see ../Caddyfile.prod).
#
# The prod overlay builds this as freehold-caddy:prd. Rebuild after bumping Caddy.
FROM caddy:2-builder AS builder
RUN xcaddy build --with github.com/caddy-dns/porkbun

FROM caddy:2-alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
