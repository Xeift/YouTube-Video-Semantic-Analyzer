# YouTube-Video-Semantic-Analyzer
Scripts that use the Gemini API to analyze whether videos from a specific creator within a certain date range meet specific conditions and export the results as .xlsx files. This saves time and eliminates the need to watch every single video yourself. For example, which VPN is Alice promoting in the videos between 2025-06-20 and 2025-06-21?

# Overview
There are two types of videos, which will affect which script you use:

A. With CC subtitles: `s1_download_video_data.py` ➡ `s2_download_cc_subtitle.py` ➡ `s3_cc_subtitle_gemini.py` ➡ `s4.py`

B. Without CC subtitles: `s1_download_video_data.py` ➡ `s2_s3_no_subtitle_gemini.py` ➡ `s4.py`

In Type A, Gemini reads the transcript. It takes about 2 seconds for gemini-2.0-flash-lite to process.

In Type B, Gemini needs to understand the full video without context. A 15-minute video takes about **1 minute** to process.  
You should use Type A if the videos have CC subtitles.

# Quickstart
After deciding which type to use, create a `.env` file with the following fields:
```
CHANNEL_NAME=
CHANNEL_ID=
YOUTUBE_DATA_APIV3_API_KEY=
GEMINI_API_KEY=
START_DATE=
END_DATE=
```
Next, run the scripts based on the type you selected.

# Warning
Gemini is not always accurate. The accuracy rate is significantly higher when using Type A. When using Type B, Gemini may occasionally give incorrect answers. This is not a mature tool—just a utility to gather the specific data I need.
