import database as db
db.create_tables()
with db.get_db() as conn:
    rows = conn.execute('''
        SELECT t.id, t.name, s.name as subject, s.user_id
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.name = \"Integration\"
    ''').fetchall()
    for r in rows:
        print('topic_id:', r['id'], 'subject:', r['subject'], 'user_id:', r['user_id'])
    
    q_rows = conn.execute('''
        SELECT topic_id, COUNT(*) as cnt 
        FROM questions 
        WHERE topic_id IN (SELECT id FROM topics WHERE name = \"Integration\")
        GROUP BY topic_id
    ''').fetchall()
    print('Questions per Integration topic:')
    for r in q_rows:
        print('  topic_id:', r['topic_id'], 'questions:', r['cnt'])
