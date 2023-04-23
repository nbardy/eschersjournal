import { SingletonRouter } from "next/router";

// api.ts
export interface RepoCreate {
  name: string;
  topic: string;
}

export interface AgentSpawn {
  repo_id: string;
}

export interface FocusUpdate {
  repo_id: string;
  new_focus: string;
}

export interface SummaryRequest {
  repo_id: string;
}

const serverBase = "http://localhost:8000";
export async function createRepo(
  repoData: RepoCreate
): Promise<{ repo_id: string }> {
  const response = await fetch(serverBase + "/create_repo/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(repoData),
  });

  return await response.json();
}

export async function spawnOnRepo(
  agentSpawn: AgentSpawn
): Promise<{ status: string }> {
  const response = await fetch(serverBase + "/spawn_on_repo/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(agentSpawn),
  });

  return await response.json();
}

export async function viewRepo(
  repoId: string
): Promise<{ metadata: any; results: any }> {
  const response = await fetch(serverBase + `/view_repo/${repoId}`);
  return await response.json();
}

export async function addNewFocus(
  focusUpdate: FocusUpdate
): Promise<{ status: string }> {
  const response = await fetch(serverBase + "/add_new_focus/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(focusUpdate),
  });

  return await response.json();
}

export async function getSummary(summaryRequest: SummaryRequest): Promise<any> {
  const response = await fetch(serverBase + "/get_summary/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(summaryRequest),
  });

  return await response.json();
}

interface AllRepoInfo {
  repo_ids: Array<string>;
  metadata: Record<string, { name: string; topic: string }>;
  agents: Record<string, Array<{ status: string }>>;
}

export async function getAllRepo(): Promise<AllRepoInfo> {
  const response = await fetch(serverBase + "/get_all_repo/");
  return await response.json();
}
