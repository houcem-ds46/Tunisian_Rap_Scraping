import pandas as pd
from datetime import datetime
import numpy as np
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError




def get_channel_info(id):

    youtube = build("youtube", "v3", developerKey=os.environ.get("API_KEY"))
    request = youtube.channels().list(
        id=id,
        part="snippet,contentDetails,statistics",
        # categoryId="UCV9x1Bo83ByXbqJga1ZxaJg",
        # forUsername="@TRIPPYBOYZ"
    )

    response = request.execute()
    # print(response)
    result_dict = dict()
    result_dict["title"] = [response["items"][0]["snippet"]["title"]]
    result_dict["viewCount"] = [response["items"][0]["statistics"]["viewCount"]]
    result_dict["subscriberCount"] = [response["items"][0]["statistics"]["subscriberCount"]]
    result_dict["videoCount"] = [response["items"][0]["statistics"]["videoCount"]]
    result_dict["createdAt"] = [response["items"][0]["snippet"]["publishedAt"]]

    return pd.DataFrame.from_dict(result_dict)


def get_latest_video_url(id):
    try:
        youtube = build("youtube", "v3", developerKey=os.environ.get("API_KEY"))
        request = youtube.channels().list(
        id=id,
        part='contentDetails'
    ).execute()
        playlist_id = request['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve the latest video from the playlist
        playlistitems_response = youtube.playlistItems().list(
            playlistId=playlist_id,
            part='snippet',
            maxResults=1
        ).execute()

        latest_video_id = playlistitems_response['items'][0]['snippet']['resourceId']['videoId']
        video_url = f'https://www.youtube.com/watch?v={latest_video_id}'
        return video_url
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        return ""


def post_process(df_input):
    df = df_input.pipe(lambda x: x[x["videoCount"].astype(int) > 0]).reset_index(drop=True)
    df["createdAt"] = df["createdAt"].apply(lambda x: x[:10])
    df["AverageViewsPerVideo"] = df["viewCount"].astype(np.int64) / df["videoCount"].astype(np.int64)
    df["AverageViewsPerVideo"] = df["AverageViewsPerVideo"].astype(np.int64)
    df["viewCount"] = df["viewCount"].astype(np.int64)
    df["subscriberCount"] = df["subscriberCount"].astype(np.int64)
    df["videoCount"] = df["videoCount"].astype(np.int64)
    df["YearsSinceCreation"] = df["createdAt"].apply(udf_date_diff)
    df["CustomClusterNbOfViews"] = df["viewCount"].apply(udf_cluster)
    return df


def get_channel_cover_image(channel_id):
    youtube = build("youtube", "v3", developerKey=os.environ.get("API_KEY"))
    request = youtube.channels().list(
        part='snippet',
        id=channel_id
    )
    response = request.execute()

    if response['items']:
        channel_info = response['items'][0]
        cover_image_url = channel_info['snippet']['thumbnails']['high']['url']
        return cover_image_url
    else:
        return None


def udf_date_diff(x):
    start_date = datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), 00, 00)
    end_date = datetime.today() #.strftime('%Y-%m-%d') #datetime(2023, 4, 23, 00, 00)
    difference = end_date - start_date
    difference_in_years = (difference.days + difference.seconds / 86400) / 365.2425
    return round(difference_in_years, 2)


def convert_to_embed(url):
    # Function to convert Youtube_url to Youtube_url_embed format
    if len(url) > 1:
        video_id = url.split('v=')[1]
        return f'https://www.youtube.com/embed/{video_id}'
    else:
        return ""

def udf_cluster(x):
    if x > 1_000_000_000:
        return "1-Super Star (reached 1 B views)"
    elif x > 500_000_000:
        return "2-Rising Star (reached 500 M views)"
    elif x > 100_000_000:
        return "3-Confirmed artist (reached 100 M views)"
    elif x > 50_000_000:
        return "4-Very popular (reached 50 M views)"
    elif x > 1_000_000:
        return "5-Popular (reached 1 M views)"
    else:
        return "6-Amateur (less than 1 M views)"


def retrieve_youtube_information(df):
    # Keep only artists flaged with keep = 1
    length_before = len(df)
    df = df[df["Keep"].astype(int) == 1].reset_index(drop=True)
    length_after = len(df)
    print("length_before : ", length_before, " | length_after: ", length_after)

    # Loop over every youtube channel and retrieve usefull data
    df_tmp = []
    for _, row in df.iterrows():
        id = row["YoutubeChannel"]
        name = row["Artist"]
        print(name, "...")
        id_cleaned = id.replace("https://www.youtube.com/channel/", "")
        df_id = get_channel_info(id_cleaned)
        df_id["YoutubeChannel"] = id
        df_id["LastestVideoUrl"] = get_latest_video_url(id_cleaned)
        df_id["LastestVideoUrlEmbeded"] = df_id['LastestVideoUrl'].apply(lambda x: convert_to_embed(x))

        df_id["CoverImageUrl"] = get_channel_cover_image(id_cleaned)
        df_tmp.append(df_id)

    df_result = pd.concat(df_tmp).reset_index(drop=True)
    df_result = post_process(df_result)
    df_result["ScrapingDate"] = datetime.now().date()
    df_result["ScrapingTimestamp"] = datetime.now()
    df_result["isLastScraping"] = True

    return df_result


