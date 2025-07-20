import json
import os
import random
import time

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (NoTranscriptFound,
                                            TranscriptsDisabled)

load_dotenv(override=True)
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

c = 1
l = len(data[CHANNEL_NAME])

for d in data[CHANNEL_NAME]:
    if 'transcript' in d:
        print('skipped')
        continue
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(d['video_id'])
        first_transcript = next(iter(transcripts))
        d['transcript'] = '\n'.join([entry.text for entry in first_transcript.fetch()])


        with open('data_transcript.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except (TranscriptsDisabled, NoTranscriptFound):
        d['transcript'] = ''
        with open('data_transcript.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    time.sleep(1 + random.random())
    c += 1
    print(f'progress: {c}/{l}')