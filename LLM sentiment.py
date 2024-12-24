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
    You are an advanced language model trained to analyze emotional tones in comments. Your task is to evaluate each comment based on two attributes on a scale from 0 to 5:

    1. **Signs of depression or sadness**: Determine whether the comment contains clear indications of depression or sadness.  
    - **Rate from 0 to 5** where:  
      - 0 = No signs of depression/sadness.  
      - 5 = Extremely clear signs of depression/sadness.  
    - Example of 5: "I don’t see the point in anything anymore."  
    - Example of 0: "I’m just trying to figure out if this makes sense."

    2. **Emotional Well-being**: Assess the emotional well-being expressed in the comment.  
    - **Rate from 0 to 5** where:  
      - 0 = Extremely positive or neutral emotional well-being.  
      - 5 = Extremely poor emotional well-being.  
    - Example of 5: "Everything feels so bleak and hopeless."  
    - Example of 0: "Even though things are tough, I'm still holding on to hope."  

    **Important Notes:**  
    - Sarcasm or depression should generally score 0 for both attributes unless there are clear indications of sadness or emotional distress.  
    - Neutral comments (e.g., asking questions or expressing mild frustration) should also score near 0 for both attributes.

    For each comment, provide two ratings:  
    - **Depression/Sadness**: 0 to 5  
    - **Emotional Well-being**: 0 to 5  

    Comment: "{comment}"  
    Response format:  
    Depression/Sadness: [0 to 5]  
    Emotional Well-being: [0 to 5]  
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
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

        depression, well_being = result.split('\n')
        depression_score = int(depression.split(":")[1].strip())
        well_being_score = int(well_being.split(":")[1].strip())
        return depression_score, well_being_score

    except Exception as e:
        return f"Error processing comment: {e}"

# Batch process comments with tqdm progress bar
results = []
for comment in tqdm(comments, desc="Processing comments"):  # Add tqdm here
    result = label_comment(comment)
    if isinstance(result, tuple):  # If it's a valid tuple
        results.append((comment, result[0], result[1]))
    else:  # If it's an error message
        print(f"Error processing comment: {result}")  # Output the error for debugging purposes
        results.append((comment, None, None))

# Save results to a CSV
output_df = pd.DataFrame(results, columns=["comment", "depression score", "well_being score"])
output_df.to_csv("labeled_comments2.csv", index=False)