def concatenate_with_previous_results(df):
    if os.environ.get("LOCAL_EXECUTION") == "False":
        from google.colab import auth
        import gspread
        from google.auth import default
        # Autenticating to google
        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)
        # Defining my worksheet
        worksheet = gc.open_by_key(os.environ.get("MY_GOOGLE_SHEET_ID")).worksheet('output_new')

        # Get_all_values gives a list of rows
        rows = worksheet.get_all_values()

        # Convert to a DataFrame
        df_output_old = pd.DataFrame(rows[1:], columns=rows[0])
    else:
        df_output_old = pd.read_csv(r'output_data\output_tmp.csv')

    # Drop isLastScraping
    if "isLastScraping" in df_output_old.columns:
        df_output_old = df_output_old.drop(columns=["isLastScraping"])

    # Concatenate old result with new dataframe
    df_final = (
        pd.concat(
            [df_output_old, df]
        )
        .sort_values(["title"])
        .reset_index(drop=True)
    )

    # Convert datetime-like objects to strings
    df_final['ScrapingDate'] = pd.to_datetime(df_final['ScrapingDate']).dt.date.astype(str)
    df_final['createdAt'] = pd.to_datetime(df_final['createdAt']).dt.date.astype(str)
    df_final['ScrapingTimestamp'] = pd.to_datetime(df_final['ScrapingTimestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    df_final['viewCount'] = df_final['viewCount'].astype(int)
    df_final['subscriberCount'] = df_final['subscriberCount'].astype(int)
    df_final['videoCount'] = df_final['videoCount'].astype(int)
    df_final['AverageViewsPerVideo'] = df_final['AverageViewsPerVideo'].astype(int)

    df_final['YearsSinceCreation'] = df_final['YearsSinceCreation'].astype(str).str.replace(',', '.').astype(float)

    # fill nan with empty string
    df_final["CoverImageUrl"] = df_final["CoverImageUrl"].fillna("")
    df_final["LastestVideoUrlEmbeded"] = df_final["LastestVideoUrlEmbeded"].fillna("")
    df_final["isLastScraping"] = df_final["isLastScraping"].fillna(False)

    return df_final


def add_flag_for_new_videos_released_since_last_scraping(df):
    # Add new column to flag new clips released since the last scraping date
    df['ScrapingDate_converted'] = pd.to_datetime(df['ScrapingDate'])
    df = df.sort_values(by=['title', 'ScrapingDate_converted'], ascending=[True, True])
    df['LatestVideoUrl_previous'] = df.groupby(["title"])['LastestVideoUrl'].shift()

    # Determine if there's a new video since the last scraping
    df['HasNewVideoSinceLastScraping'] = (
          (df['isLastScraping']) &   # update only last scraping row
          (df['LatestVideoUrl_previous'].notnull()) & # a previous video was found
           (df["LatestVideoUrl_previous"] != df["LastestVideoUrl"]) # Previous video is different from the new one
           ).fillna(False)

    # Drop not useful columns
    df = df.drop(columns=["LatestVideoUrl_previous", "ScrapingDate_converted"])
    return df


def add_date_of_previous_scraping(df):
    df = df.sort_values(by=['title', 'ScrapingDate'], ascending=[True, True])
    df['PreviousScrapingDate'] = df.groupby(["title"])['ScrapingDate'].shift()

    # Define PreviousScrapingDate
    ind = df['isLastScraping'] == True
    df.loc[~ind, "PreviousScrapingDate"] = ""

    # Define LastScrapingDate
    df["LastScrapingDate"] = ""
    df.loc[ind, "LastScrapingDate"] = df.loc[ind, "ScrapingDate"]

    # Convert to string to avoid issues
    df['PreviousScrapingDate'] = pd.to_datetime(df['PreviousScrapingDate']).dt.date.astype(str)
    df['LastScrapingDate'] = pd.to_datetime(df['LastScrapingDate']).dt.date.astype(str)
    return df


def add_gaps_compared_to_last_n_days(df, n_days, tolerated_gap_nb_of_days):
    df["ScrapingDate"] = pd.to_datetime(df['ScrapingDate'])
    last_scraping_date = df["ScrapingDate"].max()

    col_name = str(n_days) + "_Days_Ago"
    last_n_days = [last_scraping_date - pd.Timedelta(days=i) for i in range(n_days + 1 + tolerated_gap_nb_of_days)]

    # Create temporary dataframe with all required dates
    df_tmp = pd.DataFrame(last_n_days, columns=["Date"]).assign(key=1)
    df_tmp["LastScrapingDate"] = df_tmp["Date"].max()
    df_tmp["Gap_in_days"] = (df_tmp['Date'] - df_tmp["Date"].max()).dt.days
    df_tmp["Tolerated_gaps"] = (abs(df_tmp["Gap_in_days"]) <= n_days + tolerated_gap_nb_of_days) & (
                abs(df_tmp["Gap_in_days"]) >= n_days - tolerated_gap_nb_of_days)
    df_tmp["tmp_index"] = df_tmp["Gap_in_days"] + n_days

    # Keep only tolerated dates
    df_tmp = df_tmp[df_tmp["Tolerated_gaps"] == True].sort_values("tmp_index").reset_index(drop=True)

    # Enrich with all titles (cartesian product)
    df_tmp = pd.merge(df[["title"]].drop_duplicates().assign(key=1), df_tmp).drop(columns="key")

    # Retrieve viewCounts if found in df
    df_tmp = (
        pd.merge(
            df_tmp[["title", "LastScrapingDate", "Date"]],
            df[["title", "ScrapingDate", "viewCount"]].drop_duplicates().rename(columns={"ScrapingDate": "Date"}),
            on=["title", "Date"],
            how="left"
        )
    )


    # Keep only the closest event with its corresponding view count for each title
    df_tmp = (
        df_tmp.dropna(subset=['viewCount'])
        .reset_index(drop=True)
        .groupby(["LastScrapingDate", "title"])
        .agg({
             "viewCount": "first",
             "Date": "first"
         })
        .reset_index()
        .rename(columns={
            "viewCount": "viewsCount_" + col_name,
            "Date": "Date_reference_" + col_name
        })
    )

    # Update original dataframe only for rows corresponding to last scraping date
    df_result = (
        pd.merge(
            df,  # [["title", "ScrapingDate", "viewCount"]],
            df_tmp[["title", "LastScrapingDate", "viewsCount_" + col_name, "Date_reference_" + col_name]]
            .rename(columns={"LastScrapingDate": "ScrapingDate"}),
            left_on=["title", "ScrapingDate"],
            right_on=["title", "ScrapingDate"],
            how="left"
        )
    )

    # Create new columns
    df_result["viewsGapTo_" + col_name] = df_result["viewCount"] - df_result["viewsCount_" + col_name]
    df_result["viewsGrowthPercentage_" + col_name] = round(
        df_result["viewsGapTo_" + col_name] * 100 / df_result["viewsCount_" + col_name], 2)
    # print(df_result.loc[df_result["viewsGapTo_" + col_name] > 0, ["title", "ScrapingDate", "viewsGapTo_" + col_name]])

    # Post processing to avoid type issues in json
    date_cols = [
        'LastScrapingDate',
        'ScrapingDate',
        "Date_reference_" + col_name
    ]
    int_cols = [
        "viewsGapTo_" + col_name,
        "viewsCount_" + col_name,
        "viewsGrowthPercentage_" + col_name
    ]
    for col in date_cols:
        df_result[col] = pd.to_datetime(df_result[col]).dt.date.astype(str)

    for col in int_cols:
        df_result[col] = df_result[col].fillna("")

    return df_result


def get_input_sheet():
    if os.environ.get("LOCAL_EXECUTION") == "False":
        from google.colab import auth
        import gspread
        from google.auth import default
        # Autenticating to google
        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)
        # Defining my worksheet
        worksheet = gc.open_by_key(os.environ.get("MY_GOOGLE_SHEET_ID")).worksheet('input')
        # Get_all_values gives a list of rows
        rows = worksheet.get_all_values()
        # Convert to a DataFrame
        df = pd.DataFrame(rows[1:], columns=rows[0])
    else:
        df = pd.read_csv(r'input_data\input_tunisian_rappers.csv')
    return df


# def launch_all_process(local_execution=True, api_key="", my_google_sheet_id=""):
def launch_all_process():
    from os.path import join, dirname
    from dotenv import load_dotenv

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    df = get_input_sheet()
    df = retrieve_youtube_information(df)
    df = concatenate_with_previous_results(df)
    df = add_flag_for_new_videos_released_since_last_scraping(df)
    df = add_date_of_previous_scraping(df)


    # df = pd.read_csv(r"output_data\results_tmp.csv")
    df = add_gaps_compared_to_last_n_days(df, n_days=30*12, tolerated_gap_nb_of_days=30)
    df = add_gaps_compared_to_last_n_days(df, n_days=30*6, tolerated_gap_nb_of_days=15)
    df = add_gaps_compared_to_last_n_days(df, n_days=30*3, tolerated_gap_nb_of_days=7)
    df = add_gaps_compared_to_last_n_days(df, n_days=30, tolerated_gap_nb_of_days=5)
    df = add_gaps_compared_to_last_n_days(df, n_days=15, tolerated_gap_nb_of_days=4)
    df = add_gaps_compared_to_last_n_days(df, n_days=7, tolerated_gap_nb_of_days=3)

    return df


if __name__ == '__main__':

    df = launch_all_process()

    # Get the current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')

    # Sort the DataFrame
    df_sorted = df.sort_values(["title", "ScrapingDate"]).reset_index(drop=True)

    # Define the output file path with date and hour
    output_file_path = rf"output_data\results_{date_str}.csv"

    # Save the sorted DataFrame to CSV with the specified file name
    df_sorted.to_csv(output_file_path, index=False)

    print(f"Output saved to: {output_file_path}")