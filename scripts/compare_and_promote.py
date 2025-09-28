import json, os, sys
from pathlib import Path
import yaml

def load_json(p: Path, default=None):
    if not p.exists():
        return {} if default is None else default
    with open(p, "r") as f:
        return json.load(f)

def write_json(p: Path, data: dict):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)

def main():
    gates = yaml.safe_load(open("configs/gates.yaml"))
    primary = gates["primary_metric"]                # "test_accuracy"
    min_delta = float(gates["rules"]["min_delta"])   # e.g., 0.002

    # new metrics from Phase 4
    new_metrics_path = Path("artifacts/metrics.json")
    if not new_metrics_path.exists():
        print("ERROR: artifacts/metrics.json not found; run evaluate first", file=sys.stderr)
        sys.exit(2)
    new_metrics = load_json(new_metrics_path)
    if primary not in new_metrics:
        print(f"ERROR: {primary} not found in metrics.json", file=sys.stderr)
        sys.exit(2)

    new_val = float(new_metrics[primary])
    new_run = new_metrics.get("run_id") or os.getenv("GITHUB_SHA", "local")

    # current production
    manifest_path = Path("registry/production/manifest.json")
    manifest = load_json(manifest_path, default={"run_id": None, primary: -1.0})
    prod_val = float(manifest.get(primary, -1.0))
    prod_run = manifest.get("run_id")

    should_deploy = new_val >= (prod_val + min_delta)
    print(f"[gate] prod {primary}={prod_val:.6f} (run={prod_run}) | new {primary}={new_val:.6f} (run={new_run}) | min_delta={min_delta:.6f} => deploy={should_deploy}")

    # expose decision to GitHub Actions
    out = os.getenv("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"should_deploy={'true' if should_deploy else 'false'}\n")

    # If better, update manifest.json (promotion)
    if should_deploy:
        write_json(manifest_path, {"run_id": new_run, primary: new_val})
        print(f"[gate] promoted run_id={new_run} with {primary}={new_val:.6f} -> {manifest_path}")

    # Exit 0 either way; the workflow uses the output to gate deploy
    sys.exit(0)

if __name__ == "__main__":
    main()
