# WORMarine: WORMS Species Extractor

## Overview

This command line tool extracts species names from the World Register of Marine Species (WORMS) based on the provided PID (Persistent Identifier). It utilizes multithreading to send multiple requests to WORMS simultaneously and handles retries with exponential backoff in case of connection failures. The extracted species names are saved to a text file.

## Prerequisites

- Python 3
- Required Python packages: `requests`, `string`, `time`, `sys`, `argparse`, `itertools`, `bs4` (Beautiful Soup), `tqdm` and `concurrent.futures`
- Internet connection to access the WORMS database

## Usage

```bash
python3 WORMarine.py [-h] -p PID -o ORGANISM [-l LEVEL] -d DIRECTORY [-t THREADS] [-r RETRIES] [-s SLEEP]
```

## Parameters

* -p, --pid: The PID of the organism cluster (required)
* -o, --organism: The organism cluster (required)
* -l, --level: The level of detail (default: 1)
* -d, --directory: The directory to write the species names file to (required)
* -t, --threads: The number of threads to use (default: 4)
* -r, --retries: Maximum number of retries for requesting 1 page (default: 3)
* -s, --sleep: Sleep duration between retries (in seconds) with exponential backoff (default: 2)

## Organism Criteria

The organisms fetched are:
* Accepted organism names
* Only species names (genus and species)
* Present in a marine environment
* Extant (non-fossil)

## How it Works
### 1. Prefix Generation
At its core, the script generates a set of prefixes based on the user-defined "level of detail." These prefixes serve as the fundamental search terms used to query the WORMS database. Each prefix represents a unique combination of lowercase letters, allowing for a wide range of possible search queries.

```bash 
Level 1 Prefixes
For a "level of detail" set to 1, the generated list of prefixes consists of single letters: ['a', 'b', 'c', ..., 'z'].
```

```bash
Level 2 Prefixes
When the "level of detail" is set to 2, the generated list of prefixes comprises combinations of two letters: ['aa', 'ab', 'ac', ..., 'zz'].
```

### 2. Requesting Data from WORMS
Utilizing the generated prefixes and the provided PID (Organism Cluster ID), the script constructs specific URLs tailored for each prefix. It then sends HTTP requests to WORMS, initiating searches for species names starting with the respective prefixes and belonging to the given PID.

### 3. Handling Diverse Scenarios
* **Single and Multi-Species Pages**: The script adapts to different page structures within the WORMS database. For single species pages, it directly extracts the species name. On pages listing multiple species, it navigates through the HTML content, meticulously extracting the names of various species.

* **Empty Responses**: In cases where a specific prefix yields no results, the script handles empty responses. It continues its search by moving on to the next prefix, ensuring no data is left unexplored.

* **Prefixes with Excessive Species**: The script is equipped to recognize prefixes that lead to an overwhelming number of species (exceeding 5000 species). In such scenarios, it marks these prefixes for further analysis, allowing users to refine their search criteria if needed (highten the level of detail).

### 4. Concurrency and Multithreading
To optimize performance and expedite the data retrieval process, the script leverages the power of multithreading. By employing multiple threads, it concurrently sends multiple requests to WORMS, enhancing the overall speed of data extraction.

### 5. Robust Error Handling and Retry Mechanism
To ensure the robustness of the data extraction process, the script incorporates a comprehensive error handling mechanism. It detects failed requests, including potential network issues or server errors, and implements a retry strategy. The script waits for a specified duration (with an exponential backoff) and retries the request if failed for a specified amount of times.

### 6. Storing Unique Species Names
The extracted species names are meticulously collected and stored in a list. To ensure data accuracy and eliminate duplicates, this list of species names is transformed into a set data structure. Duplicates are automatically removed, and the resulting unique species names are sorted alphabetically.

### 7. Customization and User-Friendly Interface
The script offers a user-friendly interface, allowing users to customize various parameters such as the PID, organism cluster, level of detail, output directory, number of threads, maximum retries, and sleep duration between retries. This flexibility empowers users to tailor the script's behavior according to their specific requirements.

## Output
This tool creates a text file in the specified directory containing the extracted unique species names. If there are prefixes with too many species to extract, they are listed in the summary.

## Error Handling
If an error occurs during execution, the script will display the error message, halt all subsequent executions, and cancel any remaining tasks.

***

For more information about WORMS, visit [World Register of Marine Species](https://www.marinespecies.org/).