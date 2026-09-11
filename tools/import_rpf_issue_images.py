#!/usr/bin/env python3
"""Import image attachments from RetroPiFreak GitHub Issues into NOA devlog/images.

Designed for use by a GitHub/Codex agent or a developer shell.

Examples:
    python tools/import_rpf_issue_images.py --issue 42
    python tools/import_rpf_issue_images.py --all

Authentication:
    Set RPF_READ_TOKEN to a token that can read the source repository.
    GH_TOKEN and GITHUB_TOKEN are also supported as fallbacks for local use.
    RetroPiFreak is private, so cross-repository read permission is required.

Naming:
    devlog/images/issue_042_01.png
    devlog/images/issue_042_02.jpg

A manifest is kept at devlog/images/manifest.json so reruns are idempotent and
existing image names remain stable even when an issue is edited later.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SOURCE_REPO = "microom/RetroPiFreak"
DEFAULT_OUTPUT_DIR = Path("devlog/images")
MANIFEST_NAME = "manifest.json"
USER_AGENT = "NOA-RPF-Issue-Image-Importer/1.0"

# GitHub issue uploads currently appear in a few different forms depending on
# when/how they were uploaded. Markdown image syntax is parsed first, then raw
# attachment URLs are collected as a fallback.
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+)(?:\s+\"[^\"]*\")?\)")
RAW_IMAGE_URL_RE = re.compile(
    r"https?://(?:"
    r"private-user-images\.githubusercontent\.com/[^\s)<>\"]+|"
    r"user-images\.githubusercontent\.com/[^\s)<>\"]+|"
    r"github\.com/user-attachments/assets/[^\s)<>\"]+"
    r")"
)

CONTENT_TYPE_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/svg+xml": ".svg",
    "image/tiff": ".tiff",
}


def token_from_env() -> str | None:
    return (
        os.environ.get("RPF_READ_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
    )


def token_source() -> str:
    if os.environ.get("RPF_READ_TOKEN"):
        return "RPF_READ_TOKEN"
    if os.environ.get("GH_TOKEN"):
        return "GH_TOKEN"
    if os.environ.get("GITHUB_TOKEN"):
        return "GITHUB_TOKEN"
    return "none"


def request(url: str, token: str | None, accept: str = "application/vnd.github+json") -> urllib.response.addinfourl:
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60)


def api_json(url: str, token: str | None) -> Any:
    print(f"[api] GET {url}")
    with request(url, token) as response:
        print(f"[api] OK {response.status} {response.geturl()}")
        return json.loads(response.read().decode("utf-8"))


def paginated_api(url: str, token: str | None) -> Iterable[Any]:
    page = 1
    separator = "&" if "?" in url else "?"
    while True:
        batch = api_json(f"{url}{separator}per_page=100&page={page}", token)
        if not batch:
            return
        yield from batch
        if len(batch) < 100:
            return
        page += 1


def extract_image_urls(text: str | None) -> list[str]:
    if not text:
        return []

    urls: list[str] = []
    seen: set[str] = set()

    for match in MARKDOWN_IMAGE_RE.finditer(text):
        url = match.group(1)
        if url not in seen:
            seen.add(url)
            urls.append(url)

    for match in RAW_IMAGE_URL_RE.finditer(text):
        url = match.group(0)
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def get_issue(repo: str, issue_number: int, token: str | None) -> dict[str, Any]:
    return api_json(f"https://api.github.com/repos/{repo}/issues/{issue_number}", token)


def get_issue_comments(repo: str, issue_number: int, token: str | None) -> list[dict[str, Any]]:
    return list(
        paginated_api(
            f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
            token,
        )
    )


def list_issue_numbers(repo: str, token: str | None) -> list[int]:
    result: list[int] = []
    for item in paginated_api(f"https://api.github.com/repos/{repo}/issues?state=all", token):
        # GitHub's issues endpoint also returns pull requests.
        if "pull_request" not in item:
            result.append(int(item["number"]))
    return sorted(result)


def collect_issue_image_urls(repo: str, issue_number: int, token: str | None) -> list[str]:
    print(f"#{issue_number}: fetching issue")
    issue = get_issue(repo, issue_number, token)
    body_urls = extract_image_urls(issue.get("body"))
    print(f"#{issue_number}: issue fetched; body images={len(body_urls)}")

    urls = list(body_urls)
    seen = set(urls)

    print(f"#{issue_number}: fetching comments")
    comments = get_issue_comments(repo, issue_number, token)
    print(f"#{issue_number}: comments fetched; count={len(comments)}")

    for comment_index, comment in enumerate(comments, start=1):
        comment_urls = extract_image_urls(comment.get("body"))
        if comment_urls:
            print(f"#{issue_number}: comment {comment_index} images={len(comment_urls)}")
        for url in comment_urls:
            if url not in seen:
                seen.add(url)
                urls.append(url)

    print(f"#{issue_number}: total unique images={len(urls)}")
    for image_index, url in enumerate(urls, start=1):
        print(f"#{issue_number}: image {image_index}: {url}")

    return urls


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "source_repo": DEFAULT_SOURCE_REPO, "assets": {}}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("version", 1)
    data.setdefault("assets", {})
    return data


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def next_ordinal(manifest: dict[str, Any], issue_number: int) -> int:
    prefix = f"issue_{issue_number:03d}_"
    ordinals: list[int] = []
    for entry in manifest.get("assets", {}).values():
        name = str(entry.get("file", ""))
        if name.startswith(prefix):
            match = re.match(rf"{re.escape(prefix)}(\d+)", name)
            if match:
                ordinals.append(int(match.group(1)))
    return max(ordinals, default=0) + 1


def extension_from_url_or_content_type(url: str, content_type: str | None) -> str:
    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".tif", ".tiff"}:
        return ".jpg" if suffix == ".jpeg" else suffix

    if content_type:
        content_type = content_type.split(";", 1)[0].strip().lower()
        if content_type in CONTENT_TYPE_EXTENSIONS:
            return CONTENT_TYPE_EXTENSIONS[content_type]
        guessed = mimetypes.guess_extension(content_type)
        if guessed:
            return guessed

    return ".bin"


def download(url: str, token: str | None) -> tuple[bytes, str | None, str]:
    # urllib follows GitHub redirects. Keep authentication for the initial request;
    # signed private-user-images URLs generally authorize the redirected download.
    print(f"[download] GET {url}")
    with request(url, token, accept="image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8") as response:
        data = response.read()
        content_type = response.headers.get("Content-Type")
        final_url = response.geturl()
        print(
            f"[download] OK {response.status}; final_url={final_url}; "
            f"content_type={content_type!r}; bytes={len(data)}"
        )
    return data, content_type, final_url


def print_http_error(exc: urllib.error.HTTPError) -> None:
    content_type = exc.headers.get("Content-Type") if exc.headers else None
    location = exc.headers.get("Location") if exc.headers else None
    print(
        f"GitHub HTTP error {exc.code}: url={exc.geturl()} reason={exc.reason!r} "
        f"content_type={content_type!r} location={location!r}",
        file=sys.stderr,
    )

    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception as body_exc:
        print(f"response body could not be read: {body_exc}", file=sys.stderr)
        return

    # HTML error pages can be very large and add little signal to Actions logs.
    # Keep only a compact preview while preserving JSON/API error details.
    preview = body.strip().replace("\r", "")[:1200]
    if preview:
        print("response body preview:", file=sys.stderr)
        print(preview, file=sys.stderr)
        if len(body.strip()) > len(preview):
            print("... [truncated]", file=sys.stderr)


def import_issue(
    repo: str,
    issue_number: int,
    output_dir: Path,
    manifest: dict[str, Any],
    token: str | None,
    overwrite: bool,
    dry_run: bool,
) -> tuple[int, int]:
    urls = collect_issue_image_urls(repo, issue_number, token)
    if not urls:
        print(f"#{issue_number}: no images")
        return 0, 0

    imported = 0
    skipped = 0
    assets: dict[str, Any] = manifest.setdefault("assets", {})

    for image_index, url in enumerate(urls, start=1):
        existing = assets.get(url)
        if existing:
            target = output_dir / existing["file"]
            if target.exists() and not overwrite:
                print(f"#{issue_number}: skip existing {target}")
                skipped += 1
                continue

        print(f"#{issue_number}: downloading image {image_index}/{len(urls)}")
        try:
            data, content_type, final_url = download(url, token)
        except urllib.error.HTTPError as exc:
            print(
                f"#{issue_number}: image {image_index}/{len(urls)} download failed; source_url={url}",
                file=sys.stderr,
            )
            raise

        if existing:
            filename = existing["file"]
        else:
            ordinal = next_ordinal(manifest, issue_number)
            ext = extension_from_url_or_content_type(final_url, content_type)
            filename = f"issue_{issue_number:03d}_{ordinal:02d}{ext}"

        target = output_dir / filename
        print(f"#{issue_number}: {'would write' if dry_run else 'write'} {target} ({len(data)} bytes)")

        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            if target.exists() and not overwrite and not existing:
                raise RuntimeError(f"Refusing to overwrite existing file: {target}")
            target.write_bytes(data)
            assets[url] = {
                "file": filename,
                "issue": issue_number,
                "source_url": url,
            }
            imported += 1

    return imported, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", default=DEFAULT_SOURCE_REPO, help="owner/repo to read Issues from")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--issue", type=int, action="append", help="Issue number to import (repeatable)")
    parser.add_argument("--all", action="store_true", help="Scan all Issues")
    parser.add_argument("--overwrite", action="store_true", help="Replace files already recorded in the manifest")
    parser.add_argument("--dry-run", action="store_true", help="Inspect/download but do not write files or manifest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.all and not args.issue:
        print("Specify --issue N (repeatable) or --all", file=sys.stderr)
        return 2

    token = token_from_env()
    print(f"auth: token source={token_source()}")
    if not token:
        print(
            "warning: RPF_READ_TOKEN/GH_TOKEN/GITHUB_TOKEN is not set; this will fail for private repositories",
            file=sys.stderr,
        )

    print(
        f"run: source_repo={args.source_repo} output_dir={args.output_dir} "
        f"issues={args.issue or 'ALL'} dry_run={args.dry_run} overwrite={args.overwrite}"
    )

    manifest_path = args.output_dir / MANIFEST_NAME
    manifest = load_manifest(manifest_path)
    manifest["source_repo"] = args.source_repo

    try:
        issue_numbers = list_issue_numbers(args.source_repo, token) if args.all else sorted(set(args.issue or []))
        total_imported = 0
        total_skipped = 0

        for issue_number in issue_numbers:
            imported, skipped = import_issue(
                args.source_repo,
                issue_number,
                args.output_dir,
                manifest,
                token,
                args.overwrite,
                args.dry_run,
            )
            total_imported += imported
            total_skipped += skipped

        if not args.dry_run:
            save_manifest(manifest_path, manifest)

        print(f"done: imported={total_imported}, skipped={total_skipped}, issues={len(issue_numbers)}")
        return 0

    except urllib.error.HTTPError as exc:
        print_http_error(exc)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
