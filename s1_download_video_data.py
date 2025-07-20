import json
import os

import requests
from dotenv import load_dotenv

load_dotenv(override=True)
YOUTUBE_DATA_APIV3_API_KEY = os.getenv('YOUTUBE_DATA_APIV3_API_KEY')
CHANNELS = {
    os.getenv('CHANNEL_NAME'): os.getenv('CHANNEL_ID'),
}

START_DATE = os.getenv('START_DATE')
END_DATE = os.getenv('END_DATE')

def get_uploads_playlist_id(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={YOUTUBE_DATA_APIV3_API_KEY}'
    response = requests.get(url).json()
    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_video_ids_from_playlist(playlist_id):
    video_items = []
    next_page_token = ''
    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={next_page_token}&key={YOUTUBE_DATA_APIV3_API_KEY}'
        response = requests.get(url).json()
        for item in response['items']:
            published_at = item['contentDetails']['videoPublishedAt']
            video_id = item['contentDetails']['videoId']
            if START_DATE <= published_at <= END_DATE:
                video_items.append((video_id, published_at))
        next_page_token = response.get('nextPageToken', '')
        if not next_page_token:
            break
    return video_items

def format_view_count(view_count):
    view_count = int(view_count)
    if view_count >= 1_000_000:
        return f'{round(view_count / 1_000_000, 1)}M'
    elif view_count >= 1_000:
        return f'{round(view_count / 1_000)}K'
    else:
        return str(view_count)

def get_video_details(video_ids):
    video_data = []
    for i in range(0, len(video_ids), 50):
        ids = ','.join([vid for vid, _ in video_ids[i:i+50]])
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={ids}&key={YOUTUBE_DATA_APIV3_API_KEY}'
        response = requests.get(url).json()
        for item in response['items']:
            snippet = item['snippet']
            stats = item.get('statistics', {})
            video_id = item['id']
            title = snippet['title']
            published_at = snippet['publishedAt']
            description = snippet.get('description', '').strip()
            views_raw = stats.get('viewCount', '0')
            views = format_view_count(views_raw)
            video_url = f'https://www.youtube.com/watch?v={video_id}'

            vpn_in_title = is_string_contains_vpn(title)
            vpn_in_description = is_string_contains_vpn(description)

            video = {
                'video_id': video_id,
                'date': published_at,
                'title': title,
                'views': views,
                'link': video_url,
                'description': description,
                'vpn_in_title': vpn_in_title,
                'vpn_in_description': vpn_in_description,
            }
            video_data.append(video)
    return video_data

def is_string_contains_vpn(text):
    vpnes_in_string = []

    vpn_data = {
        'NordVPN': ['nordvpn', 'nord vpn', '諾德vpn', '諾德', '诺德vpn', '诺德'],
        'ExpressVPN': ['expressvpn', 'express vpn', '快帆', '快捷vpn', '极速vpn', '极速翻墙'],
        'Surfshark': ['surfshark', 'surf shark', '鯊魚vpn', '鲨鱼vpn', '衝浪鯊', '冲浪鲨'],
        'CyberGhost': ['cyberghost', 'cyber ghost', '幽靈vpn', '幽灵vpn'],
        'Private Internet Access': ['pia', 'private internet access', '私人網路存取', '私人网络存取'],
        'ProtonVPN': ['protonvpn', 'proton vpn', '質子vpn', '质子vpn', 'proton'],
        'Windscribe': ['windscribe', '風刻', '风刻'],
        'VyprVPN': ['vyprvpn', 'vypr vpn', '變色龍vpn', '变色龙vpn'],
        'Ivacy': ['ivacy', 'ivacy vpn'],
        'Atlas VPN': ['atlasvpn', 'atlas vpn', '阿特拉斯vpn'],
        'TunnelBear': ['tunnelbear', 'tunnel bear', '熊隧道', '隧道熊'],
        'Hide.me': ['hide.me', 'hideme', 'hide me', '隱藏我', '隐藏我'],
        'Hotspot Shield': ['hotspot shield', 'hotspotshield', '熱點盾', '热点盾'],
        'ProXPN': ['proxpn'],
        'StrongVPN': ['strongvpn', 'strong vpn', '強力vpn', '强力vpn'],
        'Mullvad': ['mullvad', '鼴鼠vpn', '鼹鼠vpn'],
        'ZoogVPN': ['zoogvpn', 'zoog vpn'],
        'PrivadoVPN': ['privadovpn', 'privado vpn'],
        'PureVPN': ['purevpn', 'pure vpn', '純淨vpn', '纯净vpn'],
        'BitVPN': ['bitvpn', 'bit vpn'],
        'Betternet': ['betternet', 'better net', '貝特網', '贝特网'],
        'Hola VPN': ['hola vpn', 'hola', '霍拉vpn'],
        'Psiphon': ['psiphon', '賽風', '赛风'],
    }

    lower_text = text.lower()
    for vpn, keywords in vpn_data.items():
        for keyword in keywords:
            if keyword.lower() in lower_text:
                vpnes_in_string.append(vpn)
                break

    return vpnes_in_string

def main():
    all_videos = {}
    for name, channel_id in CHANNELS.items():
        print(f'處理頻道: {name}')
        uploads_playlist_id = get_uploads_playlist_id(channel_id)
        video_ids = get_video_ids_from_playlist(uploads_playlist_id)
        if not video_ids:
            print('沒有影片。')
            continue
        videos = get_video_details(video_ids)
        videos.sort(key=lambda x: x['date'])
        all_videos[name] = videos

        for v in videos:
            print(f"date: {v['date']}")
            print(f"title: {v['title']}")
            print(f"views: {v['views']}")
            print(f"link: {v['link']}")
            print(f"description: {v['description']}\n{'-'*40}\n")
            print(f"vpn_in_title: {v['vpn_in_title']}")
            print(f"vpn_in_description: {v['vpn_in_description']}")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=2)
        print('已將結果儲存至 data.json')

if __name__ == '__main__':
    main()