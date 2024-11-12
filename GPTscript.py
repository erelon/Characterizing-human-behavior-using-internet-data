import praw
from collections import defaultdict
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
from secret import secret  # Ensure secret.py has your Reddit API credentials

# Initialize Reddit API client
reddit = praw.Reddit(**secret)

# Subreddits as constants
DEPRESSION_SUBREDDIT = 'depression'
HUMOR_SUBREDDIT = 'funny'

# Rate limiting constants
SUBMISSION_DELAY = 0.001  # seconds between submissions
COMMENT_DELAY = 0.0001     # seconds between comment operations
MAX_RETRIES = 3       # maximum number of retries for rate-limited operations

def wait_with_backoff(retry_count):
    """Implement exponential backoff"""
    wait_time = min(30, 2 ** retry_count)  # Cap at 30 seconds
    time.sleep(wait_time)

def get_user_join_date(username):
    for retry in range(MAX_RETRIES):
        try:
            user = reddit.redditor(username)
            return datetime.utcfromtimestamp(user.created_utc)
        except Exception as e:
            if '429' in str(e):
                print(f"Rate limited while fetching join date, retrying... ({retry + 1}/{MAX_RETRIES})")
                wait_with_backoff(retry)
            else:
                print(f"Error fetching join date for {username}: {e}")
                return None
    return None

def collect_depression_data(limit=100):
    depression_users = defaultdict(lambda: {'join_date': None, 'posts': 0, 'comments': 0, 'comment_texts': []})
    subreddit = reddit.subreddit(DEPRESSION_SUBREDDIT)
    
    print("Collecting users from r/depression...")
    submissions_processed = 0
    
    while submissions_processed < limit:
        try:
            for submission in tqdm(subreddit.new(limit=limit), desc="Fetching r/depression users"):
                if submission.author:
                    user = submission.author.name
                    depression_users[user]['posts'] += 1
                    if not depression_users[user]['join_date']:
                        depression_users[user]['join_date'] = get_user_join_date(user)
                        time.sleep(COMMENT_DELAY)

                try:
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        if comment.author:
                            user = comment.author.name
                            depression_users[user]['comments'] += 1
                            if not depression_users[user]['join_date']:
                                depression_users[user]['join_date'] = get_user_join_date(user)
                            depression_users[user]['comment_texts'].append({
                                'text': comment.body,
                                'created_utc': comment.created_utc
                            })
                            time.sleep(COMMENT_DELAY)
                except Exception as e:
                    print(f"Error processing comments for submission: {e}")
                    continue

                submissions_processed += 1
                time.sleep(SUBMISSION_DELAY)

                if submissions_processed >= limit:
                    break

            return depression_users

        except Exception as e:
            if '429' in str(e):
                print("Rate limited while fetching submissions, waiting before retry...")
                wait_with_backoff(submissions_processed // 10)
            else:
                print(f"Error collecting depression subreddit data: {e}")
                return depression_users

def fetch_user_activity(username, subreddit_name):
    posts = []
    comments = []
    
    for retry in range(MAX_RETRIES):
        try:
            user = reddit.redditor(username)
            
            # Fetch comments
            for comment in user.comments.new(limit=None):
                if comment.subreddit.display_name.lower() == subreddit_name.lower():
                    comments.append({
                        'text': comment.body,
                        'created_utc': comment.created_utc
                    })
                time.sleep(COMMENT_DELAY)
            
            # Fetch submissions
            for submission in user.submissions.new(limit=None):
                if submission.subreddit.display_name.lower() == subreddit_name.lower():
                    posts.append({
                        'created_utc': submission.created_utc
                    })
                time.sleep(COMMENT_DELAY)
            
            return posts, comments

        except Exception as e:
            if '429' in str(e):
                print(f"Rate limited while fetching user activity, retrying... ({retry + 1}/{MAX_RETRIES})")
                wait_with_backoff(retry)
            else:
                print(f"Error in fetch_user_activity for {username}: {e}")
                return [], []
    
    return [], []

def process_user_activity(username, dep_data):
    try:
        join_depression_date = dep_data['join_date']
        depression_posts, depression_comments = fetch_user_activity(username, DEPRESSION_SUBREDDIT)
        funny_posts, funny_comments = fetch_user_activity(username, HUMOR_SUBREDDIT)
        
        # Skip if no activity in r/funny
        if not funny_posts and not funny_comments:
            return {
                'Username': username,
                'Join Date (r/depression)': join_depression_date,
                'Posts in r/depression': len(depression_posts),
                'Comments in r/depression': len(depression_comments),
                'Texts in r/depression': [c['text'] for c in depression_comments],
                'Join Date (r/funny)': None,
                'Posts in r/funny': 0,
                'Comments in r/funny': 0,
                'Texts in r/funny': []
            }
        
        # Find earliest r/funny activity
        all_funny_times = ([p['created_utc'] for p in funny_posts] + 
                          [c['created_utc'] for c in funny_comments])
        join_funny_date = min(all_funny_times) if all_funny_times else None
        
        if join_funny_date:
            # Count depression activity before and after joining r/funny
            dep_posts_before = sum(1 for p in depression_posts if p['created_utc'] < join_funny_date)
            dep_posts_after = sum(1 for p in depression_posts if p['created_utc'] >= join_funny_date)
            dep_comments_before = sum(1 for c in depression_comments if c['created_utc'] < join_funny_date)
            dep_comments_after = sum(1 for c in depression_comments if c['created_utc'] >= join_funny_date)
            
            return {
                'Username': username,
                'Join Date (r/depression)': join_depression_date,
                'Join Date (r/funny)': datetime.utcfromtimestamp(join_funny_date),
                'Posts in r/depression before joining r/funny': dep_posts_before,
                'Comments in r/depression before joining r/funny': dep_comments_before,
                'Posts in r/depression after joining r/funny': dep_posts_after,
                'Comments in r/depression after joining r/funny': dep_comments_after,
                'Posts in r/funny': len(funny_posts),
                'Comments in r/funny': len(funny_comments),
                'Texts in r/depression': [c['text'] for c in depression_comments],
                'Texts in r/funny': [c['text'] for c in funny_comments]
            }
        
    except Exception as e:
        print(f"Error processing user {username}: {e}")
    return None

def main():
    # Collect initial depression subreddit data
    depression_users = collect_depression_data(limit=1000)  # Reduced limit for testing
    user_data = []

    # Process each user
    print("\nProcessing users for r/funny activity...")
    for username, dep_data in tqdm(depression_users.items(), desc="Processing users"):
        result = process_user_activity(username, dep_data)
        if result:
            user_data.append(result)
        time.sleep(2)  # Delay between processing users

    # Save to Excel
    try:
        df = pd.DataFrame(user_data)
        df.to_excel('user_activity_depression_funny.xlsx', index=False)
        print("Data saved to user_activity_depression_funny.xlsx")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        try:
            df.to_csv('user_activity_depression_funny.csv', index=False)
            print("Backup data saved to user_activity_depression_funny.csv")
        except Exception as e:
            print(f"Error saving backup data: {e}")

if __name__ == '__main__':
    main()
