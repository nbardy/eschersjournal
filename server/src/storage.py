import json
from pathlib import Path
import boto3
import os

import threading

local_fs_lock = threading.Lock()

BASE_DIR = "base_folder"
S3_BUCKET = "your_s3_bucket_name"

if os.getenv("USE_S3", "false").lower() == "true":
    s3 = boto3.client("s3")

local_fs_locks = {}


def _get_lock(repo_id: str, use_s3: bool) -> threading.Lock:
    return local_fs_locks.setdefault(repo_id, threading.Lock())


def create_repo_folder(repo_id: str, use_s3: bool = False):
    if use_s3:
        s3.put_object(Bucket=S3_BUCKET, Key=f"{repo_id}/")
    else:
        Path(f"{BASE_DIR}/{repo_id}").mkdir(parents=True, exist_ok=True)


def repo_exists(repo_id: str, use_s3: bool = False) -> bool:
    if use_s3:
        try:
            s3.head_object(Bucket=S3_BUCKET, Key=f"{repo_id}/")
            return True
        except s3.exceptions.ClientError as e:
            return False
    else:
        return Path(f"{BASE_DIR}/{repo_id}").exists()


def save_metadata(repo_id: str, metadata: dict, use_s3: bool = False):
    _save_to_folder(repo_id, "", json.dumps(metadata), "metadata.json", use_s3)


def load_metadata(repo_id: str, use_s3: bool = False) -> dict:
    return json.loads(_load_from_folder(repo_id, "", "metadata.json", use_s3))


def create_results_index(repo_id: str, use_s3: bool = False):
    _save_to_folder(repo_id, "results", json.dumps([]), "index.json", use_s3)


def load_results(repo_id: str, use_s3: bool = False) -> list:
    return json.loads(_load_from_folder(repo_id, "results", "index.json", use_s3))


def add_focus(repo_id: str, new_focus: str, use_s3: bool = False):
    with _get_lock(repo_id, use_s3):
        metadata = load_metadata(repo_id, use_s3)
        metadata["additional_focuses"].append(new_focus)
        save_metadata(repo_id, metadata, use_s3)


def update_results_index(repo_id: str, result_id: str, use_s3: bool = False):
    with _get_lock(repo_id, use_s3):
        results = load_results(repo_id, use_s3)
        results.append(result_id)
        create_results_index(repo_id, results, use_s3)


def _save_to_folder(repo_id: str, folder: str, content: str, filename: str, use_s3: bool = False):
    if use_s3:
        s3.put_object(Bucket=S3_BUCKET,
                      Key=f"{repo_id}/{folder}/{filename}", Body=content)
    else:
        Path(f"{BASE_DIR}/{repo_id}/{folder}/{filename}").write_text(content)


def _load_from_folder(repo_id: str, folder: str, filename: str, use_s3: bool = False) -> str:
    if use_s3:
        response = s3.get_object(
            Bucket=S3_BUCKET, Key=f"{repo_id}/{folder}/{filename}")
        return response["Body"].read().decode("utf-8")
    else:
        return Path(f"{BASE_DIR}/{repo_id}/{folder}/{filename}").read_text()
