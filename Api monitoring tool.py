import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime

import requests

DB_PATH = "database.db"
CHECK_INTERVAL = 60
TIMEOUT = 30


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS apis (
                url TEXT PRIMARY KEY
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                error TEXT
            )
        """)


def get_urls():
    with db() as conn:
        return [row[0] for row in conn.execute("SELECT url FROM apis ORDER BY url")]


def check_api(url):
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=TIMEOUT)
        return response.status_code, time.perf_counter() - start, None
    except requests.exceptions.Timeout:
        return None, None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, None, "could not connect"
    except requests.exceptions.RequestException as e:
        return None, None, str(e)


def monitor(stop_event):
    while not stop_event.is_set():
        for url in get_urls():
            status, elapsed, error = check_api(url)
            now = datetime.now().isoformat(timespec="seconds")

            with db() as conn:
                conn.execute(
                    "INSERT INTO checks (url, checked_at, status_code, response_time, error) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (url, now, status, elapsed, error),
                )

            if error:
                print(f"\n[{now}] DOWN  {url} ({error})")
            elif 200 <= status < 400:
                print(f"\n[{now}] OK    {url} {status} in {elapsed:.3f}s")
            else:
                print(f"\n[{now}] ERROR {url} status {status} in {elapsed:.3f}s")

        stop_event.wait(CHECK_INTERVAL)  # wakes up immediately on quit


def show_urls():
    urls = get_urls()
    if not urls:
        print("\n--- No URLs currently saved ---")
        return
    print("\n--- Currently monitored APIs ---")
    for num, url in enumerate(urls, start=1):
        print(f"{num}. {url}")
    print("--------------------------------")


def add_urls():
    while True:
        url = input("Enter API URL (or 'done'): ").strip()
        if url.lower() == "done":
            break
        if not url:
            print("URL cannot be empty!")
            continue
        if not url.startswith(("http://", "https://")):
            print("URL must start with http:// or https://")
            continue
        with db() as conn:
            cur = conn.execute("INSERT OR IGNORE INTO apis (url) VALUES (?)", (url,))
        print(f"Added: {url}" if cur.rowcount else "That URL is already being monitored!")


def delete_url():
    urls = get_urls()
    if not urls:
        print("Nothing to delete.")
        return
    show_urls()
    choice = input("Number of the API to delete: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(urls):
        url = urls[int(choice) - 1]
        with db() as conn:
            conn.execute("DELETE FROM apis WHERE url = ?", (url,))
        print(f"Deleted: {url}")
    else:
        print("Invalid choice.")


def main():
    init_db()
    stop_event = threading.Event()
    threading.Thread(target=monitor, args=(stop_event,), daemon=True).start()

    actions = {"a": add_urls, "d": delete_url, "s": show_urls}
    try:
        while True:
            choice = input("\n[a]dd  [d]elete  [s]how  [q]uit > ").strip().lower()
            if choice == "q":
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Unknown command.")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stop_event.set()
        print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()