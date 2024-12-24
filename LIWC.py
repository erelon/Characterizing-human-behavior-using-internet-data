from empath import Empath
import pandas as pd

# Load your data
file_name = "final.xlsx"  # Replace with your file name
data = pd.read_excel(file_name)

# Initialize Empath
lexicon = Empath()

# Define a function to analyze text
def analyze_text_with_empath(text):
    if pd.isna(text):  # Handle missing values
        return {}
    return lexicon.analyze(text, categories=["positive_emotion", "negative_emotion"])

# Apply the function to the "Text" column
analysis_results = data["Text"].apply(analyze_text_with_empath)

# Convert results to DataFrame
empath_df = pd.DataFrame(analysis_results.tolist())
data_with_empath = pd.concat([data, empath_df], axis=1)

# Save the results to a new Excel file
output_file = "data_with_empath_scores.xlsx"
data_with_empath.to_excel(output_file, index=False)

print(f"Empath analysis complete! Results saved to {output_file}.")
