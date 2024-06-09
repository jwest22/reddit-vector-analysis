import requests
import json
import time
import os
from datetime import datetime, timedelta

def get_reddit_data(subreddit, hours, limit=100):
    base_url = f'https://www.reddit.com/r/{subreddit}'
    posts_url = f'{base_url}/new.json?limit={limit}'
    comments_url = f'{base_url}/comments.json?limit={limit}'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_json(url):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    def utc_to_datetime(utc_timestamp):
        return datetime.utcfromtimestamp(utc_timestamp)
    
    all_posts = []
    all_comments = []
    
    def fetch_data(url, data_list, data_type):
        after = None
        while True:
            paginated_url = f"{url}&after={after}" if after else url
            data = get_json(paginated_url)
            if data_type == 'posts':
                items = data['data']['children']
                for item in items:
                    post_time = utc_to_datetime(item['data']['created_utc'])
                    if post_time < cutoff_time:
                        return
                    post_info = {
                        'title': item['data']['title'],
                        'author': item['data']['author'],
                        'created_utc': post_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'url': item['data']['url'],
                        'permalink': item['data']['permalink']
                    }
                    data_list.append(post_info)
                after = items[-1]['data']['name'] if items else None
            elif data_type == 'comments':
                items = data['data']['children']
                for item in items:
                    comment_time = utc_to_datetime(item['data']['created_utc'])
                    if comment_time < cutoff_time:
                        return
                    comment_info = {
                        'body': item['data']['body'],
                        'author': item['data']['author'],
                        'created_utc': comment_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'permalink': item['data']['permalink']
                    }
                    data_list.append(comment_info)
                after = items[-1]['data']['name'] if items else None
    
    fetch_data(posts_url, all_posts, 'posts')
    fetch_data(comments_url, all_comments, 'comments')
    
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    
    os.makedirs('input', exist_ok=True)
    
    posts_filename = f'input/{subreddit}_posts_{timestamp}.txt'
    comments_filename = f'input/{subreddit}_comments_{timestamp}.txt'
    
    with open(posts_filename, 'w', encoding='utf-8') as posts_file:
        for post in all_posts:
            posts_file.write(json.dumps(post) + '\n')
    
    with open(comments_filename, 'w', encoding='utf-8') as comments_file:
        for comment in all_comments:
            comments_file.write(json.dumps(comment) + '\n')
    
    return posts_filename, comments_filename

def run_comment_retrieval(subreddit, hours):
    posts_file, comments_file = get_reddit_data(subreddit, hours)
    print(f'Posts saved to {posts_file}')
    print(f'Comments saved to {comments_file}')
