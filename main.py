import praw
from collections import defaultdict
import time
import tqdm
import pandas as pd

# Set up the Reddit API client
reddit = praw.Reddit(
    client_id='aTdnEKlXERqwYZUQzk3ShQ',
    client_secret='KYtKfbauawy6iIOK6KNqpSXMAZ9G8A',
    user_agent='/u/erelon'
)


def get_recent_users(subreddit_name, limit=100):
    """Fetch unique users from recent posts and comments in a subreddit."""
    users = set()
    subreddit = reddit.subreddit(subreddit_name)
    for submission in tqdm.tqdm(subreddit.new(limit=limit), total=limit,
                                desc=f"Fetching users from r/{subreddit_name}"):
        # Add post author
        if submission.author:
            users.add(submission.author.name)
        # Add comment authors
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.author:
                users.add(comment.author.name)
    return users


def check_user_activity_in_subreddits(users, target_subreddits, limit=100):
    """Check if users are active in target subreddits and store their activity."""
    user_activity = defaultdict(list)
    for user_name in tqdm.tqdm(users, total=len(users), desc="Checking user activity"):
        try:
            user = reddit.redditor(user_name)
            for comment in user.comments.new(limit=limit):
                if comment.subreddit.display_name in target_subreddits:
                    user_activity[user_name].append(comment.subreddit.display_name)
            for submission in user.submissions.new(limit=limit):
                if submission.subreddit.display_name in target_subreddits:
                    user_activity[user_name].append(submission.subreddit.display_name)
        except Exception as e:
            print(f"Error fetching data for user {user_name}: {e}")
        time.sleep(0.1)  # Avoid rate-limiting
    return user_activity


def main():
    # Define the subreddits to check
    target_subreddits = ['depression', 'mentalhealth', 'depression_help']
    source_subreddit = 'sarcasm'

    # Step 1: Get recent users from r/sarcasm
    users_in_sarcasm = get_recent_users(source_subreddit, limit=100)
    print("Num of users: ", users_in_sarcasm)

    # Step 2: Check these users' activity in depression-related subreddits
    user_activity = check_user_activity_in_subreddits(users_in_sarcasm, target_subreddits, limit=100)

    pd.DataFrame(user_activity).to_csv('user_activity.csv')


if __name__ == '__main__':
    main()
