import os
import json
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from playwright.async_api import Page
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from requests import Response
from config import SONG_LIST_FILE_NAME, SONG_DIR

nest_asyncio.apply()

with open(SONG_LIST_FILE_NAME, "r", encoding="utf-8") as file:
    all_song_list = json.load(file)


# 避免有不合法字元
def remove_illegal_character(file_name: str):
    file_name = re.sub(r'[<>:"/\\|?*]', " ", file_name)
    return file_name


def write_to_file(song_dtl: dict):

    os.makedirs(SONG_DIR, exist_ok=True)

    file_name = song_dtl["song_link"].split("/")[-1]
    song_title = song_dtl["title"]

    song_title = remove_illegal_character(song_title)

    file_path = f"{SONG_DIR}/{song_title}_{file_name}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(song_dtl, f, ensure_ascii=False, indent=4)


def time_divider(input_time: str):
    try:
        hour, minute, second = input_time.split(":")
        return round(float(hour) * 3600 + float(minute) * 60 + float(second), 2)
    except Exception:
        return 0


async def log_response(song_dtl: dict, response: Response):
    if song_dtl["song_link"] == response.url:
        try:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")

            # get youtube link
            origin_link_block = soup.find("div", class_="alert alert-info").find("a")
            yt_link = origin_link_block["href"]

            song_dtl["youtube_link"] = yt_link

            # Parse song details
            dl_block = soup.find(name="dl")
            if dl_block:
                dt_block = dl_block.find_all(name="dt")[:3]
                for dt in dt_block:
                    if dt.text == "作曲":
                        song_dtl["artist"] = dt.find_next("dd").text
                    elif dt.text == "編曲":
                        song_dtl["arrange"] = dt.find_next("dd").text
                    elif dt.text == "作詞":
                        song_dtl["composer"] = dt.find_next("dd").text

            # Process lyrics
            lyrics_list = []
            ul_block = soup.find(name="ul", attrs={"id": "lyrics-list"})
            if ul_block:
                p_blocks = ul_block.find_all(name="p", attrs={"class": "lyrics-source"})
                option_block = soup.find(
                    "select", {"id": "input-repeat-start"}
                ).find_all("option")

                for p_block, option in zip(p_blocks, option_block):
                    # 歌詞時間軸
                    start_time = time_divider(p_block["data-start-time"])
                    end_time = time_divider(p_block["data-end-time"])

                    # 歌詞
                    lyrics = option.get_text()
                    lyrics_list.append(
                        {
                            "start_time": start_time,
                            "end_time": end_time,
                            "lyrics": lyrics.split(")", 1)[-1].strip(),
                        }
                    )

                song_dtl["lyrics_list"] = lyrics_list

            song_dtl["process_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_to_file(song_dtl)

        except Exception as e:
            print(f"Error processing response: {e}, URL: {response.url}")


async def fetch_lyrics(page: Page, song_dtl: dict, semaphore: asyncio.Semaphore):
    async with semaphore:
        song_link = song_dtl["song_link"]
        try:
            page.on(
                "response",
                lambda response: asyncio.create_task(log_response(song_dtl, response)),
            )

            # block unnecessary resources
            await page.route(
                "**/*",
                lambda route: (
                    route.abort()
                    if route.request.resource_type in ["image", "stylesheet", "font"]
                    else route.continue_()
                ),
            )

            await page.goto(song_link, timeout=10000)
            await page.wait_for_load_state("load")

        except Exception as e:
            print(f"An error occurred: {e}, at {song_link}")
        finally:
            if page:  # release resource
                await page.close()


async def main():

    start_time = time.time()

    CONCURRENT_PAGE_LIMIT = 10
    semaphore = asyncio.Semaphore(CONCURRENT_PAGE_LIMIT)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = []

        counter = 0
        BATCH_LIMIT = 500  # 可自行決定一次要處理幾首歌

        for song_dtl in all_song_list:
            if counter >= BATCH_LIMIT:
                break

            file_name = song_dtl["song_link"].split("/")[-1]
            song_title = remove_illegal_character(song_dtl["title"])
            file_path = f"{SONG_DIR}/{song_title}_{file_name}.json"

            if os.path.exists(file_path):
                print(f"歌曲 {song_title} 已存在")
                continue

            counter += 1
            page = await browser.new_page()
            tasks.append(fetch_lyrics(page, song_dtl, semaphore))

            if len(tasks) >= 10:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:
            await asyncio.gather(*tasks)

        await browser.close()

    end_time = time.time()
    print(f"Crawling completed! Cost {round(end_time - start_time, 2)} seconds.")


if __name__ == "__main__":
    asyncio.run(main())
