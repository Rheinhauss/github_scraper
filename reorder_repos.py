

def main():
    with open('repos_500_a.txt', 'r') as f, open('repos_500_reorder.txt', 'w') as f2:
       l = [[x.strip() for x in line.strip().split(',')] for line in f.readlines()]
       l.sort(key=lambda x: int(x[1]), reverse=True)
       wl = '\n'.join([', '.join(x) for x in l])
       f2.write(wl)


if __name__ == '__main__':
    main()