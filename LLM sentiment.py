import openai
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar

from secret import api_key  # Import the API key from secret.py


# Load your data
df = pd.read_excel("filtered_depression_comments_and_posts.xlsx")
comments = df['Text'].head(10).tolist()  # Limit to first 10 comments

# OpenAI API setup
openai.api_key = api_key  # Replace with your actual API key

# Function to label a comment
def label_comment(comment):
    prompt = f"""
    You are an advanced language model trained to analyze emotional tones in comments. Your task is to evaluate each comment based on two attributes:

    1. **Signs of depression or sadness**: Focus on whether the speaker indicates any real signs of depression or sadness of their own. Look for language that reflects feelings of hopelessness, helplessness, despair, or deep emotional pain.
    - **Do not rate comments that express mild frustration, confusion, or questioning as depressive** unless they clearly communicate feelings of despair or hopelessness. For example, asking a series of questions or expressing doubt about something does not necessarily indicate sadness or depression.
    - **Do not rate exaggerated statements or sarcasm as depressive** unless they contain clear indicators of emotional distress. For example, humor or sarcasm used for exaggeration should not be interpreted as depression unless there is an underlying tone of hopelessness or despair.
    - Example of depression/sadness: "I don’t see the point in anything anymore."
    - Example of NOT depression/sadness: "I’m just trying to figure out if this makes sense."

    2. **Lack of joy or positivity**: Evaluate if the comment lacks joy, positivity, or an optimistic outlook. This could include pessimism, frustration, or negativity, but it should be based on the tone and words, not just the statement of a negative fact.
    - **Do not rate confusion, frustration, or sarcastic remarks as lacking joy** unless they indicate a deeper sense of negativity or hopelessness. For example, if someone is joking or using humor without any emotional distress, it should not be rated high on lack of joy/positivity.
    - Example of lack of joy/positivity: "Everything feels so bleak and hopeless."
    - Example of positivity: "Even though things are tough, I'm still holding on to hope."

    For each comment, provide two ratings on a scale of 0 to 3:
    - **Depression/Sadness (0 to 3)**: How much does this comment reflect real signs of depression or sadness? (0 = No signs, 3 = Very strong signs of sadness or depression)
    - **Lack of Joy/Positivity (0 to 3)**: How much does this comment reflect a lack of joy or positivity? (0 = Very joyful/positive, 3 = Completely lacking joy/positivity)

    The comment might use exaggeration, sarcasm, or questioning. **Focus on whether the comment communicates genuine emotional distress or sadness, not on frustration or confusion**.

    Comment: "{comment}"
    Response format:
    Depression/Sadness: [number between 0 and 3]
    Lack of Joy/Positivity: [number between 0 and 3]
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
        if "Depression/Sadness" not in result or "Lack of Joy/Positivity" not in result:
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
