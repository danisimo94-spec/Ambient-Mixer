import json
import os
from pathlib import Path
from urllib.parse import urlparse

import requests

SEARCH_URL = "https://freesound.org/apiv2/search/text/"
SOUND_URL = "https://freesound.org/apiv2/sounds/{sound_id}/"
BASE_DIR = Path(__file__).resolve().parent
SOUNDS_DIR = BASE_DIR / "sounds"
MANIFEST_PATH = SOUNDS_DIR / "manifest.json"
ENV_PATH = BASE_DIR / ".env"


def load_env(path=ENV_PATH):
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
API_KEY = os.environ.get("FREESOUND_API_KEY")
if not API_KEY:
    raise RuntimeError("FREESOUND_API_KEY is missing. Create .env from .env.example.")

SOUNDS = {
    "rain": {"query": "rain ambience loop", "sound_id": 525046},
    "fire": {"query": "fireplace crackling loop", "sound_id": 729396},
    "cafe": {"query": "coffee shop ambience loop", "sound_id": 453074},
    "wind": {"query": "wind trees loop", "sound_id": 544853},
    "waves": {"query": "ocean waves loop", "sound_id": 852826},
    "birds": {"query": "birds forest ambience loop", "sound_id": 634511},
    "keyboard": {"query": "keyboard typing loop", "sound_id": 700412},
    "thunder": {"query": "thunderstorm ambience loop", "sound_id": 704603},
    "singing_bowls": {"query": "tibetan singing bowls meditation loop", "sound_id": 475307},
    "tingsha": {"query": "tingsha bells meditation", "sound_id": 365403},
    "gong": {"query": "gong meditation ambience loop", "sound_id": 235454},
    "flute": {"query": "flute drone meditation ambient loop", "sound_id": 634118},
    "om_drone": {"query": "om drone meditation ambient", "sound_id": 854866},
    "stream": {"query": "stream creek water flowing loop", "sound_id": 419119},
    "crickets": {"query": "crickets night ambience loop", "sound_id": 521843},
    "cave": {"query": "cave drips water ambience loop", "sound_id": 553080},
    "blizzard": {"query": "blizzard wind snowstorm loop", "sound_id": 679941},
    "train": {"query": "train ride interior ambience loop", "sound_id": 438798},
    "library": {"query": "library ambience quiet loop", "sound_id": 767305},
    "tavern": {"query": "tavern fireplace ambience loop", "sound_id": 695295},
    "rain_window": {"query": "rain on window glass ambience loop", "sound_id": 535868},
}


def search_sound(query):
    params = {
        "query": query,
        "token": API_KEY,
        "filter": 'license:"Creative Commons 0"',
        "fields": "id,name,license,previews",
        "page_size": 10,
    }
    response = requests.get(SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise RuntimeError(f"No Freesound results for: {query}")
    return results[0]


def get_sound(sound_id):
    response = requests.get(
        SOUND_URL.format(sound_id=sound_id),
        params={"token": API_KEY, "fields": "id,name,license,previews"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def download_file(url, destination):
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with destination.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 128):
                if chunk:
                    file.write(chunk)


def download_sounds():
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {}

    for category, config in SOUNDS.items():
        if category in manifest:
            existing_path = BASE_DIR / manifest[category]
            if existing_path.exists() and existing_path.stat().st_size > 0:
                print(f"Using manifest {category}: {existing_path.name}")
                continue

        query = config["query"]
        sound_id = config.get("sound_id")
        if sound_id:
            print(f"Fetching {category}: {sound_id} ({query})")
            sound = get_sound(sound_id)
        else:
            print(f"Searching {category}: {query}")
            sound = search_sound(query)
            sound_id = sound["id"]

        license_url = sound.get("license", "")
        if "publicdomain/zero" not in license_url and "by/" not in license_url:
            raise RuntimeError(f"Unsupported license for {category}: {license_url}")

        preview_url = sound.get("previews", {}).get("preview-hq-mp3")
        if not preview_url:
            raise RuntimeError(f"No preview-hq-mp3 for {category}: {sound.get('name')}")

        suffix = Path(urlparse(preview_url).path).suffix or ".mp3"
        filename = f"{sound_id}{suffix}"
        destination = SOUNDS_DIR / filename

        if destination.exists() and destination.stat().st_size > 0:
            print(f"Using existing {category}: {destination.name}")
        else:
            print(f"Downloading {category}: {sound.get('name')} -> {destination.name}")
            download_file(preview_url, destination)

        manifest[category] = str(Path("sounds") / filename).replace("\\", "/")

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH}")
    return manifest


if __name__ == "__main__":
    download_sounds()
