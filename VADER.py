import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tqdm

# Load the Excel file
file_name = "final.xlsx"  # Replace with your file name
data = pd.read_excel(file_name)

# Initialize the VADER Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Define a function to compute sentiment scores
def compute_sentiment(text):
    if pd.isna(text):  # Handle missing values
        return {"pos": None, "neu": None, "neg": None, "compound": None}
    scores = analyzer.polarity_scores(text)
    return scores

# Apply the function to the "Text" column with tqdm
tqdm.pandas(desc="Computing Sentiment Scores")  # Initialize tqdm
sentiment_scores = data["Text"].progress_apply(compute_sentiment)

# Convert sentiment scores to separate columns
scores_df = pd.DataFrame(sentiment_scores.tolist())
data_with_scores = pd.concat([data, scores_df], axis=1)

# Save the results to a new Excel file
output_file = "data_with_sentiment_scores.xlsx"
data_with_scores.to_excel(output_file, index=False)

print(f"Sentiment analysis complete! Results saved to {output_file}.")
