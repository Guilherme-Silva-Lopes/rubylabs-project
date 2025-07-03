# JSONPlaceholder API Data Processing

## Overview

This project contains a Python script that fetches and processes data from the JSONPlaceholder API. It retrieves users, their latest posts, and the latest comments on those posts, applying specific filtering criteria. The processed data is then saved to a CSV file.

The script is designed to be efficient and resilient, using asynchronous programming for concurrent API requests and implementing retries with exponential backoff for handling transient network issues.

## Features

- **Data Retrieval**: Fetches users, posts, and comments from the JSONPlaceholder API.
- **Filtering**:
    - Processes only users with even IDs.
    - Fetches the 5 latest posts for each selected user.
    - Fetches the 3 latest comments for each of those posts.
- **Data Validation**: Checks for the presence of required fields in the fetched data.
- **Concurrency**: Uses `aiohttp` for asynchronous API calls to improve performance.
- **Error Handling**: Implements retries with exponential backoff for failed API requests using the `tenacity` library.
- **Logging**: Provides detailed logging of events, including API calls, retries, and validation issues.
- **Output**: Saves the combined data into a single CSV file named `output.csv`.

## Setup and Execution

### Prerequisites

- Python 3.7+

### Installation

1.  **Clone the repository or download the source code.**

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the Script

To run the script, execute the following command in your terminal:

```bash
python main.py
```

The script will start fetching the data, and upon completion, you will find the `output.csv` file in the same directory.

## Design Decisions

- **Asynchronous Programming**: `asyncio` and `aiohttp` were chosen for concurrency to handle multiple API requests efficiently without the overhead of threads or multiple processes. This is well-suited for I/O-bound tasks like making API calls.
- **Sorting**: Since the JSONPlaceholder API does not provide a date field for posts and comments, sorting is done based on the `id` field in descending order to get the latest items.
- **Validation**: Data validation is kept simple, checking for the existence of key fields. Errors are logged, but the program continues to process other valid data to ensure robustness.
- **Dependencies**: The script relies on `aiohttp` for asynchronous requests and `tenacity` for a flexible and powerful retry mechanism. These were chosen to avoid reinventing the wheel and to use well-tested libraries.
