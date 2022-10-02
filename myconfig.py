from github import Github

CONFIG = {
    "min_stars": 500,
    "token": "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",
    "rurl": "https://api.github.com/search/repositories?q={}+language:java&sort=stars&order=desc&page={}&per_page=100",
    "curl": 'https://api.github.com/search/commits?q=repo:{}+resource+leak&per_pager=100&page={}'
}
g = Github(CONFIG['token'])
