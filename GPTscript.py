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

def get_user_join_date(username):
    try:
        user = reddit.redditor(username)
        return datetime.utcfromtimestamp(user.created_utc)
    except Exception as e:
        print(f"Error fetching join date for {username}: {e}")
        return None

def fetch_user_activity(username, subreddit_name):
    try:
        user = reddit.redditor(username)
        posts, comments = 0, 0
        comment_texts = []
        
        # Use try-except for each iteration to handle potential errors
        try:
            for comment in user.comments.new(limit=None):
                if comment.subreddit.display_name.lower() == subreddit_name.lower():
                    comments += 1
                    comment_texts.append({
                        'text': comment.body,
                        'created_utc': comment.created_utc
                    })
        except Exception as e:
            print(f"Error fetching comments for {username}: {e}")

        try:
            for submission in user.submissions.new(limit=None):
                if submission.subreddit.display_name.lower() == subreddit_name.lower():
                    posts += 1
        except Exception as e:
            print(f"Error fetching submissions for {username}: {e}")

        return posts, comments, comment_texts
    except Exception as e:
        print(f"Error in fetch_user_activity for {username}: {e}")
        return 0, 0, []

def process_user_activity(username, dep_data, humor_subreddit):
    try:
        join_depression_date = dep_data['join_date']
        posts_depression, comments_depression, texts_depression = fetch_user_activity(
            username, DEPRESSION_SUBREDDIT)
        
        # Check activity in r/funny
        try:
            user = reddit.redditor(username)
            is_in_funny = False
            join_funny_date = None
            
            # Check comments first
            for comment in user.comments.new(limit=100):  # Limit added to prevent excessive API calls
                if comment.subreddit.display_name.lower() == humor_subreddit.lower():
                    is_in_funny = True
                    if join_funny_date is None or comment.created_utc < join_funny_date:
                        join_funny_date = comment.created_utc
                    
            if not is_in_funny:
                # Check submissions if no comments found
                for submission in user.submissions.new(limit=100):
                    if submission.subreddit.display_name.lower() == humor_subreddit.lower():
                        is_in_funny = True
                        if join_funny_date is None or submission.created_utc < join_funny_date:
                            join_funny_date = submission.created_utc
                        break
                        
        except Exception as e:
            print(f"Error checking r/funny activity for {username}: {e}")
            return None

        # If user is not active in r/funny, return basic data
        if not is_in_funny:
            return {
                'Username': username,
                'Join Date (r/depression)': join_depression_date,
                'Posts in r/depression': posts_depression,
                'Comments in r/depression': comments_depression,
                'Texts in r/depression': [t['text'] for t in texts_depression],
                'Join Date (r/funny)': None,
                'Posts in r/funny': 0,
                'Comments in r/funny': 0,
                'Texts in r/funny': []
            }

        # Fetch r/funny activity
        posts_funny, comments_funny, texts_funny = fetch_user_activity(username, humor_subreddit)

        # Calculate activity before and after joining r/funny
        dep_posts_before = dep_posts_after = dep_comments_before = dep_comments_after = 0

        if join_funny_date and texts_depression:
            for text in texts_depression:
                if text['created_utc'] < join_funny_date:
                    dep_comments_before += 1
                else:
                    dep_comments_after += 1

        return {
            'Username': username,
            'Join Date (r/depression)': join_depression_date,
            'Join Date (r/funny)': datetime.utcfromtimestamp(join_funny_date) if join_funny_date else None,
            'Posts in r/depression before joining r/funny': dep_posts_before,
            'Comments in r/depression before joining r/funny': dep_comments_before,
            'Posts in r/depression after joining r/funny': dep_posts_after,
            'Comments in r/depression after joining r/funny': dep_comments_after,
            'Posts in r/funny': posts_funny,
            'Comments in r/funny': comments_funny,
            'Texts in r/depression': [t['text'] for t in texts_depression],
            'Texts in r/funny': [t['text'] for t in texts_funny]
        }
    except Exception as e:
        print(f"Error processing user {username}: {e}")
        return None

def main():
    # Define DataFrame to store user data
    user_data = []
    depression_users = defaultdict(lambda: {'join_date': None, 'posts': 0, 'comments': 0, 'comment_texts': []})

    # Collect users from r/depression
    print("Collecting users from r/depression...")
    try:
        subreddit = reddit.subreddit(DEPRESSION_SUBREDDIT)
        for submission in tqdm(subreddit.new(limit=1000), desc="Fetching r/depression users"):
            if submission.author:
                user = submission.author.name
                depression_users[user]['posts'] += 1
                depression_users[user]['join_date'] = get_user_join_date(user)

            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                if comment.author:
                    user = comment.author.name
                    depression_users[user]['comments'] += 1
                    depression_users[user]['join_date'] = get_user_join_date(user)
                    depression_users[user]['comment_texts'].append({
                        'text': comment.body,
                        'created_utc': comment.created_utc
                    })
    except Exception as e:
        print(f"Error collecting depression subreddit data: {e}")
        return

    # Process each user
    print("Processing users for r/funny activity...")
    for username, dep_data in tqdm(depression_users.items(), desc="Processing users"):
        user_result = process_user_activity(username, dep_data, HUMOR_SUBREDDIT)
        if user_result:
            user_data.append(user_result)

        # Add delay to avoid rate limiting
        time.sleep(0.5)

    # Save to Excel
    try:
        df = pd.DataFrame(user_data)
        df.to_excel('user_activity_depression_funny.xlsx', index=False)
        print("Data saved to user_activity_depression_funny.xlsx")
    except Exception as e:
        print(f"Error saving data to Excel: {e}")
        # Backup save as CSV
        try:
            df.to_csv('user_activity_depression_funny.csv', index=False)
            print("Backup data saved to user_activity_depression_funny.csv")
        except Exception as e:
            print(f"Error saving backup data: {e}")

if __name__ == '__main__':
    main()
