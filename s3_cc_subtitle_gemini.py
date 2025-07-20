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

CHANNEL_NAME = config['CHANNEL_NAME']

class Vpn(BaseModel):
    name: str


def is_promoting_vpn(transcription):
    client = genai.Client(api_key = config['GEMINI_API_KEY'])


    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=transcription),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[Vpn],
        system_instruction=[
            types.Part.from_text(text="""Please determine whether the video promotes or sponsors any VPN services. If it does, output the names of all promoted VPNs in the structured format defined by the system. If it doesn't, output "n" in the same structured format. The transcript of the video will be provided by the user."""),
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


with open('data_transcript.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

CHANNEL_NAME = config['CHANNEL_NAME']
c = 1
l = len(data[CHANNEL_NAME])

for d in data[CHANNEL_NAME]:
    print(d['transcript'])
    if 'promoted_vpns' in d:
        print('skipped')
        continue
    promoted_vpns = is_promoting_vpn(d['transcript'])
    d['promoted_vpns'] = promoted_vpns
    print(promoted_vpns)
    with open('data_transcript_infer.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"progress: {c}/{l}")
    
    time.sleep(0.5)
    c += 1