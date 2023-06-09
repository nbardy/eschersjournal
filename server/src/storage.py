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


# def load_results(repo_id: str) -> list:
#     return json.loads(_load_from_folder(repo_id, "results", "index.json"))

def _exists_in_folder(repo_id: str, folder: str, filename: str) -> bool:
    if use_s3:
        try:
            s3.head_object(Bucket=S3_BUCKET,
                           Key=f"{repo_id}/{folder}/{filename}")
            return True
        except s3.exceptions.ClientError as e:
            return False
    else:
        return Path(f"{BASE_DIR}/{repo_id}/{folder}/{filename}").exists()


def load_results(repo_id: str) -> list:
    # check if exists
    if _exists_in_folder(repo_id, "results", "index.json"):
        return json.loads(_load_from_folder(repo_id, "results", "index.json"))
    else:
        print(f"WARNING: results index for {repo_id} does not exist")
        return []

    # fault tolerance for missing file throw warning and return empty results


def add_focus(repo_id: str, new_focus: str):
    with _get_lock(repo_id):
        metadata = load_metadata(repo_id)
        metadata["additional_focuses"].append(new_focus)
        save_metadata(repo_id, metadata)


def create_log_folder_for_agent(repo_id: str, agent_id: str):
    return _mkdir(repo_id, f"agents/{agent_id}/logs")


def save_and_upload_agent_result(repo_id: str, agent_id: str, job_id: str, content: str, filename: str):
    _save_to_folder(repo_id, f"results/{agent_id}/{job_id}",
                    content, filename)
    update_repo_results_index(repo_id, agent_id, job_id)


def update_repo_results_index(repo_id: str, agent_id: str, job_id: str):
    with _get_lock(repo_id):
        results = load_results(repo_id)
        results.append(f"{agent_id}/{job_id}")
        _save_to_folder(repo_id, "results", json.dumps(results), "index.json")


def get_all_repo_ids() -> list:
    if use_s3:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        return [content["Key"].split("/")[0] for content in response["Contents"]]
    else:
        return [repo.name for repo in Path(BASE_DIR).iterdir() if repo.is_dir()]


def _mkdir(repo_id: str, folder: str):
    full_path = f"{BASE_DIR}/{repo_id}/{folder}"
    if use_s3:
        s3.put_object(Bucket=S3_BUCKET,
                      Key=f"{repo_id}/{folder}/")

    else:
        Path(full_path).mkdir(parents=True, exist_ok=True)

    return full_path


def _save_to_folder(repo_id: str, folder: str, content: str, filename: str):
    _mkdir(repo_id, folder)
    if use_s3:
        s3.put_object(Bucket=S3_BUCKET,
                      Key=f"{repo_id}/{folder}/{filename}",
                      Body=content.encode("utf-8"))
    else:
        Path(f"{BASE_DIR}/{repo_id}/{folder}/{filename}").write_text(content)


def _load_from_folder(repo_id: str, folder: str, filename: str) -> str:
    if use_s3:
        response = s3.get_object(
            Bucket=S3_BUCKET, Key=f"{repo_id}/{folder}/{filename}")
        return response["Body"].read().decode("utf-8")
    else:
        return Path(f"{BASE_DIR}/{repo_id}/{folder}/{filename}").read_text()


def save_and_upload_file(repo_id: str, content: str, filename: str):
    _save_to_folder(repo_id, "results", content, filename)


# job: json
def save_pending_job(repo_id: str, job: dict):
    _save_to_folder(repo_id, "pending_jobs",
                    json.dumps(job), f"{job['job_id']}.json")


def get_pending_job(repo_id: str, job_id: str) -> dict:
    # if no such file or direcotry error, return empty list
    try:
        jobs = json.loads(_load_from_folder(
            repo_id, "pending_jobs", f"{job_id}.json"))
    except FileNotFoundError:
        jobs = []

    return jobs


# def get_pending_jobs(repo_id: str) -> list:
#     if use_s3:
#         response = s3.list_objects_v2(
#             Bucket=S3_BUCKET, Prefix=f"{repo_id}/pending_jobs/")
#         return [content["Key"].split("/")[-1].split(".")[0] for content in response["Contents"]]
#     else:
#         return [job.name.split(".")[0] for job in Path(f"{BASE_DIR}/{repo_id}/pending_jobs").iterdir() if job.is_file()]

# Redo this to also support a non existent folder
def get_pending_jobs(repo_id: str) -> list:
    if use_s3:
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET, Prefix=f"{repo_id}/pending_jobs/")
        return [content["Key"].split("/")[-1].split(".")[0] for content in response["Contents"]]
    else:
        try:
            return [job.name.split(".")[0] for job in Path(f"{BASE_DIR}/{repo_id}/pending_jobs").iterdir() if job.is_file()]
        except FileNotFoundError:
            return []
