import time
import requests
from pprint import pprint
import os
from myconfig import g, CONFIG
from myexceptions import *


FILE = None
repo_set = set()
fn = 'repos_1k.txt'
newfn = 'repos_500_a.txt' # 比repos_1k.txt多出的repo


def save_repo_info(name: str, stars: int, forks: int, watchers:int, is_android: bool = False):
    global g
    global FILE
    global CONFIG
    global repo_set
    # FILE.write(name+', '+str(stars)+'\n')
    print(
        f"[YES!] found BIG repo: {name} with {stars} stars, {forks} forks. Android related: {is_android}")
    FILE.write(f'{name}, {stars}, {forks}, {watchers}, {is_android}\n')
    FILE.flush()


def search(word: str):
    global g
    global FILE
    global CONFIG
    global repo_set
    
    page = 0
    stop = False
    while True:
        while True:
            try:
                r = requests.get(url=CONFIG['rurl'].format(word,page), headers={
                                'Authorization': f'token {CONFIG["token"]}'})
                if r.status_code == 422:
                    raise MaxPageExceedException
                elif r.status_code != 200 and r.status_code != 422:
                    raise RateException
                else:
                    rl = r.json()["items"]
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

        for repo in rl:
            stars = repo["stargazers_count"]
            # print(f'[INFO] {repo.full_name}, {stars}')
            if stars < CONFIG['min_stars']:
                stop = True
                break
            fullname = repo["full_name"]
            if fullname in repo_set:
                print(f'[INFO] already has {fullname} in set')
                continue
            repo_set.add(fullname)
            is_android = False
            if 'android' in fullname:
                is_android = True
            for topic in repo["topics"]:
                if topic == 'android':
                    is_android = True
                    break
            save_repo_info(fullname, stars, repo["forks_count"], repo["watchers_count"], is_android)

        page += 1
        if stop:
            break

def main():
    global g
    global FILE
    global CONFIG
    global repo_set
    global fn
    global newfn
    
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    ctime = time.ctime().replace(':', '-')

    process = 'aa'
    print(f'[INFO] opening file {fn}')
    if os.path.exists("process.txt"):
        with open("process.txt", 'r') as pf:
            process = pf.readlines()[0]

    print(f'[INFO] starting from "{process}"')

    if os.path.exists(fn):
        with open(fn, 'r') as f:
            for line in f.readlines():
                l = [x.strip() for x in line.strip().split(',')]
                repo_set.add(l[0])
    with open(newfn, 'a') as f:
        FILE = f
        for x in alphabet:
            if x < process[0]:
                continue
            for y in alphabet:
                if x == process[0] and y <= process[1] and process!='aa':
                    continue
                # for z in alphabet:
                word = x+y
                print(f'[INFO] now searching repos: "{word}"')
                # check_repo(word)
                search(word)
                with open("process.txt", 'w+') as pf:
                    pf.write(word)


if __name__ == "__main__":
    main()
