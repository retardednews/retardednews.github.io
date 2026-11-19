# RetardedNews rules

Read SOURCES.md before adding stories and FACEBOOK.md before posting.

## Images (hard rules)
- **Public domain or CC0 only.** No CC BY / CC BY-SA or any image that requires attribution, and nothing copyrighted.
  Set `license` in tools/stories.json to exactly `Public domain` or `CC0`; build.py rejects anything else.
- **Always self-hosted.** Never hotlink upload.wikimedia.org or any other host. Pipeline after editing stories:
  `python tools/fetch_image_meta.py` → `python tools/fetch_images.py` → `python tools/build.py`, then commit `img/`.
- No photo credit or watermark text on images or Facebook share cards.
