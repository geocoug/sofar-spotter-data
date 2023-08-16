# sofar-spotter-data

[![ci](https://github.com/geocoug/sofar-spotter-data/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/geocoug/sofar-spotter-data/actions/workflows/ci-cd.yml)

Pull Sofar Spotter data from the [Sofar API](https://docs.sofarocean.com/spotter-and-smart-mooring/spotter-data/wave-data) based on a user-specified date range and write results to JSON files.

## Usage

1. Clone the repository: `git clone https://github.com/geocoug/sofar-spotter-data.git`

1. Create a virtual Python environment: `python -m venv .venv && source .venv/bin/activate`

1. Install the Python requirements: `python -m pip install -r requirements.txt`

1. Create a `.env` file with the following keys:

    ```ini
    SOFAR_TOKEN=Your_API_Token
    ```

1. Run the script and specify appropriate positional arguments. See the help section for details.

    ```sh
    usage: pull_sofar_data.py [-h] [-v] start_date end_date outdir

    Pull data from Sofar Spotter wave sensors. Version 0.0.1, 2023-05-25

    positional arguments:
      start_date     Starting date to query for data. Format: YYYY-MM-DD
      end_date       Ending date to query for data. Format: YYYY-MM-DD
      outdir         Output directory to save data

    options:
      -h, --help     show this help message and exit
      -v, --verbose  Control the amount of information to display.
    ```

## Example

Below is an example script call which pulls all Spotter device data between dates `2023-04-01` and `2023-05-31` and places results in JSON files within a local directory called `./data`. The directory `./data` is created if one does not exist already.

### Python

  ```sh
  python pull_sofar_data.py 2023-04-01 2023-05-31 ./data
  ```

### Docker

```sh
docker run -v $(pwd)/data:/usr/local/app/data ghcr.io/geocoug/sofar-spotter-data -v 2023-04-01 2023-05-31 ./data
```

### Output

Output is binned into subdirectories by device name. Data are placed into JSON files for each day between the specified date range, for each device.

```txt
./data
├── SPOT-0401
│   ├── ...
│   ├── SPOT-0401_20230530.json
│   └── SPOT-0401_20230531.json
└── SPOT-0486
    ├── ...
    ├── SPOT-0486_20230530.json
    └── SPOT-0486_20230531.json
```

**Note**: The script does not check if there are no data returned for a specific device on any given date for any data type, which will result in an empty JSON array, as seen below.

```json
{
  "data": {
    "spotterId": "SPOT-0760",
    "limit": 100,
    "track": [],
    "wind": [],
    "partitionData": [],
    "surfaceTemp": [],
    "frequencyData": [],
    "barometerData": [],
    "waves": []
  }
}
```
