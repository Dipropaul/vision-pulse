import sqlite3

conn = sqlite3.connect('visionpulse.db')
cursor = conn.cursor()
cursor.execute('SELECT script, prompts FROM videos ORDER BY created_at DESC LIMIT 1')
row = cursor.fetchone()
print('=== SCRIPT ===')
print(row[0][:1000])
print('\n=== FIRST PROMPT ===')
if row[1]:
    import json
    prompts = json.loads(row[1])
    if prompts:
        print(prompts[0])
conn.close()
