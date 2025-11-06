# PR instructions: Add Music & Books to Jellyfin Newsletter

This bundle adds **Music (albums)** and **Books/Audiobooks** sections.

## Files included
- `source/fetch_extra_media.py` – fetches recent **MusicAlbum**, **Book**, and **AudioBook** items from Jellyfin.
- `template/blocks/music_and_books.html` – a Jinja2 snippet you can include in your email template.
- `config-additions.yml` – keys to add under `jellyfin:` in your config.
- `main.py.patched` – example of your `main.py` with Music/Books integration added.
- `main.py.patch` – unified diff you can apply if your file is close to the pasted version.

## Quick steps
1. Copy `source/fetch_extra_media.py` into your repo.
2. In `main.py`, add:
   ```py
   from source.fetch_extra_media import get_recent_music_albums, get_recent_books
   ```
3. Insert the Music/Books fetch just after Movies/TV are gathered, then include them in the template payload. Use `main.py.patched` as a guide or apply `main.py.patch`.
4. In your email template, add:
   ```jinja2
   {% include "blocks/music_and_books.html" %}
   ```
5. In `config/config.yml` under `jellyfin:` add:
   ```yaml
   watched_music_folders:
     - "music"
   watched_book_folders:
     - "books"
   ```
