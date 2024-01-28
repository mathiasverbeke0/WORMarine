# WORMarine: WORMS Species Extractor

## Overview

WORMarine is a command-line tool designed to extract species names from the World Register of Marine Species (WORMS) using a provided PID (Persistent Identifier). This tool employs multithreading for parallelized requests to WORMS, implementing a retry mechanism with exponential backoff in case of connection failures. The extracted species names are then saved to a text file.

## Prerequisites

- Python 3
- Required Python packages: `requests`, `string`, `time`, `sys`, `argparse`, `itertools`, `bs4` (Beautiful Soup), `tqdm` and `concurrent.futures`
- Internet connection to access the WORMS database

## Usage

```bash
python3 WORMarine.py [-h] -p PID -d DIRECTORY [-l LEVEL] [-t THREADS] [-r RETRIES] [-s SLEEP]
```

### Options

* -p, --pid: The PID of the organism cluster (required)
* -d, --directory: The directory to write the species names file to (required)
* -l, --level: The level of detail (default: 1)
* -t, --threads: The number of threads to use (default: 4)
* -r, --retries: Maximum number of retries for requesting 1 page (default: 3)
* -s, --sleep: Sleep duration between retries (in seconds) with exponential backoff (default: 2)

## Organism Criteria

The tool fetches organisms that meet the following criteria:
* Accepted organism names
* Only species names (genus and species)
* Present in a marine environment
* Extant (non-fossil)

## How it Works
### 1. Prefix Generation
The script generates a set of prefixes based on the user-defined "level of detail." These prefixes serve as fundamental search terms for querying the WORMS database.

* Level 1 Prefixes: Single letters ['a', 'b', 'c', ..., 'z'].
* Level 2 Prefixes: Combinations of two letters ['aa', 'ab', 'ac', ..., 'zz'].

### 2. Requesting Data from WORMS
Utilizing the generated prefixes and the provided PID, the script constructs specific URLs for each prefix, initiating searches for species names starting with the respective prefixes and belonging to the given PID. To optimize performance, the script employs concurrency and multithreading, enhancing data retrieval speed through simultaneous requests to WORMS.

### 3. Storing Unique Species Names
Extracted species names are stored in a list, transformed into a set to ensure uniqueness, and sorted alphabetically. This collection of unique species names is then written to a text file in the specified directory.

## Handling Diverse Scenarios
* **Single and Multi-Species Pages**: The script adapts to varied page structures within the WORMS database. For single species pages, it directly extracts the species name. On pages listing multiple species, it navigates through the HTML content, systematically extracting the names of various species.

* **Empty Responses**: In instances where a particular prefix yields no results, the script manages empty responses by proceeding to the next prefix

* **Prefixes with Excessive Species**: If the number of species names surpasses the 5000 threshold (due to WORMS limitations), the script identifies and marks the prefixes of organisms associated with these names, displaying them in the terminal. In most cases, adjusting the level of detail resolves this issue.

* **Connection Failures**: The script implements a retry mechanism with exponential backoff to handle connection failures. If a request fails, the script waits for a specified duration and retries the request for a specified number of times.

## Important organism clusters and corresponding PIDs

| PID | Organism Cluster |
|-----|------------------|
| 1   | Biota            |
| 2   | Animalia         |
| 3   | Plantae          |
| 4   | Fungi            |
| 5   | Protozoa         |
| 6   | Bacteria         |
| 8   | Archaea          |
| 10  | Viruses          |

***

For more information about WORMS, visit [World Register of Marine Species](https://www.marinespecies.org/).