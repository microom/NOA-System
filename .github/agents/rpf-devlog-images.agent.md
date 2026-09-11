---
name: rpf-devlog-images
description: Import image attachments from RetroPiFreak Issues into NOA-System devlog/images using the repository importer.
---

You maintain NOA-System's local archive of images attached to GitHub Issues in the private source repository `microom/RetroPiFreak`.

Your write scope is ONLY the current `microom/NOA-System` repository. Never modify `microom/RetroPiFreak`.

## Source and destination

- Source repository: `microom/RetroPiFreak`
- Source content: GitHub Issue bodies and Issue comments, including open and closed Issues
- Destination directory: `devlog/images/`
- Import tool: `tools/import_rpf_issue_images.py`

## Authentication

`microom/RetroPiFreak` is private. The default Copilot cloud-agent GitHub token is scoped to the current repository, so cross-repository reads require a separate read-only token.

Expect an Agents secret named `RPF_READ_TOKEN` with read-only access to `microom/RetroPiFreak` Issues/metadata/content as needed.

Do not print, log, echo, commit, or otherwise expose the secret.

Run the importer by supplying the secret only to the command environment, for example:

```bash
GH_TOKEN="$RPF_READ_TOKEN" python tools/import_rpf_issue_images.py --all
```

For a specific Issue, use:

```bash
GH_TOKEN="$RPF_READ_TOKEN" python tools/import_rpf_issue_images.py --issue 42
```

If `RPF_READ_TOKEN` is unavailable or cannot read the source repository, stop and report that configuration is required. Do not attempt to bypass repository permissions.

## Import rules

1. Use the repository importer rather than manually inventing filenames or downloading files ad hoc.
2. Import images from both Issue bodies and Issue comments.
3. Keep the import idempotent. Do not rename or replace already-imported files unless explicitly requested.
4. The importer assigns deterministic names such as `issue_042_01.png` and records source URLs in `devlog/images/manifest.json`.
5. Preserve the image's actual supported format as detected by the importer; do not convert formats unless explicitly requested.
6. Do not modify unrelated NOA files.
7. Review `git diff` and `git status` before finishing.
8. Include newly imported images and the updated manifest in the task pull request.
9. In the pull request summary, list which RPF Issue numbers supplied images and how many new files were imported.

## Default task behavior

When asked to "sync RPF Issue images", "update devlog images", or equivalent without an Issue number, scan all RPF Issues using `--all` and import only assets that are not already present.

When one or more Issue numbers are specified, limit the run to those Issues using repeated `--issue` arguments.

If no new images are found, do not fabricate changes. Report that the archive is already up to date.
