# WORKLIST — Freehold Health Dashboard
<!-- Ordered by priority. Top = next. Cross off when done. -->

- [x] 1. Read deps.py, models.py, main.py, audit.py, build_info.py to understand Freehold's patterns
- [x] 2. Create a HealthCheck model in models.py (service, status, checked_at, detail)
- [x] 3. Create routers/health.py with a /status page that checks Postgres, Keycloak, MinIO, and app build SHA
- [x] 4. Register the health router in main.py
- [x] 5. Create a templates/status.html page showing service health with green/red indicators
- [x] 6. Write tests for the health endpoint in tests/test_health.py
- [x] 7. Run the full test suite to prove nothing broke
- [x] 8. Git commit with a meaningful message
