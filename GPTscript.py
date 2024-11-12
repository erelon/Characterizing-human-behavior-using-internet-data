import praw
from collections import defaultdict
import pandas as pd
import time
from datetime import datetime
import tqdm  # For progress tracking

# Import your Reddit API credentials from a separate file (secret.py).
from secret import secret

# Set up the Reddit API client
reddit = praw.Reddit(**secret)

# Define the subreddits
depression_subreddit = 'depression'
humor_subreddit = 'funny'

def get_recent_users(subreddit_name, limit=1000):
    """Fetch unique users from recent posts and comments in a subreddit."""
    users = {}
    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in tqdm.tqdm(subreddit.new(limit=limit), desc=f"Fetching users from r/{subreddit_name}"):
        if submission.author and submission.author.name not in users:
            users[submission.author.name] = submission.created_utc
        for comment in submission.comments:
            if comment.author and comment.author.name not in users:
                users[comment.author.name] = comment.created_utc
    return users

def get_user_comments_in_subreddit(username, subreddit_name, before_timestamp, after_timestamp):
    """Fetch user's comments in a specific subreddit within given time range."""
    user_comments = []
    user = reddit.redditor(username)
    
    for comment in user.comments.new(limit=None):
        if comment.subreddit.display_name == subreddit_name:
            comment_time = comment.created_utc
            if before_timestamp <= comment_time <= after_timestamp:
                user_comments.append(comment.body)
                
    return user_comments

def get_user_join_date_in_subreddit(username, subreddit_name):
    """Fetch the join date for a user in a specific subreddit."""
    user = reddit.redditor(username)
    
    for comment in user.comments.new(limit=None):
        if comment.subreddit.display_name == subreddit_name:
            return comment.created_utc
    return None

def main():
    # Step 1: Collect initial users from the depression subreddit
    depression_users = get_recent_users(depression_subreddit, limit=100)
    
    # Data storage
    matched_user_data = []
    
    # Step 2: Check activity in r/funny after joining r/depression
    for user, depression_join_time in tqdm.tqdm(depression_users.items(), desc="Analyzing user activity", total=len(depression_users)):
        humor_join_time = get_user_join_date_in_subreddit(user, humor_subreddit)
        
        # Ensure the user joined r/funny after r/depression
        if humor_join_time and humor_join_time > depression_join_time:
            # Fetch comments in r/depression before and after joining r/funny
            before_comments = get_user_comments_in_subreddit(user, depression_subreddit, 0, humor_join_time)
            after_comments = get_user_comments_in_subreddit(user, depression_subreddit, humor_join_time, time.time())
            
            # Fetch comments in r/funny after joining
            funny_comments = get_user_comments_in_subreddit(user, humor_subreddit, humor_join_time, time.time())
            
            # Calculate daily activity
            days_before = (humor_join_time - depression_join_time) / 86400
            days_after = (time.time() - humor_join_time) / 86400
            
            daily_comments_before = len(before_comments) / days_before if days_before > 0 else 0
            daily_comments_after = len(after_comments) / days_after if days_after > 0 else 0
            daily_funny_comments = len(funny_comments) / days_after if days_after > 0 else 0
            
            # Append to results
            matched_user_data.append({
                'Username': user,
                'Join Date (r/depression)': datetime.utcfromtimestamp(depression_join_time),
                'Join Date (r/funny)': datetime.utcfromtimestamp(humor_join_time),
                'Daily Comments (r/depression) Before': daily_comments_before,
                'Daily Comments (r/depression) After': daily_comments_after,
                'Daily Comments (r/funny)': daily_funny_comments,
                'Comments (r/depression) Before': before_comments,
                'Comments (r/depression) After': after_comments,
                'Comments (r/funny)': funny_comments,
            })
            time.sleep(0.5)  # To avoid hitting Reddit's rate limit
    
    # Step 3: Save to Excel
    df = pd.DataFrame(matched_user_data)
    df.to_excel('user_humor_depression_activity.xlsx', index=False)
    print("Data saved to user_humor_depression_activity.xlsx")

if __name__ == '__main__':
    main()
