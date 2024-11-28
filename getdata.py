import praw
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import time

from secret import secret

# Initialize Reddit API client
reddit = praw.Reddit(**secret)

# Step 1: Read the list of users from the Excel file
df_users = pd.read_excel("users.xlsx")  # Load the Excel file
usernames = df_users.iloc[:, 0].tolist()  # Assuming usernames are in the first column

# Initialize a list to store the fetched data
comments_data = []

# Step 2: Fetch all comments and posts for each user
for user in tqdm(usernames, desc="Fetching posts/comments"):
    try:
        user_data = reddit.redditor(user)

         # Fetch the user's comments
        for comment in user_data.comments.new(limit=None):
            comments_data.append([comment.author.name if comment.author else "deleted",
                                    comment.body,
                                    comment.created_utc,
                                    comment.subreddit.display_name,
                                    'comment',
                                    f"https://www.reddit.com{comment.permalink}"])  # Add the comment link

        # Fetch the user's posts
        for post in user_data.submissions.new(limit=None):
            comments_data.append([post.author.name if post.author else "deleted",
                                    post.title,
                                    post.created_utc,
                                    post.subreddit.display_name,
                                    'post',
                                    post.url])  # Add the post URL

        # Optional: Sleep for a second to prevent hitting Reddit's rate limit
        time.sleep(1)

    except Exception as e:
        print(f"Error fetching data for {user}: {e}")

# Step 3: Convert the collected data into a DataFrame
df = pd.DataFrame(comments_data, columns=["Username", "Text", "Date", "Subreddit", "Type", "Link"])

# Convert the 'Date' column to a readable format
df['Date'] = pd.to_datetime(df['Date'], unit='s')

# Step 4: Save the data to Excel
df.to_excel("user_comments_and_posts.xlsx", index=False)

print("Data saved to user_comments_and_posts.xlsx")