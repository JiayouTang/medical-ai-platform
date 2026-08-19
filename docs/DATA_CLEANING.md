# Data Cleaning

The real SPARCS 2021 CSV in the parent workspace is large:

```text
../009 医养项目数据/Hospital_Inpatient_Discharges__SPARCS_De-Identified___2021_20231012.csv/Hospital_Inpatient_Discharges__SPARCS_De-Identified___2021_20231012.csv
```

Observed shape:

- size: about 794 MB
- rows: 2,101,589 including header
- raw columns: 33

## Scripts

Clean raw CSV into canonical project columns:

```bash
conda run -n medical-ai python scripts/clean_sparcs_csv.py --limit 1000 --output data/processed/inpatient_sparcs_2021_clean_1000.csv
```

Load cleaned CSV into MySQL:

```bash
conda run -n medical-ai python scripts/load_sparcs_mysql.py --csv data/processed/inpatient_sparcs_2021_clean_1000.csv --replace-table
```

Verified result:

```text
Cleaned 1000 rows into data/processed/inpatient_sparcs_2021_clean_1000.csv
Loaded 1000 cleaned SPARCS rows into inpatient.
```

The cleaner also writes a quality profile next to the output file:

```text
data/processed/inpatient_sparcs_2021_clean_1000.profile.json
```

The profile includes row count, null counts, max observed string lengths, top categorical values, numeric min/max values, and a sample of invalid rows.

For the full file, omit `--limit`:

```bash
conda run -n medical-ai python scripts/clean_sparcs_csv.py
sudo mysql -e "SET GLOBAL local_infile = 1; SHOW GLOBAL VARIABLES LIKE 'local_infile';"
conda run -n medical-ai python scripts/load_sparcs_mysql.py --replace-table --method load-data
```

`data/processed/*` is ignored by Git.

The cleaner uses streaming `csv.DictReader`/`DictWriter` from the Python standard library to avoid loading the 794 MB source file into memory. Pandas remains acceptable for future profiling, EDA, or richer data quality reports, but it is not required for the current ingestion path.

If MySQL `local_infile` cannot be enabled, use `--method insert`. This is slower but does not require the server-side local infile switch:

```bash
conda run -n medical-ai python scripts/load_sparcs_mysql.py --replace-table --method insert
```

## Normalization Rules

- `Age Group` is normalized:
  - `0 to 17` -> `0to17`
  - `18 to 29` -> `18to29`
  - `30 to 49` -> `30to49`
  - `50 to 69` -> `50to69`
  - `70 or Older` -> `70orOlder`
- `Gender` is normalized:
  - `F` -> `Female`
  - `M` -> `Male`
  - `U` -> `Unknown`
- `Emergency Department Indicator` is normalized:
  - `Y` -> `Yes`
  - `N` -> `No`
- `Length of Stay` values like `120 +` are stored as integer `120`.
- `Total Charges` and `Total Costs` remove thousands separators and are stored as decimals.
- Blank strings become SQL `NULL`.
- `RaceEthnicity` is derived as `Race | Ethnicity` for compatibility with earlier QuerySpec fields.

## Current MySQL Development Table

The current local `inpatient` table was recreated from `data/processed/inpatient_sparcs_2021_clean_1000.csv`, so it contains a 1000-row cleaned development subset from SPARCS 2021, not the earlier 20-row synthetic table.
