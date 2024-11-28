import pandas as pd
from tqdm import tqdm

# Define keywords related to depression
depression_keywords = [
    "depression", "depressed", "depressive", "depressing", "sad", "sadness", "sorrow", "lonely", "loneliness",
    "hopeless", "despair", "unmotivated", "low energy", "fatigue", "tired", "down", "blue",
    "unwell", "anxiety", "panic", "nervous", "panic attack", "overwhelmed", "stressed",
    "pressure", "loss of interest", "no motivation", "crying", "tears", "emotional", "self-harm",
    "suicidal", "hopelessness", "worthless", "helpless", "empty", "numb", "isolated", "alone",
    "abandoned", "shame", "guilt", "frustration", "therapy", "psychiatrist", "antidepressant",
    "medication", "mental health", "counselor", "therapy session", "coping", "self-care", "mindfulness"
]

# Function to check if the comment or post contains any of the depression keywords
def contains_depression_keywords(text, keywords):
    # Convert text to lowercase for case-insensitive comparison
    text_words = set(text.lower().split())  # Split text into unique words
    return any(keyword.lower() in text_words for keyword in keywords)

# Load the Excel file containing the posts/comments data
df = pd.read_excel("user_comments_and_posts.xlsx")

# Step 1: Use tqdm to show a progress bar for the filtering process
tqdm.pandas(desc="Filtering posts/comments with depression keywords")

# Step 2: Filter comments and posts based on keywords
df_filtered = df[df['Text'].progress_apply(lambda x: contains_depression_keywords(str(x), depression_keywords))]

# Step 3: Save the filtered data to a new Excel file
df_filtered.to_excel("filtered_depression_comments_and_posts.xlsx", index=False)

print(f"Filtered data saved to filtered_depression_comments_and_posts.xlsx")
