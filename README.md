# US Place Nicknames

This dataset contains nicknames for US states, counties, and cities.
Examples are "The Lone Star State" (Texas) and "The Ozone Belt" (St. Tammany Parish, Louisiana).

| File | Level | Places | Nicknames |
|------|-------|-------:|----------:|
| [`data/states.csv`](data/states.csv) | State | 50 | 912 |
| [`data/counties.csv`](data/counties.csv) | County | 240 | 430 |
| [`data/cities.csv`](data/cities.csv) | City and town | 2,881 | 9,782 |

## Get the data

- **See the data.** Click a file in the `data/` folder. GitHub shows it as a table that you can search.
- **Download one file.** Open the file. Then click **Download raw file**.
- **Download all files.** Go to [Releases](../../releases). Download `us-place-nicknames.zip`.
  The ZIP file also contains `all_nicknames.csv` (all levels in one file), `nicknames.json`,
  and a `combined/` folder with one row for each place (nicknames separated by "; ").
- **Load the data in code.** Use the raw URL of the file.

```python
import pandas as pd
url = "https://raw.githubusercontent.com/ToAFinish/us-place-nicknames/main/data/cities.csv"
cities = pd.read_csv(url, keep_default_na=False)
```

```r
cities <- read.csv("https://raw.githubusercontent.com/ToAFinish/us-place-nicknames/main/data/cities.csv")
```

## Data structure

Each row contains one nickname for one place. A place with ten nicknames has ten rows.
All files use UTF-8 and commas. Values that contain a comma have quotes around them.

### `states.csv`

| Column | Description | Example |
|--------|-------------|---------|
| `state` | Two-letter USPS state code | `TX` |
| `state_name` | Name of the state | `Texas` |
| `nickname` | One nickname | `The Lone Star State` |
| `source` | Where the nickname comes from (URL or citation). Optional. | |
| `notes` | Other information. Optional. | |

### `counties.csv`

| Column | Description | Example |
|--------|-------------|---------|
| `state` | Two-letter USPS state code | `LA` |
| `county` | Name of the county, without the word "County" or "Parish" | `St. Tammany` |
| `county_type` | `County`, `Parish`, `Borough`, `Independent City`, or another Census type | `Parish` |
| `county_fips` | Five-digit FIPS code (2020 Census). Use it to join with Census data. | `22103` |
| `nickname`, `source`, `notes` | Same as `states.csv` | |

### `cities.csv`

| Column | Description | Example |
|--------|-------------|---------|
| `state` | Two-letter USPS state code | `AK` |
| `city` | Name of the city, town, or village | `Anchorage` |
| `nickname`, `source`, `notes` | Same as `states.csv` | |

The rows are in order of state, place, and nickname. This order keeps changes small and easy to review.

## Add or correct a nickname

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md).

- **Without Git:** [Open an issue](../../issues/new/choose) and fill in the form.
- **With Git:** Edit the CSV file and open a pull request. An automatic check examines each pull request.

## Data quality

Many nicknames in this dataset are old. Some come from tourism and business promotions.
Some nicknames are no longer in use. Some entries possibly contain errors from the original text.
If you find an error, [report it](../../issues/new/choose).

## License

The data is available under the license in [LICENSE](LICENSE).

## Cite this dataset

See [CITATION.cff](CITATION.cff). On GitHub, click **Cite this repository**.
