"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { REPL_MODE_SLOPPY } from "repl";
import {
  spawnOnRepo,
  RepoCreate,
  createRepo,
  getAllRepo,
} from "../api/model_server";

function useQueryFn<T>(
  fn: () => Promise<T>,
  opts: { pollOps: { ms: number } }
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [loading, setLoading] = useState(true);

  const queryFn = useCallback(() => {
    fn()
      .then((response) => {
        setData(response);
      })
      .catch((error) => {
        setError(error);
      });

    setLoading(false);
  }, [fn]);

  // poll
  useEffect(() => {
    if (opts.pollOps) {
      const interval = setInterval(() => {
        queryFn();
      }, opts.pollOps.ms);

      return () => clearInterval(interval);
    } else {
      queryFn();
    }
  }, [opts.pollOps, queryFn]);

  // This will minimize the number of times the consumer component re-renders
  const resultMemo = useMemo(() => {
    const result = [data, loading, error] as const;

    return result;
  }, [data, loading, error]);

  return resultMemo;
}

const available_agent_types = [
  "vis_critic_agent",
  "research_agent",
  "vis_programmer",
];

interface DashboardProps {
  repo: string;
}

interface RepoData {
  agents: AgentData[];
  resultData: ResultData[];
}

interface AgentData {
  name: string;
  status: string;
  lastSeen: string;
  results: string[];
}

interface ResultData {
  name: string;
  file: string;
}

// helper functions
const createAndSpawn = async (
  name: string | null | undefined,
  topic: string | null | undefined
) => {
  if (name == null || topic == null) {
    return;
  }

  const repoData: RepoCreate = {
    name: name,
    topic: topic,
  };
  const response = await createRepo(repoData);

  await Promise.all(
    available_agent_types.map(async (agentType) => {
      await spawnOnRepo({
        repo_id: response.repo_id,
        agent_type: agentType,
      });
    })
  );

  return response;
};

const allPollOps = { ms: 200 };

export function Dashboard(dashboardProps: DashboardProps) {
  const textareaRefName = useRef<HTMLTextAreaElement>(null);
  const textareaRefTopic = useRef<HTMLTextAreaElement>(null);

  const [currentRepoId, setCurrentRepoId] = useState("fakeRepo");

  // poll and store state for get all repo

  const [repoData, repoDataLoading, repoFetchError] = useQueryFn(getAllRepo, {
    pollOps: allPollOps,
  });

  const currentRepoMetadata = repoData?.metadata[currentRepoId] ?? [];
  const currentRepoAgents = repoData?.agents[currentRepoId] ?? [];
  const currentRepoResultData = repoData?.results[currentRepoId] ?? [];

  return (
    <div>
      <h1>Dashboard</h1>
      <div>
        <h2>Repos</h2>
        {repoData != null &&
          repoData.repo_ids.map((repoId, i) => {
            const metadata = repoData.metadata[repoId];
            return (
              <div key={i}>
                {metadata.name}
                {/* set current on click */}
                <button onClick={() => setCurrentRepoId(repoId)}>
                  Make Active
                </button>
              </div>
            );
          })}
        <h4>New Repo</h4>
        <div>
          <div>
            <label>Name</label>
            <textarea
              className="textarea-input text-input-name"
              ref={textareaRefName}
            ></textarea>
            <label>Topic</label>
            <textarea
              className="textarea-input text-input-topic"
              ref={textareaRefTopic}
            ></textarea>
            <button
              onClick={() =>
                createAndSpawn(
                  textareaRefName.current?.value,
                  textareaRefTopic.current?.value
                )
              }
            >
              Create Repo
            </button>
          </div>
        </div>
      </div>
      <h2>Current Repo: {currentRepoId}</h2>
      <h2>Agents</h2>
      {available_agent_types.map((agentType) => {
        return (
          <button
            key={agentType}
            onClick={() => {
              spawnOnRepo({ repo_id: currentRepoId, agent_type: agentType });
            }}
          >
            Spawn
          </button>
        );
      })}
      <div className="agents">
        {Object.values(currentRepoAgents).map((agent, i) => (
          <div className="agent" key={i}>
            <div className="info">
              <div>
                {"no name todo"}
                {/* if status == "online" do a green emoji or red otherwise and print status */}
                <span>
                  {agent.status === "online" ? (
                    <span role="img" aria-label="online">
                      ✅
                    </span>
                  ) : (
                    <span role="img" aria-label="offline">
                      ❌
                    </span>
                  )}
                </span>
              </div>
              {/* <div>{agent.lastSeen}</div> */}
            </div>
            {/* <h3>Results</h3>
            {agent.results
              ?.map((resultName, i) => {
                return getResultByName(resultName, currentRepoMetadat);
              })
              .filter((result): result is ResultData => !!result)
              .map((result) => {
                return (
                  <div className="result" key={i}>
                    <div>{result.name}</div>
                    <div>{result.file}</div>
                  </div>
                );
              })} */}
          </div>
        ))}
        <h3>Results</h3>
        {currentRepoResultData.map((result: any, i) => {
          return (
            <div className="result" key={i}>
              <div>{result.name}</div>
              <div>{result.file}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export const fakeRepoData = (): RepoData => {
  return {
    agents: [
      {
        name: "agent1",
        status: "online",
        lastSeen: "2021-01-01",
        results: ["result1", "result2"],
      },
      {
        name: "agent2",
        status: "online",
        lastSeen: "2021-01-01",
        results: [],
      },
    ],
    resultData: [
      {
        name: "result1",
        file: "file1",
      },
      {
        name: "result2",
        file: "file2",
      },
    ],
  };
};
