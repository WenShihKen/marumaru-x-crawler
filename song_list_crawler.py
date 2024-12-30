from bs4 import BeautifulSoup
import json
import collections
import time
import requests
import random
import os
import collections
from config import (
    MARUMARU_BASE_URL,
    HEADERS,
    SONG_LIST_FILE_NAME,
)

all_songs = []

# 排除已爬過的歌單
existed_songs = collections.defaultdict(bool)

# 將已爬過的歌單讀進來
if not os.path.exists(SONG_LIST_FILE_NAME):
    with open(SONG_LIST_FILE_NAME, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
else:
    with open(SONG_LIST_FILE_NAME, "r", encoding="utf-8") as f:
        all_songs = json.load(f)
        for song in all_songs:
            existed_songs[song["song_link"].split("/")[-1]] = True

try:
    # auto get total pages
    response = requests.get(MARUMARU_BASE_URL, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        pages_block = soup.find("span", id="vt-pagination-info")
        total_pages = int(pages_block["data-page-count"])
        print(f"Total pages: {total_pages}")

    for page in range(1, total_pages + 1):
        print(f"scraping page {page}...")

        url = f"{MARUMARU_BASE_URL}{page}"

        response = requests.get(url, headers=HEADERS)
        tmp_songs = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # find all song blocks
            # 看網站的排版在顯示一定數量以上時會有空白的block
            songs = soup.find_all("div", class_="song-list-root")

            print(f"page {page}, total songs: {len(songs)}")
            for song in songs:
                # 取得詳細的歌曲連結
                link_tag = song.find("a", href=True)
                song_link = (
                    f"https://www.marumaru-x.com/{link_tag['href']}" if link_tag else ""
                )
                if song_link == "":
                    continue

                key_word = song_link.split("/")[-1]
                if key_word in existed_songs:
                    continue

                title_tag = song.find("h2", class_="card-title")
                if title_tag:
                    title = title_tag.text.strip()
                else:
                    continue

                # 取得縮圖
                img_tag = song.find("img")
                image_url = img_tag["src"] if img_tag else ""

                duration_tag = song.find("div", class_="vu-abs-r-b duration")
                duration = duration_tag.text.strip() if duration_tag else ""
                # 計算歌曲秒數
                seconds = 0
                try:
                    seconds = int(duration.split(":")[0]) * 60 + int(
                        duration.split(":")[1]
                    )
                except:
                    pass

                tmp_songs.append(
                    {
                        "title": title,
                        "image_url": image_url,
                        "song_link": song_link,
                        "duration": seconds,
                    }
                )
        else:
            print(
                f"failed to retrieve page {page}. status code: {response.status_code}"
            )
            break

        all_songs.extend(tmp_songs)

    sleep_time = random.uniform(1, 5)
    time.sleep(sleep_time)

except Exception as e:
    print(f"Error: {e}")

with open(SONG_LIST_FILE_NAME, "w", encoding="utf-8") as f:
    json.dump(all_songs, f, ensure_ascii=False, indent=4)

print(f"Crawling completed!")
