import json, sys, os
src, out = sys.argv[1], sys.argv[2]
v = json.load(open(src))
for k in ("bins", "events", "qc"):
    open(os.path.join(out, f"grid_{k}.csv"), "w").write(v[k] + "\n")
print({k: v[k].count("\n") for k in v})
