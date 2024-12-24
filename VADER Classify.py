import pandas as pd

# Load your dataset
file_name = "data_with_sentiment_scores.xlsx"  # Replace with your file name
data = pd.read_excel(file_name)

# Classify texts into positive, neutral, or negative
def classify_sentiment(compound):
    if compound > 0.05:
        return 'positive'
    elif compound < -0.05:
        return 'negative'
    else:
        return 'neutral'

# Apply classification based on the compound score
data['sentiment_category'] = data['compound'].apply(classify_sentiment)

# Calculate proportions of each sentiment category
total_texts = len(data)
proportions = data['sentiment_category'].value_counts(normalize=True)  # Normalize=True gives proportions

# Save the updated data with sentiment categories
output_file = "sentiment_classification_results.xlsx"
data.to_excel(output_file, index=False)

# Print the proportions
print("Proportions of Sentiment Categories:")
print(proportions)

print(f"Sentiment classification results saved to {output_file}.")
