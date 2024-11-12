import json
import pandas as pd
import tqdm

if __name__ == '__main__':
    with open("cleaned_data.json", "r") as file:
        data = json.load(file)

    df = pd.DataFrame()

    i = 0
    for user in tqdm.tqdm(data, desc="Processing users"):
        """
        For every user keep:
        -  count the number of posts per reddit
        -  first post in each subreddit
        -  Add flag to people with first post in depression:
        -       See if they are posting more in funny as time goes on (list per month for depression and funny)
        """
        user_data = data[user]
        if "funny" not in user_data:
            user_data["funny"] = []
        if "depression" not in user_data:
            user_data["depression"] = []
        count_funny = len(user_data["funny"])
        count_depression = len(user_data["depression"])
        first_funny = min([post["created_utc"] for post in user_data["funny"]]) if count_funny > 0 else None
        first_depression = min(
            [post["created_utc"] for post in user_data["depression"]]) if count_depression > 0 else None
        flag = 1 if first_depression and first_funny and first_depression < first_funny else 0

        # count per month for each subreddit
        if count_funny > 0:
            # order by time
            user_data["funny"].sort(key=lambda x: x["created_utc"])
            # bin all times into months
            bins = {}
            for post in user_data["funny"]:
                month = pd.to_datetime(post["created_utc"], unit="s").to_period("M")
                bins[month] = bins.get(month, 0) + 1
        else:
            bins = {}
        funny_bins = bins

        if count_depression > 0:
            # order by time
            user_data["depression"].sort(key=lambda x: x["created_utc"])
            # bin all times into months
            bins = {}
            for post in user_data["depression"]:
                month = pd.to_datetime(post["created_utc"], unit="s").to_period("M")
                bins[month] = bins.get(month, 0) + 1
        else:
            bins = {}
        depression_bins = bins

        df = df._append({"user": user,
                         "count_funny": count_funny,
                         "count_depression": count_depression,
                         "first_funny": pd.to_datetime(first_funny, unit="s") if first_funny else 0,
                         "first_depression": pd.to_datetime(first_depression, unit="s") if first_depression else 0,
                         "flag": flag,
                         "funny_bins": funny_bins,
                         "depression_bins": depression_bins}, ignore_index=True)

    df.to_csv("user_activity.csv", index=False)
