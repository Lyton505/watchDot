#!/bin/bash
echo -e "Tables are:\n"

sqlite3 <<'EOF'
.open watchdot.db
.tables
EOF

echo -e "\nFirst 10 entries in intern_hits:\n"

sqlite3 <<'EOF'
.open watchdot.db
SELECT id,root_domain, sent_at FROM intern_hits;
EOF
