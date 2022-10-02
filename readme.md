# Readme

## Usage

使用顺序与注意事项

1. `repo.py`

   - 如果从零开始搜，那么将 `fn` & `newfn` 设置为一样的输出文件名
   - 如果已有一个repo爬虫结果文件，想要在此基础上继续进行增量查找，则 `fn` 为旧结果， `newfn` 为新的输出文件
   - 以两个拉丁字母排列组合（`aa`）作为关键字进行搜索

2. (optional) `reorder_repos.py`

   - 把结果按照star从多到少排序

3. `write_repo_from_txt_into_db.py`

   - 把 repo 爬虫结果导入到 repos.db 的 repos 里

   - ```sqlite
     CREATE TABLE IF NOT EXISTS repos (
                 ID          INTEGER         PRIMARY KEY,
                 name        text, 
                 owner       text, 
                 stars       integer, 
                 forks       integer, 
                 watchers    integer, 
                 is_android  boolean
     )
     ```

4. `commit.py`

   - 以 "resource leak" 作为关键字进行搜索

   - 爬取 commit 存到 repos.db 的 commits 里

   - ```sqlite
     CREATE TABLE IF NOT EXISTS commits (
                     ID              INTEGER         PRIMARY KEY,
                     cid             integer,
                     repo_id         integer,
                     sha             text,
                     date            text,
                     author          text,
                     message         text,
                     defect_ver      text,
                     nodefect_ver    text,
                     FOREIGN KEY (repo_id) REFERENCES repos (ID)
     )
     ```
