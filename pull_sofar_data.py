#!/usr/bin/env python

import argparse
import json
import logging
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

__version__ = "0.0.1"
__vdate = "2023-05-25"

load_dotenv()

# Sofar API token
SOFAR_TOKEN = os.getenv("SOFAR_TOKEN")

# Configure the script logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s : %(levelname)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


def clparser() -> argparse.ArgumentParser:
    """Create a parser to handle input arguments and displaying a help message."""
    desc_msg = f"""Pull data from Sofar Spotter wave sensors.
    Version {__version__}, {__vdate}"""
    parser = argparse.ArgumentParser(description=desc_msg)
    parser.add_argument(
        "start_date",
        help="""Starting date to query for data. Format: YYYY-MM-DD""",
    )
    parser.add_argument(
        dest="end_date",
        help="""Ending date to query for data. Format: YYYY-MM-DD""",
    )
    parser.add_argument(
        "outdir",
        help="""Output director to save data""",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Control the amount of information to display.",
    )
    return parser


def send_request(
    request_type: str,
    url: str,
    **kwargs: str,
) -> requests.Response | None:
    """Send an HTTP request.

    Args:
    ----
        request_type (str): Accepts "GET" or "POST"
        url (str): Request URL

    Returns:
    -------
        requests.Response: Request response.
    """
    valid_methods = ("GET", "POST")
    if request_type.upper() not in valid_methods:
        raise ValueError(f"Invalid request type. Supported types: {valid_methods}")
    try:
        response = requests.request(request_type.upper(), url, **kwargs)
        response.raise_for_status()  # Raises an exception if status code >= 400
        return response
    except requests.exceptions.RequestException as err:
        logger.error(f"{err}. Request type: {request_type}. Args: {kwargs}")
        return None


def main(start_date: datetime, end_date: datetime, outdir: str) -> None:
    """Entrypoint for the script to call all other methods.

    Args:
    ----
        start_date (datetime): Starting date range.
        end_date (datetime): Ending date range.
        outdir (str): Directory to save output.
    """
    logger.info(
        f"Requesting data between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}",  # noqa
    )
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    devices = send_request(
        "GET",
        "https://api.sofarocean.com/api/devices",
        headers={"token": SOFAR_TOKEN},
    )
    if devices:
        devices = [device["spotterId"] for device in devices.json()["data"]["devices"]]
        for device in devices:
            if not os.path.exists(os.path.join(outdir, device)):
                os.makedirs(os.path.join(outdir, device))
        logger.info(f"Devices found: {devices}")
        while start_date <= end_date:
            logger.info(f"Collecting data for {start_date}")
            for device in devices:
                # https://docs.sofarocean.com/spotter-and-smart-mooring/spotter-data/wave-data
                data = send_request(
                    "GET",
                    f"https://api.sofarocean.com/api/wave-data?spotterId={device}&includeWindData=true&includeSurfaceTempData=true&includeTrack=true&includeFrequencyData=true&includeDirectionalMoments=true&includePartitionData=true&includeBarometerData=true&limit=500&startDate={datetime.strftime(start_date, '%Y-%m-%dT00:00:00Z')}&endDate={datetime.strftime(start_date + timedelta(days=1), '%Y-%m-%dT00:00:00Z')}",  # noqa
                    headers={"token": SOFAR_TOKEN},
                )
                if data:
                    data = data.json()
                    outfile = os.path.join(
                        os.path.join(outdir, device),
                        f"{device}_{start_date.strftime('%Y%m%d')}.json",
                    )
                    with open(outfile, "w") as f:
                        json.dump(data, f, indent=2)
                else:
                    logger.warning(f"Failed to receive data for {device}")
            start_date = start_date + timedelta(days=1)
    else:
        raise Exception("Failed to receive device list")
    logger.info(f"Data saved to {outdir}")
    logger.info("Complete")


if __name__ == "__main__":
    parser = clparser()
    args = parser.parse_args()
    verbose = args.verbose
    if verbose:
        logger.addHandler(stream_handler)
    main(
        start_date=datetime.strptime(args.start_date, "%Y-%m-%d"),
        end_date=datetime.strptime(args.end_date, "%Y-%m-%d"),
        outdir=args.outdir,
    )
