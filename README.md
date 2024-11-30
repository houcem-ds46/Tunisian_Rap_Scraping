# Project Presentation: Tunisian Rap YouTube Data Analytics

This repository retrieves information from the YouTube API to perform data analytics on the Tunisian Rap Artists ecosystem.

The ObservableHQ dashboard associated can be found [here](https://toulousedataviz.github.io/collections/tunisian_rappers/tunisian_rappers_deviceType_5.html)

![image](https://github.com/houcem-ds46/Tunisian_Rap_Scraping/assets/34838300/33584c83-a107-423e-bad7-d4bd8caf8f63)

Creator: [Houcem CHAABANE](https://www.linkedin.com/in/houcem-eddine-chaabane/)  

A blog post about this respository's topic can be found [here](https://tunisianrapblog.simple.ink/).  

Special thanks to [Toulouse Dataviz](https://toulouse-dataviz.fr/), [Alain Ottenheimer](https://www.linkedin.com/in/alainottenheimer/), and [Vincent Vivanloc](https://www.linkedin.com/in/vvivanloc) for their amazing and generous help.


## Data Flow Diagram

```plaintext
+----------------+         +-------------+         +-----------------+
|                |         |             |         |                 |
| Input Dataset  +-------> | Processing  +-------> | Output Dataset  |
|                |         |             |         |                 |
+----------------+         +-------------+         +-----------------+
```

## Installation

Before running the project, ensure that you have all the necessary dependencies installed. You can do this by installing the packages listed in the `requirements.txt` file. To install these dependencies, run the following command in your terminal:

```sh
pip install -r requirements.txt
```

## Environment Variables

To run this project, a `.env` file must be created with the following variables:
- `API_KEY` is your personal YouTube API key.
- `LOCAL_EXECUTION` indicates if you are executing on a local machine. If set to `False`, the execution is happening in Google Colab.
- `MY_GOOGLE_SHEET_ID` is only mandatory when `LOCAL_EXECUTION` is set to `False`. It indicates the URL path of your Google Sheet. This Google Sheet must contain a sheet named "input" and a sheet named "output_new".


## Input Dataset : Documentation

The input dataset used in project must contain information about various YouTube channels (associated with different artists) that are needed to be scraped. If you are excecuting on your local machine then the file must be stored as csv in "input_data\input_tunisian_rappers.csv". If you are excecuting in google collab then it must be stored in your google sheet's sheet named "input". 
Each row in the dataset represents an artist and their corresponding YouTube channel information. Below is a detailed description of each column in the dataset:

| Column Name      | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Artist           | Name of the artist.                                                         |
| YoutubeChannel   | URL of the artist's YouTube channel.                                        |
| Keep             | A flag indicating whether the channel should be included (1) or excluded (0). |

### Example Dataset

Here is an example of the dataset used in this project:

| Artist              | YoutubeChannel                                                          | Keep |
|---------------------|--------------------------------------------------------------------------|------|
| naqqa               | [YouTube](https://www.youtube.com/channel/UCyGtqW7TfOToaMY0A8GnXyA)      | 1    |
| zomra               | [YouTube](https://www.youtube.com/channel/UCVnoVCYHZqTjaQGPE5wUi7Q)      | 1    |
| ABSY gam7           | [YouTube](https://www.youtube.com/channel/UCvhIothkBGEpDfgZdxvWc6g)      | 1    |
| wmd                 | [YouTube](https://www.youtube.com/channel/UCGeO-C6bauO14dXBqTvjvow)      | 1    |
| empire              | [YouTube](https://www.youtube.com/channel/UC982yfxBCeh5WI9GRRlciww)      | 1    |
| redstar radi        | [YouTube](https://www.youtube.com/channel/UCpNEN5-7gzhUpapA3ob2ZqQ)      | 1    |
| gga                 | [YouTube](https://www.youtube.com/channel/UCEaQBiiuwbn_UG64vCq04dA)      | 1    |
| redstar             | [YouTube](https://www.youtube.com/channel/UC4m5L8brApVSVe_AoD_Lw4w)      | 1    |
| hamzaoui med amine  | N/A                                                                      | 0    |

### Notes
- The `Artist` column contains the name of the artist.
- The `YoutubeChannel` column contains the URL of the artist's YouTube channel. If this field is empty, it indicates that there is no YouTube channel associated with that artist.
- The `Keep` column is a binary flag where `1` indicates that the YouTube channel should be included in the scraping process, and `0` indicates that it should be excluded.

## Output Dataset : Documentation

The output dataset from this repository contains detailed information about various YouTube channels associated with different artists. Each row in the dataset represents a snapshot of the YouTube channel's metrics at a specific scraping date. Below is a detailed description of each column in the dataset:

| Column Name                               | Description                                                                                                               |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| title                                     | The title of the YouTube page (usually the name of the artist).                                                           |
| viewCount                                 | Total number of views of the page at the scraping date.                                                                   |
| subscriberCount                           | Total number of subscribers (followers) of the page at the scraping date.                                                 |
| videoCount                                | Total number of videos on the page at the scraping date.                                                                  |
| createdAt                                 | Date when the artist's YouTube page was created.                                                                          |
| YoutubeChannel                            | URL link to the YouTube page (standardized format: https://www.youtube.com/channel/ + channel ID).                        |
| LastestVideoUrl                           | URL link to the latest video published on the artist's YouTube page at the scraping date. Videos less than 60 seconds are excluded (YouTube Shorts). |
| ScrapingDate                              | The date of the scraping.                                                                                                 |
| ScrapingTimestamp                         | The timestamp of the scraping.                                                                                            |
| AverageViewsPerVideo                      | Average number of views per video at the scraping date.                                                                   |
| YearsSinceCreation                        | Number of years since the YouTube channel was created (at the scraping date).                                             |
| CustomClusterNbOfViews                    | Custom cluster calculated based on the number of views.                                                                   |
| CoverImageUrl                             | URL link to the cover image of the YouTube page.                                                                          |
| isLastScraping                            | Boolean value indicating if this is the most recent scraping.                                                             |
| LastestVideoUrlEmbeded                    | The URL link to the latest video in "embed" format published on the page at the scraping date.                            |
| HasNewVideoSinceLastScraping              | Boolean value indicating if a new video has been published on the artist's YouTube channel since the last scraping. This variable is True if and only if a new video has been published between LastScrapingDate and PreviousScrapingDate. |
| PreviousScrapingDate                      | The date of the penultimate scraping (applicable only for the row corresponding to the latest scraping).                   |
| LastScrapingDate                          | The date of the latest scraping (applicable only for the row corresponding to the latest scraping).                       |
| viewsCount_360_Days_Ago                   | Number of views the artist had 360 days (+/- 30 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| Date_reference_360_Days_Ago               | The date of the scraping conducted 360 days (+/- 30 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| viewsGapTo_360_Days_Ago                   | Difference in the number of views between the latest scraping date and the scraping conducted 360 days (+/- 30 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsGrowthPercentage_360_Days_Ago        | Percentage difference in the number of views between the latest scraping date and the scraping conducted 360 days (+/- 30 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsCount_180_Days_Ago                   | Number of views the artist had 180 days (+/- 15 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| Date_reference_180_Days_Ago               | The date of the scraping conducted 180 days (+/- 15 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| viewsGapTo_180_Days_Ago                   | Difference in the number of views between the latest scraping date and the scraping conducted 180 days (+/- 15 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsGrowthPercentage_180_Days_Ago        | Percentage difference in the number of views between the latest scraping date and the scraping conducted 180 days (+/- 15 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsCount_90_Days_Ago                    | Number of views the artist had 90 days (+/- 7 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| Date_reference_90_Days_Ago                | The date of the scraping conducted 90 days (+/- 7 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| viewsGapTo_90_Days_Ago                    | Difference in the number of views between the latest scraping date and the scraping conducted 90 days (+/- 7 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsGrowthPercentage_90_Days_Ago         | Percentage difference in the number of views between the latest scraping date and the scraping conducted 90 days (+/- 7 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsCount_30_Days_Ago                    | Number of views the artist had 30 days (+/- 5 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| Date_reference_30_Days_Ago                | The date of the scraping conducted 30 days (+/- 5 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| viewsGapTo_30_Days_Ago                    | Difference in the number of views between the latest scraping date and the scraping conducted 30 days (+/- 5 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsGrowthPercentage_30_Days_Ago         | Percentage difference in the number of views between the latest scraping date and the scraping conducted 30 days (+/- 5 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsCount_15_Days_Ago                    | Number of views the artist had 15 days (+/- 4 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| Date_reference_15_Days_Ago                | The date of the scraping conducted 15 days (+/- 4 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| viewsGapTo_15_Days_Ago                    | Difference in the number of views between the latest scraping date and the scraping conducted 15 days (+/- 4 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsGrowthPercentage_15_Days_Ago         | Percentage difference in the number of views between the latest scraping date and the scraping conducted 15 days (+/- 4 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsCount_7_Days_Ago                     | Number of views the artist had 7 days (+/- 3 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| Date_reference_7_Days_Ago                 | The date of the scraping conducted 7 days (+/- 3 days) ago relative to the latest scraping date (applicable only for the row corresponding to the latest scraping). |
| viewsGapTo_7_Days_Ago                     | Difference in the number of views between the latest scraping date and the scraping conducted 7 days (+/- 3 days) ago (applicable only for the row corresponding to the latest scraping). |
| viewsGrowthPercentage_7_Days_Ago          | Percentage difference in the number of views between the latest scraping date and the scraping conducted 7 days (+/- 3 days) ago (applicable only for the row corresponding to the latest scraping). |
| ArtistRankAccordingToViewsPerTimestamp    | The artist's rank based on the number of views. This rank is calculated for all artists at each scraping date timestamp. The artist ranked 1 has the highest number of views. |
