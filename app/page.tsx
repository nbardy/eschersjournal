import "./page.css";
import { Dashboard } from "./components/dashboard";

export const runtime = "edge";

export const defaultRepoName = "default_repo";
export default async function Page() {
  return <Dashboard repo={defaultRepoName} />;
}

// is defined takes a list of values or one or many as args
// e.g. isDefined(x, y, z) or assertDefined(x) or assertDefined([x, y, z])
// Will true if all values are defined and false otherwise
