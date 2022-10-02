import sqlite3
import os
import github
from myconfig import g, CONFIG
import requests
from myexceptions import *
import time


progress: int = 3056
maxid = None
c: sqlite3.Cursor = None
conn = None


class Repo:

    def __init__(self, arglist: list):
        assert len(arglist) == 7
        self.name: str = arglist[2]
        self.owner: str = arglist[1]
        self.stars: int = int(arglist[3])
        self.forks: int = int(arglist[4])
        self.watchers: int = int(arglist[5])
        self.is_android: bool = bool(arglist[6])
        self.fullname: str = f'{self.owner}/{self.name}'
        self._id: int = int(arglist[0])


def search_repo_for_commits(repo: Repo):
    global c
    global conn
    cid = 0
    page = 1
    stop = False
    first = True
    while True:
        while True:
            try:
                uuu = CONFIG['curl'].format(repo.fullname, page)
                print(f'[INFO] {uuu}')
                r = requests.get(url=uuu, headers={
                    'Authorization': f'token {CONFIG["token"]}'})
                if r.status_code == 422:
                    raise MaxPageExceedException
                elif r.status_code != 200 and r.status_code != 422:
                    print(f'status code: {r.status_code}')
                    raise RateException
                else:
                    rl = r.json()["items"]
                    if first == False and r.json()['total_count'] < page*100:
                        stop = True
                    break
            except RateException:
                print("[WARN] rate limit exceeded, sleep 60s")
                time.sleep(60)
                continue
            except MaxPageExceedException:
                stop = True
                break
            except Exception as e:
                print(f"[ERRO] {e}, sleep 10s")
                time.sleep(10)
                continue

        if stop:
            break

        for commit in rl:
            print(f'[INFO] found commit {repo.fullname}_{cid}')
            msg = commit["commit"]["message"].replace('"', "'")
            tmp = ', '.join([x['sha'] for x in commit['parents']])
            sttt = f'''INSERT INTO commits VALUES (
                                NULL, 
                                {cid}, 
                                {repo._id}, 
                                "{commit["sha"]}", 
                                "{commit["commit"]["author"]["date"]}", 
                                "{commit["commit"]["author"]["name"]}", 
                                "{msg}",
                                "{tmp}",
                                "{commit["sha"]}")'''
            try:
                c.execute(sttt)
            except Exception as e:
                print(sttt)
            conn.commit()
            cid += 1

        page += 1
        first = False
        if stop:
            break


def main():
    global progress
    global maxid
    global conn
    global c
    if os.path.exists('progress_commit.txt'):
        with open('progress_commit.txt', 'r') as f:
            progress = int(f.read())
    else:
        progress = -1

    conn = sqlite3.connect('file:repos.db?mode=ro', uri=True)
    c = conn.cursor()
    res = c.execute(f'SELECT * FROM repos where ID>{progress}').fetchall() if maxid is None else c.execute(
        f'SELECT * FROM repos where ID>{progress} AND ID<{maxid}').fetchall()
    conn.close()
    conn = sqlite3.connect('repos.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS commits (
                ID              INTEGER         PRIMARY KEY,
                cid             integer,
                repo_id         integer,
                sha             text,
                date            text,
                author          text,
                message         text,
                defect_ver      text,
                nodefect_ver    text,
                FOREIGN KEY (repo_id) REFERENCES repos (ID))
            """)
    for r in res:
        repo = Repo(r)
        print(repo.fullname)
        search_repo_for_commits(repo)
        progress = r[0]
        with open('progress_commit.txt', 'w+') as f:
            f.write(str(progress))


if __name__ == '__main__':
    main()
