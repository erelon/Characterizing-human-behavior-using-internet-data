import praw
from collections import defaultdict
import pandas as pd
import time
import tqdm
from datetime import datetime

# Import your Reddit API credentials from a separate file (secret.py).
from secret import secret

# Set up the Reddit API client
reddit = praw.Reddit(**secret)

# Define the subreddits
depression_subreddits = ['depression']
humor_subreddits = ['funny']

def get_recent_users(subreddit_name, limit=100, days_ago=30):
    """Fetch unique users from recent posts and comments in a subreddit."""
    users = defaultdict(lambda: {'posts': 0, 'comments': 0, 'timestamp': []})
    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in tqdm.tqdm(subreddit.new(limit=limit), total=limit, desc=f"Fetching users from r/{subreddit_name}"):
        if submission.created_utc < time.time() - days_ago * 86400:
            continue
        if submission.author:
            users[submission.author.name]['posts'] += 1
            users[submission.author.name]['timestamp'].append(submission.created_utc)
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.created_utc < time.time() - days_ago * 86400:
                continue
            if comment.author:
                users[comment.author.name]['comments'] += 1
                users[comment.author.name]['timestamp'].append(comment.created_utc)
    return users

def get_user_details(username):
    """Fetch user join date and post/comment karma."""
    try:
        user = reddit.redditor(username)
        join_date = datetime.utcfromtimestamp(user.created_utc)
        post_count = user.link_karma
        comment_count = user.comment_karma
        return join_date, post_count, comment_count
    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
        return None, None, None

def check_user_activity_in_subreddits(users, target_subreddits, limit=30):
    """Check if users are active in target subreddits after initial activity."""
    user_activity = defaultdict(lambda: {'posts': 0, 'comments': 0, 'karma': 0})
    for user_name in tqdm.tqdm(users, total=len(users), desc="Checking user activity"):
        try:
            user = reddit.redditor(user_name)
            for comment in user.comments.new(limit=limit):
                if comment.subreddit.display_name in target_subreddits:
                    user_activity[user_name]['comments'] += 1
                    user_activity[user_name]['karma'] += comment.score
            for submission in user.submissions.new(limit=limit):
                if submission.subreddit.display_name in target_subreddits:
                    user_activity[user_name]['posts'] += 1
                    user_activity[user_name]['karma'] += submission.score
        except Exception as e:
            print(f"Error fetching data for user {user_name}: {e}")
        time.sleep(0.01)
    return user_activity

def main():
    limit = 100
    days_ago_initial = 30  # Check initial depression activity within this period
    days_ago_followup = 60  # Follow-up humor activity after this period

    # Step 1: Collect initial user activity in depression-related subreddits
    initial_users = defaultdict(dict)
    for subreddit in depression_subreddits:
        users = get_recent_users(subreddit, limit=limit, days_ago=days_ago_initial)
        initial_users.update(users)
    
    # Step 2: Track these users' activity in humor-related subreddits later
    humor_activity = check_user_activity_in_subreddits(initial_users, humor_subreddits, limit=limit)

    # Step 3: Track their subsequent activity in depression-related subreddits
    followup_depression_activity = check_user_activity_in_subreddits(initial_users, depression_subreddits, limit=limit)

    # Create a list to store matched user data
    matched_user_data = []

    # Step 4: Check if users joined r/depression before r/funny and fetch their join dates, posts, and comments
    for user, data in initial_users.items():
        # Fetch join date and post/comment stats for r/depression
        join_depression_date, post_count_depression, comment_count_depression = get_user_details(user)

        # Check if user is also in humor subreddits and joined humor subreddits later
        if join_depression_date:
            for subreddit in humor_subreddits:
                try:
                    user_data_in_humor = reddit.subreddit(subreddit).search(f"author:{user}", limit=1)
                    if user_data_in_humor:
                        # Check if the user joined the humor subreddit after depression
                        join_humor_date = min([submission.created_utc for submission in user_data_in_humor])
                        if join_humor_date > join_depression_date.timestamp():
                            humor_posts = humor_activity[user].get('posts', 0)
                            humor_comments = humor_activity[user].get('comments', 0)
                            humor_karma = humor_activity[user].get('karma', 0)
                            matched_user_data.append({
                                'Username': user,
                                'Join Date (r/depression)': join_depression_date,
                                'Posts (r/depression)': post_count_depression,
                                'Comments (r/depression)': comment_count_depression,
                                'Join Date (r/funny)': datetime.utcfromtimestamp(join_humor_date) if join_humor_date else None,
                                'Posts (r/funny)': humor_posts,
                                'Comments (r/funny)': humor_comments,
                                'Karma (r/funny)': humor_karma
                            })
                except Exception as e:
                    print(f"Error checking humor activity for {user}: {e}")

    # Step 5: Create DataFrame and save to Excel
    df = pd.DataFrame(matched_user_data)
    df.to_excel('user_humor_depression_activity.xlsx', index=False)

    print("Data saved to user_humor_depression_activity.xlsx")

if __name__ == '__main__':
    main()
