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
    You are an advanced language model trained to analyze emotional tones in comments. Your task is to evaluate each comment based on two attributes:

    1. **Signs of depression or sadness**: Determine whether the comment contains clear indications of depression or sadness.  
    - **Rate as 1 (depressed/sad)** if the comment reflects hopelessness, despair, deep emotional pain, or sadness.  
    - **Rate as 0 (not depressed/sad)** if the comment does not show these signs, even if it expresses mild frustration, sarcasm, questioning, or confusion without underlying despair.  
    - Example of depression/sadness: "I don’t see the point in anything anymore."  
    - Example of NOT depression/sadness: "I’m just trying to figure out if this makes sense."

    2. **Emotional Well-being**: Assess the emotional well-being expressed in the comment.  
    - **Rate as 1 (poor emotional well-being)** if the comment reflects negativity, pessimism, or emotional distress.  
    - **Rate as 0 (good emotional well-being)** if the comment is neutral, positive, stable, humorous, sarcastic, or questioning without emotional distress.  
    - Example of poor emotional well-being: "Everything feels so bleak and hopeless."  
    - Example of neutral or positive emotional well-being: "Even though things are tough, I'm still holding on to hope."  

    **Important Notes:**  
    - **Sarcasm or humor** should generally score 0 for both attributes unless there are clear indications of sadness or emotional distress.  
    - **Neutral comments** (e.g., asking questions or expressing mild frustration) should also score 0 for both attributes.

    For each comment, provide two ratings:  
    - **Depression/Sadness**: 0 = Not depressed, 1 = Depressed  
    - **Emotional Well-being**: 0 = Good well-being, 1 = Poor well-being  

    Comment: "{comment}"  
    Response format:  
    Depression/Sadness: [0 or 1]  
    Emotional Well-being: [0 or 1]  
    """



    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Correct model name
            messages=[
                {"role": "system", "content": "You are an advanced language model trained to analyze emotional tones in comments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.0
        )

        # Extract the response
        result = response['choices'][0]['message']['content'].strip()

        # Handle the case where the response format is not as expected
        if "Depression/Sadness" not in result or "Emotional Well-being" not in result:
            return f"Unexpected response format: {result}"

        dep, well_being = result.split('\n')
        dep_score = int(dep.split(":")[1].strip())
        well_being_score = int(well_being.split(":")[1].strip())
        return dep_score, well_being_score

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
output_df = pd.DataFrame(results, columns=["comment", "depression_score", "emotional_well_being_score"])
output_df.to_csv("labeled_comments.csv", index=False)
