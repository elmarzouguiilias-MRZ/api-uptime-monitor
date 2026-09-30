# API Uptime Monitor

A lightweight, multi-threaded Python CLI application that periodically monitors API endpoints and logs response times, HTTP status codes, and network errors into a SQLite database.

## Features
- **Background Threading:** Continuously checks APIs without blocking the CLI menu.
- **Historical Audit Log:** Logs response times and errors to a SQLite database over time.
- **Graceful Shutdown:** Uses thread events for immediate, clean termination.
- **Defensive Networking:** Safely handles timeouts, connection drops, and bad URLs.

## Requirements
- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/api-uptime-monitor.git](https://github.com/your-username/api-uptime-monitor.git)
   cd api-uptime-monitor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python monitor.py
   ```

## Usage
Interactive commands inside the CLI:
- `a` : Add a new URL to monitor
- `d` : Delete a monitored URL
- `s` : Show all currently monitored URLs
- `q` : Stop monitoring and exit