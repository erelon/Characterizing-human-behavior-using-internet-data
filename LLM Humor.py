import openai
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar

from secret import api_key  # Import the API key from secret.py



# Load your data
df = pd.read_excel("filtered_depression_comments_and_posts.xlsx")
comments = df['Text'].head(100).tolist()  # Limit to first 10 comments

# OpenAI API setup
openai.api_key = api_key  # Replace with your actual API key

# Function to label a comment
def label_comment(comment):
    prompt = f"""
    You are an advanced language model trained to analyze humor in comments. Your task is to evaluate comments based on two attributes related to humor:

    1. **Humor Intent**: Does the comment attempt to be humorous through jokes, puns, playful exaggerations, or other forms of comedic intent?  
    - **Rate as 1 (humorous intent)** if the comment clearly tries to be funny or comedic.  
    - **Rate as 0 (no humorous intent)** if the comment does not show any effort to amuse.  
    - Examples of humorous intent: "Why don’t skeletons fight each other? They don’t have the guts." or "I told my computer I needed a break, and now it won't stop sending me coffee memes."  
    - Examples of no humorous intent: "I went to the store and bought some milk." or "Can someone explain how this works?"

    2. **Commenter's Amusement**: Does the comment suggest that the commenter themselves is entertained, amused, or laughing?  
    - **Rate as 1 (entertained)** if the comment shows clear expressions of amusement (e.g., "lol," "haha," or playful acknowledgment of humor).  
    - **Rate as 0 (not entertained)** if the comment does not indicate any enjoyment or laughter.  
    - Examples of entertained commenters: "Haha, that's hilarious!" or "LOL, I can't stop laughing."  
    - Examples of not entertained commenters: "I don't find this funny." or "This makes no sense to me."

    ### Guidelines:
    - **Focus on clear intent or emotional tone**: For humor intent, evaluate whether the comment is designed to amuse. For commenter amusement, assess whether the comment expresses enjoyment or laughter, even if the humor is external to the comment itself.
    - Distinguish between failed humor attempts and successful self-amusement.

    For each comment, provide two ratings:
    - **Humor Intent**: 0 = No humor intent, 1 = Clear humor intent  
    - **Commenter's Amusement**: 0 = Not entertained, 1 = Clearly entertained  

    Comment: "{comment}"  
    Response format:  
    Humor Intent: [0 or 1]  
    Commenter's Amusement: [0 or 1]  
    """





    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Correct model name
            messages=[
                {"role": "system", "content": "You are an advanced language model trained to analyze humor in comments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.0
        )

        # Extract the response
        result = response['choices'][0]['message']['content'].strip()

        # Handle the case where the response format is not as expected
        if "Humor Intent" not in result or "Commenter's Amusement" not in result:
            return f"Unexpected response format: {result}"

        humor, amusment = result.split('\n')
        humor_score = int(humor.split(":")[1].strip())
        amusment_score = int(amusment.split(":")[1].strip())
        return humor_score, amusment_score

    except Exception as e:
        return f"Error processing comment: {e}"

# Batch process comments with tqdm progress bar
results = []
for comment in tqdm(comments, desc="Processing comments"):  # Add tqdm here
    result = label_comment(comment)
    if isinstance(result, tuple):  # If it's a valid tuple (depression, emotional well-being score)
        results.append((comment, result[0], result[1]))
    else:  # If it's an error message
        print(f"Error processing comment: {result}")  # Output the error for debugging purposes
        results.append((comment, None, None))

# Save results to a CSV
output_df = pd.DataFrame(results, columns=["comment", "Humor_intent", "Commenter's Amusement"])
output_df.to_csv("labeled_comments2.csv", index=False)
