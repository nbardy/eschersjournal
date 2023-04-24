from fastapi.middleware.cors import CORSMiddleware
import uuid
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import boto3
import os
import storage
import agents.core as agents
import summaries

app = FastAPI()

# USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
USE_S3 = False
if USE_S3:
    s3 = boto3.client("s3")


class RepoCreate(BaseModel):
    name: str
    topic: str


class AgentSpawn(BaseModel):
    repo_id: str
    agent_type: str


class FocusUpdate(BaseModel):
    repo_id: str
    new_focus: str


class SummaryRequest(BaseModel):
    repo_id: str


# ... (other imports)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # You can replace "*" with the specific origins you want to allow
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/create_repo/")
async def create_repo(repo_data: RepoCreate):
    repo_id = str(uuid.uuid4())

    storage.create_repo_folder(repo_id)
    storage.save_metadata(repo_id, repo_data.dict())
    storage.create_results_index(repo_id)

    agents.spawn_agents(repo_id, agents.all_types)

    return {"repo_id": repo_id}


@app.post("/spawn_on_repo/")
async def spawn_on_repo(agent_spawn: AgentSpawn):
    repo_id = agent_spawn.repo_id
    if not storage.repo_exists(repo_id):
        print("Repo not found: ", repo_id)
        raise HTTPException(status_code=404, detail="Repo not found")

    agents.spawn_agent(repo_id, agent_spawn.agent_type)

    return {"status": "agents_spawned"}


@app.get("/view_repo/{repo_id}")
async def view_repo(repo_id: str):
    if not storage.repo_exists(repo_id):
        raise HTTPException(status_code=404, detail="Repo not found")
    metadata = storage.load_metadata(repo_id)
    results = storage.load_results(repo_id)
    return {"metadata": metadata, "results": results}


@app.post("/add_new_focus/")
async def add_new_focus(focus_update: FocusUpdate):
    repo_id = focus_update.repo_id
    if not storage.repo_exists(repo_id):
        raise HTTPException(status_code=404, detail="Repo not found")
    storage.add_focus(repo_id, focus_update.new_focus)
    return {"status": "focus_added"}


@app.post("/get_summary/")
async def get_summary(summary_request: SummaryRequest):
    repo_id = summary_request.repo_id
    if not storage.repo_exists(repo_id):
        print("Repo ID: " + repo_id)
        raise HTTPException(status_code=404, detail="Repo not found")

    summary = summaries.generate_summary(repo_id)
    return summary


@app.get("/get_all_repo/")
async def get_all_repo():
    repo_ids = storage.get_all_repo_ids()
    metadata = {}
    agents_map = {}

    # load metadata file for each repo
    for repo_id in repo_ids:
        metadata[repo_id] = storage.load_metadata(repo_id)

    # Return agents running on each repo
    for id in repo_ids:
        agents_map[id] = agents.get_agents(id)

    # "Let's add results as a new field, and add results id to each agent"

    results = {}

    for id in repo_ids:
        results[id] = storage.load_results(id)

    return {
        "repo_ids": repo_ids,
        "metadata": metadata,
        "agents": agents_map,
        "results": results,
    }


# Run app on main
if __name__ == "__main__":
    import uvicorn

    # argparse dev mode default true

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    dev_mode = args.dev

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=dev_mode)
