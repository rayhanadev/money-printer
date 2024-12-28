# Money Printer

TODO:
- [x] scrape youtube videos
  - uses pytube and google apis to search and download
- [X] scrape reddit posts
  - uses praw to scrape reddit data
- [x] generate voiceover
  - openai voice (tts-1 model)
- [x] generate captions
  - get captions from voice endpoint
- [x] generate video with moviepy
  - [x] split video into 1m clips
  - [x] add captions over video
  - [x] add voiceover to video
- [ ] queue for review
  - can be done with a filesystem queue
- [ ] publish to platforms (yt shorts, tiktok, reels)
  - can be done with youtube api, tiktok api, instagram api
