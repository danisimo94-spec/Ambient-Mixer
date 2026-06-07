# Ambient Mixer

Minimal dark desktop ambient sound mixer built with Python, CustomTkinter, and pygame.

Ambient Mixer downloads short preview audio files from Freesound on first run, stores them locally, and lets you mix multiple looping ambience layers with per-sound and master volume controls.

## Features

- Minimal dark 400x520 desktop UI
- 8 ambient sound layers:
  - Rain
  - Fire
  - Cafe
  - Wind
  - Waves
  - Birds
  - Keyboard
  - Thunder / Storm
- Per-sound clickable progress bars for volume
- Master volume clickable progress bar
- Presets:
  - Deep Work
  - Rain Cafe
  - Sleep
  - Nature
  - Storm
- Topbar play/pause button
- Pomodoro-style timer in topbar
  - Click timer to cycle through `00:00`, `25:00`, `45:00`, `60:00`, `90:00`
  - Timer starts automatically when Play is pressed if selected time is greater than zero
- First-run sound downloader using Freesound preview MP3 URLs
- Local `sounds/manifest.json` cache so sounds are not downloaded every launch
- Optional Windows desktop launcher via `Start Ambient Mixer.bat`

## Screens / style

Design goal: quiet, minimal, dark, distraction-free.

Colors:

- Window background: `#111111`
- Active row background: `#1a1a1a`
- Active text: `#eeeeee`
- Inactive text: `#444444`
- Progress fill: `#eeeeee`
- Progress track: `#222222`

Font:

- Uses Inter if installed
- Falls back to Segoe UI or system default sans-serif

## Requirements

- Python 3.10+
- Freesound API key
- Windows, macOS, or Linux with Python GUI support

Python packages:

```txt
customtkinter
pygame
requests
```

## Setup

Clone repo:

```bash
git clone https://github.com/danisimo94-spec/Ambient-Mixer.git
cd Ambient-Mixer
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows cmd:

```cmd
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Freesound API key

This app uses Freesound API only to download public preview files. Your API key must stay private.

Create `.env` in project root:

```bash
cp .env.example .env
```

Edit `.env`:

```env
FREESOUND_API_KEY=your_freesound_api_key_here
```

`.env` is ignored by git and must not be committed.

Get API key here:

<https://freesound.org/apiv2/apply/>

## Run

```bash
python main.py
```

On first run:

1. `main.py` checks for `sounds/manifest.json`.
2. If missing, it runs `downloader.py` automatically.
3. `downloader.py` downloads preview MP3 files into `sounds/`.
4. `sounds/manifest.json` maps categories to local files.
5. App starts and uses local audio files.

Run downloader manually if needed:

```bash
python downloader.py
```

## Windows desktop launcher

Local Windows helper:

```txt
Start Ambient Mixer.bat
```

Double-click it to launch with `pythonw.exe` and avoid console window.

If Python is installed in another path, edit bat file.

## Controls

### Play / pause

Use round button in top right.

- Play starts all sound channels in loop mode.
- Pause pauses all active channels.
- Resuming does not restart sounds; it unpauses channels.

### Sound volumes

Each sound row has thin clickable progress bar.

- Click bar to set volume.
- Drag bar to adjust volume.
- Volume updates live without restarting audio.

Effective channel volume:

```txt
sound_volume / 100 * master_volume / 100
```

### Master volume

Bottom bar controls master volume.

- Click/drag to adjust.
- Updates all channel volumes live.

### Presets

Preset pills set multiple sound volumes at once.

Preset values:

```txt
Deep Work: rain=40, fire=20, keyboard=30, others=0
Rain Cafe: rain=50, cafe=40, fire=10, others=0
Sleep: rain=30, waves=50, wind=20, others=0
Nature: birds=60, wind=30, waves=30, others=0
Storm: rain=70, thunder=50, wind=40, others=0
```

### Timer

Click timer text in topbar to cycle:

```txt
00:00 -> 25:00 -> 45:00 -> 60:00 -> 90:00 -> 00:00
```

If time is greater than zero, timer starts automatically when Play is pressed.

## Sound sources

Downloader uses Freesound API and downloads `previews.preview-hq-mp3` only. These preview files do not require OAuth.

Current pinned Freesound IDs:

| Category | Freesound ID | Description |
| --- | ---: | --- |
| rain | 525046 | Rain ambience loop |
| fire | 729396 | Campfire / fireplace crackling |
| cafe | 453074 | Coffee shop ambience |
| wind | 544853 | Wind through trees |
| waves | 852826 | Gentle ocean waves loop |
| birds | 634511 | Spring birds and woodpeckers |
| keyboard | 700412 | Computer keyboard typing |
| thunder | 704603 | Thunderstorm with rain |

The downloader checks that licenses are CC0 or CC-BY-compatible URL patterns before writing the manifest.

## Project structure

```txt
Ambient-Mixer/
├── main.py                    # Desktop UI and audio mixer
├── downloader.py              # Freesound downloader
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── .gitignore                 # Keeps token/cache/audio out of git
├── Start Ambient Mixer.bat    # Optional Windows launcher
└── sounds/                    # Generated local audio cache, ignored by git
    ├── manifest.json          # Generated category -> file mapping, ignored by git
    └── *.mp3                  # Generated downloaded previews, ignored by git
```

## Git hygiene

Ignored files:

- `.env`
- Python cache files
- virtual environments
- generated audio files in `sounds/`
- generated `sounds/manifest.json`

This keeps API tokens and downloaded media out of the repository.

## Troubleshooting

### `FREESOUND_API_KEY is missing`

Create `.env` from `.env.example` and add your Freesound API key.

### No sound plays

Check:

1. System volume is not muted.
2. Master volume in app is greater than 0.
3. At least one sound row volume is greater than 0.
4. `sounds/manifest.json` exists.
5. MP3 files exist in `sounds/`.

### Downloader fails

Possible causes:

- Invalid or missing Freesound API key
- No internet connection
- Freesound API outage
- Freesound sound preview unavailable

Run manually for detailed console output:

```bash
python downloader.py
```

### Pygame warning about `pkg_resources`

You may see warning like:

```txt
pkg_resources is deprecated as an API
```

This warning comes from pygame internals and does not block app launch.

## License

App code: MIT License recommended.

Downloaded sounds are not stored in git. They are fetched from Freesound at runtime and remain subject to their own Freesound licenses.
