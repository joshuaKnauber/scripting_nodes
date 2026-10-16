---
name: build
description: Package a Scripting Nodes zip to share (test build, beta build, build for testers). Use when asked for "a build", "a new build", "a beta build", "a zip for testers". Packaging only, no tests or validation.
---

# Build

Run from the repo root:

```bash
python3 scripts/share_build.py          # scripting_nodes-<version>.zip
python3 scripts/share_build.py --beta   # scripting_nodes-<version>-beta.zip
```

- Add `--beta` whenever the user mentions "beta". Otherwise build without it.
- `--version X.Y.Z` only if the user asks for a specific version. The default is the version in `addon/scripting_nodes/blender_manifest.toml`.
- Don't run tests, validation or install checks. This is packaging only.

The script builds from the last commit (HEAD) in a temp copy, so the checkout and its manifest stay untouched. It leaves out features listed in `LEFT_OUT` in the script (currently the data explorer) and copies the zip to `builds/` and `~/Desktop`, replacing an older zip of the same name.

Report back: the zip path on the Desktop, the commit it was built from, and what was left out. If the script prints that there are uncommitted changes, say that they aren't in the build.
