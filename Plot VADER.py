import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load the data with sentiment scores
file_name = "data_with_sentiment_scores.xlsx"  # Replace with your actual file name
data = pd.read_excel(file_name)

# Configure the visualization
plt.rcParams['font.size'] = 16

# Create subplots
fig, axs = plt.subplots(1, 4, figsize=(22, 5), sharey=True)

# Set y-limit for uniformity
plt.ylim(0, 40)
axs[0].set_ylabel('Number of texts')

# Plot histograms for each sentiment score
sns.histplot(data=data, x="neg", color='r', bins=20, ax=axs[0])
sns.histplot(data=data, x="neu", color='grey', bins=20, ax=axs[1])
sns.histplot(data=data, x="pos", color='g', bins=20, ax=axs[2])
sns.histplot(data=data, x="compound", bins=20, ax=axs[3])

# Customize axes labels
axs[0].set(xlim=(0, 1), xlabel="Negative")
axs[1].set(xlim=(0, 1), xlabel="Neutral")
axs[2].set(xlim=(0, 1), xlabel="Positive")
axs[3].set(xlim=(-1, 1), xlabel="Compound")

# Show the plot
plt.tight_layout()
plt.show()
