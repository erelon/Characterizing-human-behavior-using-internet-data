import openai
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar

from secret import api_key  # Import the API key from secret.py

# Load your data
df = pd.read_excel("filtered_depression_comments_and_posts.xlsx")
comments = df['Text'].tolist()  # Include all comments

# OpenAI API setup
openai.api_key = api_key  # Replace with your actual API key

# Function to label a comment
def label_comment(comment):
    prompt = f"""
    You are an advanced language model trained to analyze humor in comments. Your task is to evaluate comments based on two attributes related to humor:

    1. **Humor Intent**: Does the comment attempt to be humorous through jokes, puns, playful exaggerations, or other forms of comedic intent?  
       - **Rate on a scale of 0 to 5**:
         - 0: No humor intent at all
         - 1: Minimal or unclear humor intent
         - 2: Slight humor intent
         - 3: Moderate humor intent
         - 4: Strong humor intent
         - 5: Very clear and deliberate humor intent  
       - Examples:
         - 5: "Why don’t skeletons fight each other? They don’t have the guts."
         - 0: "I went to the store and bought some milk."

    2. **Commenter's Amusement**: Is the commenter genuinely entertained, expressing joy or laughter? Look for explicit signs like "haha," "lol," or playful acknowledgment of humor.  
       - **Rate on a scale of 0 to 5**:
         - 0: No amusement or enjoyment expressed
         - 1: Minimal or unclear amusement
         - 2: Slight amusement
         - 3: Moderate amusement
         - 4: Strong amusement
         - 5: Very clear amusement, such as "LOL, I can't stop laughing!"  
       - Examples:
         - 5: "Haha, that's hilarious!"  
         - 0: "This makes no sense to me."

    Comment: "{comment}"  
    Response format:  
    Humor Intent: [0–5]  
    Commenter's Amusement: [0–5]  
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an advanced language model trained to analyze humor in comments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.0
        )

        # Extract the response
        result = response['choices'][0]['message']['content'].strip()

        # Ensure the response contains both attributes
        if "Humor Intent" in result and "Commenter's Amusement" in result:
            # Parse the scores
            lines = result.split('\n')
            humor_score = int(lines[0].split(":")[1].strip())
            amusement_score = int(lines[1].split(":")[1].strip())
            return humor_score, amusement_score
        else:
            return f"Unexpected response format: {result}"

    except Exception as e:
        return f"Error processing comment: {e}"

# Batch process comments with tqdm progress bar
results = []
for comment in tqdm(comments, desc="Processing comments"):
    result = label_comment(comment)
    if isinstance(result, tuple):  # If it's a valid tuple
        results.append((comment, result[0], result[1]))
    else:  # If it's an error message
        print(f"Error processing comment: {result}")
        results.append((comment, None, None))

# Save results to a CSV
output_df = pd.DataFrame(results, columns=["comment", "Humor Intent", "Commenter's Amusement"])
output_df.to_csv("labeled_humor.csv", index=False)
