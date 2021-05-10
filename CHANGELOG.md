## 2.0.0 (2021-05-10)

## 1.0.0 (2021-05-09)

### Feat

- **UserResource**: add ability for the user to delete their account
- handle changing or updating of user info
- add filestorage wrapper to handle cloud storage
- :wrench: Organize app config & add AWS configs
- :sparkles: Record user sessions & can invalidate them
- :sparkles: Add endpoints to user login
- :sparkles: decorator helper to check user roles
- :hammer: Add cli command to add users & update app settings
- :hammer: flask migrate init and first migration
- :hammer: add users blueprint and first api resource
- :construction_worker: add pre-commit framework to handle linting
- :hammer: Configure extensions used
- :hammer: Basic exception class for handling internal app errors
- :hammer: Extend sqlalchemy instance default model
- :sparkles: register helpers to flask
- :sparkles: add different registerer functions for flask instance
- :label: add typehinted chain helper function

### Refactor

- **User-Model**: add proxy properties for password and photo fields

### Fix

- :bug: Fix timestamp fields to include timezone
- :bug: Fix Extensions & their handlers

### Perf

- :zap: add proxy for user password checking
