import json
import pandas as pd
import tqdm

if __name__ == '__main__':
    with open("cleaned_data.json", "r") as file:
        data = json.load(file)

    processed_data = []
    for user in tqdm.tqdm(data, desc="Processing users"):
        """
        For every user keep:
        -  count the number of posts per reddit
        """
        user_data = data[user]
        if "funny" not in user_data:
            user_data["funny"] = []
        if "depression" not in user_data:
            user_data["depression"] = []
        count_funny = len(user_data["funny"])
        count_depression = len(user_data["depression"])

        processed_data.append({"user": user,
                               "count_funny": count_funny,
                               "count_depression": count_depression,
                               })

    df = pd.DataFrame(processed_data)

    df.to_csv("user_activity.csv", index=False)
