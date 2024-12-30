# marumaru-x 歌詞備份工具 

## Introduction
This is a tool to crawl song and lyrics from [marumaru-x](https://www.marumaru-x.com)


## Installation
```bash
pip install -r requirement.txt

playwright install
```

## Crawling
```bash
python song_list_crawler.py

python lyrics_crawler.py
``` 


## Output 
The crawled data will be saved in JSON format.  
### Song List Example
```json
[
    {
        "title": "",  // song title
        "image_url": "",  // thumbnail
        "song_link": "",  // link to marumaru lyrics page
        "duration": 100  // seconds
    }
]
```

### Lyrics Detail Example
```json
{
    "title": "",
    "image_url": "",
    "song_link": "",
    "duration": 100,
    "youtube_link": "",
    "composer": "",  // may be empty
    "artist": "",  // may be empty
    "arrange": "",  // may be empty
    "lyrics_list": [
        {
            "start_time": 0.0,  
            "end_time": 5.0,  
            "lyrics": "Lyrics line 1"
        },
        {
            "start_time": 5.0,
            "end_time": 10.0,
            "lyrics": "Lyrics line 2"
        }
    ],
    "process_time": "1970-01-01 00:00:00" 
}
```

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/WenShihKen"><img src="https://avatars.githubusercontent.com/u/16423988?v=3?s=100" width="100px;" alt="Ken"/><br /><sub><b>Ken</b></sub></a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

> All contributions are the same, no matter how big or small.

## License

[MIT](LICENSE)