from cmath import nan
import csv
from operator import itemgetter
import sqlite3
import os
import time
from myconfig import *
from myexceptions import *
import requests
import re


repo_create_time_map = {}


def get_resp(url, auth=True):
    while True:
        try:
            if auth:
                resp = requests.get(url, headers={
                    'Authorization': f'token {CONFIG["token"]}'})
            else:
                resp = requests.get(url)
            if resp.status_code != 200 and resp.status_code != 422:
                print(f'status code: {resp.status_code}', flush=True)
                raise RateException
            return resp
        except RateException:
            print("[WARN] rate limit exceeded, sleep 60s", flush=True)
            time.sleep(60)
            continue
        except Exception as e:
            print(f"[ERRO] {e}, sleep 10s", flush=True)
            time.sleep(10)
            continue


def get_commitCount(owner, name):
    resp = get_resp(
        f'https://api.github.com/repos/{owner}/{name}/commits?per_page=1')
    return re.search('\d+$', resp.links['last']['url']).group()


def get_repo_create_time(owner, name):
    global repo_create_time_map
    repo_fullname = f'{owner}/{name}'
    if repo_fullname in repo_create_time_map:
        return repo_create_time_map[repo_fullname]
    else:
        resp = get_resp(f'https://api.github.com/repos/{owner}/{name}')
        repo_create_time = resp.json()['created_at']
        repo_create_time_map[repo_fullname] = repo_create_time
        return repo_create_time


def get_commit_add_del_count(owner, name, sha):
    resp = get_resp(
        f'https://api.github.com/repos/{owner}/{name}/commits/{sha}')
    return resp.json()['stats']


def main():
    # Connect to the database
    conn = sqlite3.connect('repos.db')
    c = conn.cursor()
    result = c.execute('''
    SELECT  r.name, r.owner, r.stars, r.is_android, 
            c.cid, c.sha, c.date,
            c.defect_ver, c.nodefect_ver
    FROM    repos AS r, commits AS c
    WHERE   r.ID = c.repo_id
    ''').fetchall()
    # Create the CSV file

    with open('result.csv', 'w') as f:
        writer = csv.writer(f)
        # Write the header
        writer.writerow(['ID', 'repo_fullname', 'link_to_commit', '负责人', 'stars', 'commits',
                         'repo_create_time', 'version_defect', 'version_nodefect', 'add_del_lines', ])
        # Write the data
        ID = 0
        for row in result:
            ID += 1
            repo_fullname = f'{row[0]}/{row[1]}'
            link_to_commit = f'https://github.com/{row[0]}/{row[1]}/commit/{row[5]}'
            resp = ''
            stars = row[2]
            version_defect = row[7]
            version_nodefect = row[8]

            commmits = get_commitCount(row[0], row[1])
            repo_create_time = get_repo_create_time(row[0], row[1])
            addcnt, delcnt, totalcnt = itemgetter('additions', 'deletions', 'total')(
                get_commit_add_del_count(row[0], row[1], row[5]))
            add_del_lines = f'+{addcnt},-{delcnt}'
            writer.writerow([ID, repo_fullname, link_to_commit, resp, stars, commmits,
                             repo_create_time, version_defect, version_nodefect, add_del_lines])
            print(f'[INFO] {ID}\t{link_to_commit} done', flush=True)

    # Close the database connection
    conn.close()


if __name__ == '__main__':
    main()
