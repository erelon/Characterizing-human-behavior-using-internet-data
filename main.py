import praw
from collections import defaultdict
import time
import tqdm
import pandas as pd

from secret import secret

# Set up the Reddit API client
reddit = praw.Reddit(**secret)


def get_recent_users(subreddit_name, limit=100):
    """Fetch unique users from recent posts and comments in a subreddit."""
    users = defaultdict(lambda: defaultdict(int))
    subreddit = reddit.subreddit(subreddit_name)
    for submission in tqdm.tqdm(subreddit.new(limit=limit), total=limit,
                                desc=f"Fetching users from r/{subreddit_name}"):
        # Add post author
        if submission.author:
            users[submission.author.name]['post'] += 1
        # Add comment authors
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.author:
                users[comment.author.name]['comment'] += 1
    return users


def check_user_activity_in_subreddits(users, target_subreddits, limit=100):
    """Check if users are active in target subreddits and store their activity."""
    user_activity = defaultdict(lambda: defaultdict(int))
    for user_name in tqdm.tqdm(users, total=len(users), desc="Checking user activity"):
        try:
            user = reddit.redditor(user_name)
            for comment in user.comments.new(limit=limit):
                if comment.subreddit.display_name in target_subreddits:
                    user_activity[user_name]['comment'] += 1
            for submission in user.submissions.new(limit=limit):
                if submission.subreddit.display_name in target_subreddits:
                    user_activity[user_name]['post'] += 1
        except Exception as e:
            print(f"Error fetching data for user {user_name}: {e}")
        time.sleep(0.01)  # Avoid rate-limiting
    return user_activity


def main():
    limit = 25
    # Define the subreddits to check
    target_subreddits = ['depression', 'mentalhealth', 'depression_help']
    source_subreddit = 'sarcasm'

    # Step 1: Get recent users from r/sarcasm
    users_in_sarcasm = get_recent_users(source_subreddit, limit=limit)
    print("Num of users: ", len(users_in_sarcasm))

    # Step 2: Check these users' activity in depression-related subreddits
    user_activity = check_user_activity_in_subreddits(users_in_sarcasm, target_subreddits, limit=limit)

    print(users_in_sarcasm)
    print(user_activity)

    # Take the users who are active in the target subreddits and save a df with the comments and posts of these users
    # in the source and target subreddit

    df = pd.DataFrame(columns=['user', 'source_subreddit_posts', 'source_subreddit_comments',
                               'target_subreddit_posts', 'target_subreddit_comments',
                               'source_subreddit_total', 'target_subreddit_total'])

    for user in user_activity:
        if user_activity[user]['comment'] > 0 or user_activity[user]['post'] > 0:
            df = df._append({'user': user,
                             'source_subreddit_posts': users_in_sarcasm[user]['post'],
                             'source_subreddit_comments': users_in_sarcasm[user]['comment'],
                             'target_subreddit_posts': user_activity[user]['post'],
                             'target_subreddit_comments': user_activity[user]['comment'],
                             'source_subreddit_total': users_in_sarcasm[user]['post'] + users_in_sarcasm[user][
                                 'comment'],
                             'target_subreddit_total': user_activity[user]['post'] + user_activity[user]['comment']},
                            ignore_index=True)
    for user in users_in_sarcasm:
        if user not in user_activity:
            df = df._append({'user': user,
                             'source_subreddit_posts': users_in_sarcasm[user]['post'],
                             'source_subreddit_comments': users_in_sarcasm[user]['comment'],
                             'target_subreddit_posts': 0,
                             'target_subreddit_comments': 0,
                             'source_subreddit_total': users_in_sarcasm[user]['post'] + users_in_sarcasm[user][
                                 'comment'],
                             'target_subreddit_total': 0}, ignore_index=True)

    df.to_csv('users_activity.csv', index=False)


if __name__ == '__main__':
    main()
