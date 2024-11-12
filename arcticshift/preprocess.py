import json
from collections import defaultdict

import tqdm


def clean_post(post):
    # Define the fields you want to keep
    if post['author'] == '[deleted]':
        return None
    fields_to_keep = ['id', 'title', 'selftext', 'created_utc']
    cleaned_post = {field: post[field] for field in fields_to_keep}
    cleaned_post["body"] = cleaned_post.pop("selftext")
    cleaned_post["is_post"] = True
    return post['author'], cleaned_post


def clean_comment(post):
    # Define the fields you want to keep
    if post['author'] == '[deleted]':
        return None
    fields_to_keep = ['id', 'body', 'created_utc']
    cleaned_post = {field: post[field] for field in fields_to_keep}
    cleaned_post["title"] = ""
    cleaned_post["is_post"] = False
    return post["author"], cleaned_post


def get_from_subreddit(subreddit_name, all_data):
    jsonl_file = rf"C:\Users\erels\Downloads\r_{subreddit_name}_posts.jsonl"
    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in tqdm.tqdm(file):
            data = json.loads(line)
            out = clean_post(data)
            if out:
                all_data[out[0]][subreddit_name].append(out[1])

    jsonl_file = rf"C:\Users\erels\Downloads\r_{subreddit_name}_comments.jsonl"
    # Open the file and load each line as a JSON object
    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in tqdm.tqdm(file):
            data = json.loads(line)
            out = clean_comment(data)
            if out:
                all_data[out[0]][subreddit_name].append(out[1])


if __name__ == '__main__':
    all_data = defaultdict(lambda: defaultdict(list))
    get_from_subreddit("funny", all_data)
    get_from_subreddit("depression", all_data)

    json.dump(all_data, open("cleaned_data.json", "w"))
