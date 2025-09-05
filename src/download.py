import requests
import argparse
from tqdm import tqdm
from pathlib import Path
from utils.utils_loggers import setup_logger
from utils.helpers import STATE

# instantiating logging for file download.log
logger = setup_logger(__name__, log_file="downloading")


def state_normalized(state: str = STATE) -> str:
    return state.lower().replace(" ", "-")


def download_osm_file(state: str = STATE) -> None:
    norm_state = state_normalized(state)
    html_url = f"https://download.geofabrik.de/north-america/us/{norm_state}.html"

    try:
        logger.info(f"Fetching HTML page for {state} from {html_url}")
        page_response = requests.get(html_url)
        page_response.raise_for_status()

        # check if the file link exists in the HTML page
        file_ref = f"{norm_state}-latest.osm.pbf"
        if file_ref not in page_response.text:
            logger.error(f"Download link for {state} not found in the HTML page.")
            return

        file_url = f"https://download.geofabrik.de/north-america/us/{norm_state}-latest.osm.pbf"
        logger.info(f"Found .osm.pbf file at {file_url}")

        filename = Path(f"./data/{norm_state}-latest.osm.pbf")
        filename.parent.mkdir(parents=True, exist_ok=True)

        if filename.exists():
            logger.info(f"{filename.name} already exists. Skipping download.")
            return

        file_response = requests.get(file_url, stream=True)
        file_response.raise_for_status()

        total_size = int(file_response.headers.get("content-length") or 0)
        if total_size == 0:
            logger.warning(
                "No content length header available. Progress bar may be incorrect."
            )
        with (
            open(filename, "wb") as file,
            tqdm(
                total=total_size, unit="B", unit_scale=True, desc=f"Downloading {state}"
            ) as bar,
        ):
            for chunk in file_response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

        logger.info(f"Download completed: {filename}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during downloading: {e}")

    return


def main():
    parser = argparse.ArgumentParser(
        description="Downloads state's .osm.pbf from Geofabrik."
    )
    parser.add_argument(
        "--state",
        "-s",
        default=STATE,
        help="State/territory name (e.g., 'Puerto Rico', 'Virginia').",
    )
    args = parser.parse_args()
    download_osm_file(state=args.state)


if __name__ == "__main__":
    main()
