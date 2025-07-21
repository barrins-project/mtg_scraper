import argparse
import json
from collections import defaultdict
from pathlib import Path
from queue import Queue
from threading import Lock, Thread
from typing import Any, DefaultDict, Generator, List, Optional

from scraper.services.mtgtop8 import consumer, producer
from scraper.utils.mtgtop8 import BASE_PATH, get_id_from_filepath


def main():
    parser = argparse.ArgumentParser(description="Rescrape MTG Top8 files.")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Number of files to process in each chunk.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of files to process in each batch.",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=4,
        help="Number of threads to use for processing.",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Key to check in JSON files (e.g., 'decks>notes').",
    )
    parser.add_argument(
        "--chunk-by-chunk",
        action="store_true",
        help="Pause between chunks for manual verification.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display targeted IDs without launching threads.",
    )

    args = parser.parse_args()

    rescrape_files(
        chunk_size=args.chunk_size,
        batch_size=args.batch_size,
        num_threads=args.num_threads,
        chunk_by_chunk=args.chunk_by_chunk,
        target=args.target,
        dry_run=args.dry_run,
    )

    print("🎉 All tournaments reprocessed.")


def rescrape_files(
    chunk_size: int,
    batch_size: int,
    num_threads: int,
    chunk_by_chunk: bool,
    target: Optional[str],
    dry_run: bool,
):
    files = sorted(
        list(BASE_PATH.rglob("*.json")),
        key=lambda x: get_id_from_filepath(x),
    )
    if not files:
        print("No JSON files found in the base path. Exiting.")
        return

    keys_to_check: Optional[List[str]] = None
    if target:
        keys_to_check = target.split(">")
        print(f"🔎 Checking for key {' > '.join(keys_to_check)} in all files...")

    if dry_run:
        rescrape_ids = get_ids_to_rescrape(files, keys_to_check, batch_size)
        print(f"💡 Dry run mode — {len(rescrape_ids)} IDs to rescrape:")
        print(rescrape_ids[:50])
        if len(rescrape_ids) > 50:
            print(f"... and {len(rescrape_ids) - 50} more.")
        return

    check = (
        input(f"Do you want to check all {len(files)} files? (y/n): ")
        if target
        else input(f"Do you want to reprocess all {len(files)} files? (y/n): ")
    )
    if check.lower() != "y":
        print("Aborting rescrape.")
        return

    for chunk_start in range(0, len(files), chunk_size):
        chunk_files = files[chunk_start : chunk_start + chunk_size]
        print(
            f"\n⛏️ Chunk {get_id_from_filepath(chunk_files[0])} to {get_id_from_filepath(chunk_files[-1])}"
        )
        if chunk_by_chunk:
            input("Press Enter to start processing this chunk...")

        chunk_ids: List[int] = get_ids_to_rescrape(
            files=chunk_files,
            keys_to_check=keys_to_check,
            batch_size=batch_size,
        )

        task_queue = Queue()
        lock = Lock()
        retries: DefaultDict[str, int] = defaultdict(int)

        for i in range(0, len(chunk_ids), batch_size):
            batch = chunk_ids[i : i + batch_size]
            threads = [
                Thread(target=producer, args=(event_id, task_queue, lock))
                for event_id in batch
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        print(f"📦 Chunk queued: {task_queue.qsize()} tournaments")

        consumer_threads = [
            Thread(target=consumer, args=(task_queue, lock, i + 1, retries))
            for i in range(num_threads)
        ]
        for t in consumer_threads:
            t.start()
        for t in consumer_threads:
            t.join()

        print(
            f"✅ Finished chunk {get_id_from_filepath(chunk_files[0])} to {get_id_from_filepath(chunk_files[-1])}"
        )

        if chunk_start + chunk_size < len(files):
            print("🔁 Continuing to the next chunk...")


def get_ids_to_rescrape(
    files: List[Path],
    keys_to_check: Optional[List[str]],
    batch_size: int,
) -> List[int]:
    rescrape_ids: List[int] = []

    def batch_process(files_chunk: List[Path]) -> Generator[int, Any, None]:
        for file in files_chunk:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not data:
                    print(f"File {file} is empty or invalid. Skipping.")
                    continue

                if keys_to_check:
                    if not has_nested_key(data, keys_to_check):
                        yield get_id_from_filepath(file)
                else:
                    yield get_id_from_filepath(file)

            except Exception as e:
                print(f"⚠️ Error reading {file}: {e}")
                continue

    for i in range(0, len(files), batch_size):
        files_batch = files[i : i + batch_size]
        for file_id in batch_process(files_batch):
            rescrape_ids.append(file_id)

    return rescrape_ids


def has_nested_key(data: dict, keys: List[str]) -> bool:
    """Vérifie si des clés imbriquées existent dans un dictionnaire JSON."""
    d = data
    for key in keys:
        if isinstance(d, list):
            d = d[0] if d else {}
        if not isinstance(d, dict) or key not in d:
            return False
        d = d[key]
    return True


if __name__ == "__main__":
    main()
