from datetime import datetime
import requests
import sys
import time

url = 'https://raw.githubusercontent.com/gohugoio/hugoThemesSiteBuilder/main/themes.txt'
token = sys.argv[1]
auth = "Bearer " + token

def get_repo_star(repo_url: str) -> int:
    segs = repo_url.split('/')
    owner = segs[1]
    repo = segs[2]
    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}',
                            headers = {
                                'Accept': 'application/vnd.github+json',
                                'X-GitHub-Api-Version': '2022-11-28',
                                'Authorization': auth})
    res_json = response.json()
    return res_json['stargazers_count']

m: dict[str, dict] = {}

response = requests.get(url)
if response.status_code == 200:
    file_content = response.text
    themes = file_content.strip().split('\n')
    theme_nums = len(themes)
    print(f"Got {theme_nums} themes")
    start = time.time()
    for i, theme in enumerate(themes):
        if not theme.startswith('github.com'):
            print(f"Skipping none github theme: {theme}")
            continue

        segs = theme.split('/')
        owner = segs[1]
        repo = segs[2]
        repo_url = f"https://github.com/{owner}/{repo}"

        stars = get_repo_star(theme)
        m[repo] = {"theme": theme, "stars": stars, "url": repo_url} 
        cost = time.time() - start
        total_cost = int(cost / (i+1) * theme_nums)
        cost = int(cost)
        print(f"[{cost}s/{total_cost}s] [{i+1}/{theme_nums}] {theme} stars: {stars}")
else:
    print(f"Failed to fetch {url}, Status code: {response.status_code}")

m = dict(sorted(m.items(), key=lambda item: item[1]["stars"], reverse=True))

with open("README.md", 'w') as f:  
    f.write("Updated at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n---\n")
    f.write('| {:40} | {:20} |\n'.format("Theme", "Stars"))
    f.write('| {:40} | {:20} |\n'.format(":---", ":---"))
    for key, value in m.items():  
        theme_md = "[" + key + "](" + value["url"] + ")"
        f.write('| {:40} | {:20} |\n'.format(theme_md, value["stars"]))
