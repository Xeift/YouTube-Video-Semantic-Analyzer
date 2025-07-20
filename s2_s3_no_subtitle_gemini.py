import base64
import json
import os
import time
from typing import List

from dotenv import dotenv_values, load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

config = dotenv_values(".env")

class Vpn(BaseModel):
    name: str


def is_promoting_vpn(video_link):
    client = genai.Client(api_key=config['GEMINI_API_KEY'])

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    file_data=types.FileData(
                        file_uri=video_link,
                        mime_type="video/*",
                    )
                ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[Vpn],
        system_instruction=[
            types.Part.from_text(text="""請你判斷該影片是否有推廣/業配加密貨幣交易所。若有則按照系統定義的結構化輸出所有推廣的交易所名稱，若無則結構化輸出n。"""),
        ],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    vpns: list[Vpn] = response.parsed
    vpns_parsed = []
    for vpn in vpns:
        vpns_parsed.append(vpn.name)
    
    return vpns_parsed


with open('data_transcript_infer.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

CHANNEL_NAME = config['CHANNEL_NAME']

c = 0
l = len(data[CHANNEL_NAME])

for d in data[CHANNEL_NAME]:
    if 'promoted_vpns' in d:
        print('已略過')
    else:
        print('doing')
        print(d)
        promoted_vpns = is_promoting_vpn(d["link"])
        d['transcript'] = '\n'.join(promoted_vpns)
        d['promoted_vpns'] = promoted_vpns
        print(promoted_vpns)
        with open('data_transcript_infer.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        time.sleep(0.5)


    print(f'進度：{c}/{l}')
    c += 1