# ClickUp -> dashboard sync

Source of truth: ClickUp list 901100143518 ("Comprehensive Remote Employer Profiles").
Dashboard files: `index.html` (read-only page), `data/index.json` (ids + lastSync), `data/e/<taskId>.json` (one file per employer).
`sync/cu_map.py` turns raw ClickUp tasks into employer records (field IDs and option labels are in that file).
`data/index.json.lastSync` = newest ClickUp date_updated (ms) already applied. Employers with a newer date_updated are re-fetched.
