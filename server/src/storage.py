import json
from pathlib import Path
import boto3
import os

import threading

local_fs_lock = threading.Lock()

BASE_DIR = "base_folder"
S3_BUCKET = "your_s3_bucket_name"

use_s3 = False

local_fs_locks = {}

s3 = None


def enable_s3():
    global use_s3
    use_s3 = True

    if s3 is None:
        s3 = boto3.client("s3")


def disable_s3():
    global use_s3
    use_s3 = False


# Locks on a repo
def _get_lock(repo_id: str) -> threading.Lock:
    return local_fs_locks.setdefault(repo_id, threading.Lock())


def create_repo_folder(repo_id: str):
    if use_s3:
        s3.put_object(Bucket=S3_BUCKET, Key=f"{repo_id}/")
    else:
        Path(f"{BASE_DIR}/{repo_id}").mkdir(parents=True, exist_ok=True)


def repo_exists(repo_id: str) -> bool:
    if use_s3:
        try:
            s3.head_object(Bucket=S3_BUCKET, Key=f"{repo_id}/")
            return True
        except s3.exceptions.ClientError as e:
            return False
    else:
        return Path(f"{BASE_DIR}/{repo_id}").exists()


def save_metadata(repo_id: str, metadata: dict):
    _save_to_folder(repo_id, "", json.dumps(metadata), "metadata.json")


def load_metadata(repo_id: str) -> dict:
    return json.loads(_load_from_folder(repo_id, "", "metadata.json"))


def create_results_index(repo_id: str):
    _save_to_folder(repo_id, "results", json.dumps([]), "index.json")


def load_results(repo_id: str) -> list:
    return json.loads(_load_from_folder(repo_id, "results", "index.json"))


def add_focus(repo_id: str, new_focus: str):
    with _get_lock(repo_id):
        metadata = load_metadata(repo_id)
        metadata["additional_focuses"].append(new_focus)
        save_metadata(repo_id, metadata)


def update_results_index(repo_id: str, job_id: str):
    with _get_lock(repo_id):
        results = load_results(repo_id)
        results.append(job_id)
        _save_to_folder(repo_id, "results", json.dumps(results), "index.json")


def update_repo_results_index(repo_id: str, job_id: str):
    with _get_lock(repo_id):
        results = load_results(repo_id)
        results.append(job_id)
        _save_to_folder(repo_id, "results", json.dumps(results), "index.json")


def save_and_upload_agent_result(repo_id: str, agent_id: str, job_id: str, content: str, filename: str):
    _save_to_folder(repo_id, f"results/{agent_id}/{job_id}",
                    content, filename)


def get_all_repo_ids() -> list:
    if use_s3:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        return [content["Key"].split("/")[0] for content in response["Contents"]]
    else:
        return [repo.name for repo in Path(BASE_DIR).iterdir() if repo.is_dir()]


def _save_to_folder(repo_id: str, folder: str, content: str, filename: str):
    if use_s3:
        s3.put_object(Bucket=S3_BUCKET,
                      Key=f"{repo_id}/{folder}/{filename}", Body=content)
    else:
        folder_path = Path(f"{BASE_DIR}/{repo_id}/{folder}")
        folder_path.mkdir(exist_ok=True)
        Path(f"{folder_path}/{filename}").write_text(content)


def _load_from_folder(repo_id: str, folder: str, filename: str) -> str:
    if use_s3:
        response = s3.get_object(
            Bucket=S3_BUCKET, Key=f"{repo_id}/{folder}/{filename}")
        return response["Body"].read().decode("utf-8")
    else:
        return Path(f"{BASE_DIR}/{repo_id}/{folder}/{filename}").read_text()


def save_and_upload_file(repo_id: str, content: str, filename: str):
    _save_to_folder(repo_id, "results", content, filename)
