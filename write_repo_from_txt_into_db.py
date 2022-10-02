import sqlite3
from pprint import pprint

conn = sqlite3.connect('repos.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS repos (
            ID          INTEGER         PRIMARY KEY,
            name        text, 
            owner       text, 
            stars       integer, 
            forks       integer, 
            watchers    integer, 
            is_android  boolean)
        """)
# pprint(c.execute('SELECT * FROM repos').fetchall())
with open('repos_1k_reorder.txt', 'r') as f:
    l = [x.strip().split(', ') for x in f.readlines()]
    for ll in l:
        name, owner = ll[0].split('/')
        c.execute(
            f'INSERT INTO repos VALUES (NULL, "{name}", "{owner}", {ll[1]}, {ll[2]}, {ll[3]}, {ll[4]})')

conn.commit()
pprint(c.execute('SELECT * FROM repos').fetchall())
