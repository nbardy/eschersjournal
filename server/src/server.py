import uuid
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import boto3
import os
import storage
import agents
import summaries

app = FastAPI()

USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
if USE_S3:
    s3 = boto3.client("s3")


class RepoCreate(BaseModel):
    topic: str
    additional_focuses: List[str]


class AgentSpawn(BaseModel):
    repo_id: str


class FocusUpdate(BaseModel):
    repo_id: str
    new_focus: str


class SummaryRequest(BaseModel):
    repo_id: str


@app.post("/create_repo/")
async def create_repo(repo_data: RepoCreate):
    repo_id = str(uuid.uuid4())
    storage.create_repo_folder(repo_id, use_s3=USE_S3)
    storage.save_metadata(repo_id, repo_data.dict(), use_s3=USE_S3)
    storage.create_results_index(repo_id, use_s3=USE_S3)
    agents.spawn_agents(repo_id)
    return {"repo_id": repo_id}


@app.post("/spawn_on_repo/")
async def spawn_on_repo(agent_spawn: AgentSpawn):
    repo_id = agent_spawn.repo_id
    if not storage.repo_exists(repo_id, use_s3=USE_S3):
        raise HTTPException(status_code=404, detail="Repo not found")
    agents.spawn_agents(repo_id)
    return {"status": "agents_spawned"}


@app.get("/view_repo/{repo_id}")
async def view_repo(repo_id: str):
    if not storage.repo_exists(repo_id, use_s3=USE_S3):
        raise HTTPException(status_code=404, detail="Repo not found")
    metadata = storage.load_metadata(repo_id, use_s3=USE_S3)
    results = storage.load_results(repo_id, use_s3=USE_S3)
    return {"metadata": metadata, "results": results}


@app.post("/add_new_focus/")
async def add_new_focus(focus_update: FocusUpdate):
    repo_id = focus_update.repo_id
    if not storage.repo_exists(repo_id, use_s3=USE_S3):
        raise HTTPException(status_code=404, detail="Repo not found")
    storage.add_focus(repo_id, focus_update.new_focus, use_s3=USE_S3)
    return {"status": "focus_added"}


@app.post("/get_summary/")
async def get_summary(summary_request: SummaryRequest):
    repo_id = summary_request.repo_id
    if not storage.repo_exists(repo_id, use_s3=USE_S3):
        raise HTTPException(status_code=404, detail="Repo not found")
    summary = summaries.generate_summary(repo_id, use_s3=USE_S3)
    return summary
