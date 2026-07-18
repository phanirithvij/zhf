#!/usr/bin/env python3
import json
import os
import git
import subprocess
import sys
from pathlib import Path


def clone_nixpkgs(rev, nixos):
    owd = os.getcwd()
    if not os.path.exists("data/nixpkgs"):
        os.makedirs("data/nixpkgs")
    os.chdir("data/nixpkgs")
    repo = git.Repo.init()
    try:
        origin = repo.create_remote("origin", "https://github.com/NixOS/nixpkgs.git")
    except:
        # remote already exists
        origin = repo.remotes.origin
        origin.set_url("https://github.com/NixOS/nixpkgs.git")
    print(f"Cloning revision {rev} into data/nixpkgs...")
    origin.fetch(refspec=rev)
    repo.git.reset(rev, hard=True)
    if nixos:
        print(
            "Applying do_not_remove_maintainers.patch to nixos/release-combined.nix..."
        )
        repo.git.apply(f"{owd}/scripts/do_not_remove_maintainers.patch")
    os.chdir(owd)


def batch_evaluate(jobs, is_nixos):
    file_to_evaluate = "./data/nixpkgs/nixos/release-combined.nix" if is_nixos else "./data/nixpkgs/pkgs/top-level/release.nix"
    expr = f"let jobs = import {file_to_evaluate}; in {{\n"
    for job_name in jobs:
        real_job_name = job_name if is_nixos else ".".join(job_name.split(".")[1:])
        path_expr = ".".join(f'"{p}"' for p in real_job_name.split("."))
        expr += f'  "{job_name}" = let m = builtins.tryEval (jobs.{path_expr}.meta or {{}}); in if m.success then {{ maintainers = m.value.maintainers or []; teams = m.value.teams or []; }} else {{ maintainers = []; teams = []; }};\n'
    expr += "}\n"
    with open("batch.nix", "w") as f:
        f.write(expr)
    try:
        r = subprocess.check_output("nix eval --json -f batch.nix 2> /dev/null", shell=True).decode("utf-8")
        return json.loads(r)
    except Exception as e:
        print(f"Batch evaluation failed: {e}")
        return {}


def main(evals):
    for ev in evals:
        eval_id, commit_hash, is_nixos = ev
        
        # Determine paths
        evalcache_path = f"data/evalcache/{eval_id}.cache"
        maintainerscache_path = f"data/maintainerscache/{eval_id}.cache"
        
        if not os.path.exists(evalcache_path):
            continue

        if os.path.exists(maintainerscache_path):
            print(f"Maintainers for evaluation {eval_id} are already cached")
            continue

        clone_nixpkgs(commit_hash, is_nixos)
        
        jobs_info = {}
        with open(evalcache_path) as f:
            for line in f.readlines():
                status = line.split(" ")
                if "failed" in status[-1].strip().lower():
                    job_name = status[0].strip()
                    if not is_nixos:
                        job_name = f"nixpkgs.{job_name}"
                    jobs_info[job_name] = status[1:]
        
        jobs_to_eval = list(jobs_info.keys())
        if not jobs_to_eval:
            Path(maintainerscache_path).touch()
            continue

        res = {}
        # Batch in chunks of 500
        chunk_size = 500
        for i in range(0, len(jobs_to_eval), chunk_size):
            chunk = jobs_to_eval[i:i+chunk_size]
            print(f"Evaluating batch {i//chunk_size + 1}/{(len(jobs_to_eval) + chunk_size - 1)//chunk_size}...")
            batch_res = batch_evaluate(chunk, is_nixos)
            for k, v in batch_res.items():
                maintainers = v.get("maintainers", [])
                teams = v.get("teams", [])
                for t in teams:
                    if "shortName" in t:
                        maintainers.append({"github": "team_" + t["shortName"].lower()})
                res[k] = maintainers
            
            # If batch failed completely, mark as error
            if not batch_res:
                for k in chunk:
                    res[k] = ["error"]

        with open(maintainerscache_path, "a") as f:
            for k, v in res.items():
                if not v or v == ["error"]:
                    f.write(f"_ {k} {' '.join(jobs_info[k])}")
                else:
                    for maint in v:
                        if "github" in maint:
                            f.write(f"{maint['github']} {k} {' '.join(jobs_info[k])}")
                        else:
                            f.write(f"_ {k} {' '.join(jobs_info[k])}")


if __name__ == "__main__":
    args = sys.argv[1:]
    to_pass = []
    while args:
        eval_id = args.pop(0)
        commit_hash = args.pop(0)
        is_nixos = args.pop(0) == "1"
        to_pass += [(eval_id, commit_hash, is_nixos)]
    main(to_pass)
