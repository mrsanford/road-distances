import requests
import argparse
from tqdm import tqdm
from utils.utils_loggers import setup_logger
from utils.helpers import build_url, make_local_paths

# setting up custom logging
logger = setup_logger(__name__, log_file="downloading")


def download_osm_file(region: str, country: str = None, province: str = None) -> None:
    """
    Downloads an .osm.pbf file from Geofabrik for a given region/country/province.
    """
    url = build_url(region, country, province)  # PBF link
    html_url = build_url(region, country, province, html=True)  # HTML index
    input_pbf, _, _ = make_local_paths(region, country, province)

    try:
        logger.info(f"Fetching HTML page {html_url}")
        page_response = requests.get(html_url)
        page_response.raise_for_status()

        file_ref = url.split("/")[-1]
        if file_ref not in page_response.text:
            logger.error(f"Download link not found in {html_url}")
            return

        if input_pbf.exists():
            logger.info(f"{input_pbf.name} already exists. Skipping download.")
            return

        file_response = requests.get(url, stream=True)
        file_response.raise_for_status()

        total_size = int(file_response.headers.get("content-length") or 0)
        if total_size == 0:
            logger.warning(
                "No content length header available. Progress bar may be incorrect."
            )

        with (
            open(input_pbf, "wb") as file,
            tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=f"Downloading {input_pbf.stem}",
            ) as bar,
        ):
            for chunk in file_response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

        logger.info(f"Download completed: {input_pbf}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during downloading: {e}")


def main():
    parser = argparse.ArgumentParser(description="Downloads OSM PBF from Geofabrik.")
    parser.add_argument(
        "--region", "-r", required=True, help="Region (e.g., 'Africa', 'North America')"
    )
    parser.add_argument(
        "--country", "-c", help="Optional country (e.g., 'Nigeria', 'Canada')"
    )
    parser.add_argument("--province", "-p", help="Optional province (e.g., 'Alberta')")
    args = parser.parse_args()

    download_osm_file(args.region, args.country, args.province)


if __name__ == "__main__":
    main()
