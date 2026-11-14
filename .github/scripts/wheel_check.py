"""Detect stale published wheels and cibuildwheel pins.

Exit codes:
  0 = everything current
  1 = drift detected (prints details)
  2 = could not complete the check (e.g. PyPI unreachable); not a drift signal

Checked weekly by .github/workflows/wheel-check.yml. See issue #8.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYPI_JSON = "https://pypi.org/pypi/{name}/json"

# A release must provide at least one wheel matching each platform family for
# every supported CPython minor. Substrings are matched against wheel filenames.
PLATFORM_CHECKS = {
    "Windows (win_amd64)": "win_amd64",
    "macOS (universal2/arm64/x86_64)": ("universal2", "arm64", "x86_64"),
    "Linux (manylinux x86_64)": "manylinux",
}


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.load(resp)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        print(f"ERROR: could not fetch {url}: {exc}", file=sys.stderr)
        print(
            "This is a connectivity/API failure, not a drift signal; "
            "re-run the check.",
            file=sys.stderr,
        )
        sys.exit(2)


def supported_python_versions():
    text = (ROOT / "setup.cfg").read_text(encoding="utf-8")
    versions = re.findall(r"Programming Language :: Python :: (3\.\d+)", text)
    return sorted(set(versions), key=lambda v: tuple(int(p) for p in v.split(".")))


def pinned_cibuildwheel():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    match = re.search(r"pypa/cibuildwheel@(v[0-9][^\s]*)", text)
    return match.group(1) if match else None


def has_platform_wheel(filename, cp_version, platform):
    tag = "cp" + cp_version.replace(".", "")
    if not filename.startswith(f"unishox2_py3-"):
        return False
    if not re.search(rf"-{tag}-{tag}-", filename):
        return False
    needles = platform if isinstance(platform, tuple) else (platform,)
    return any(n in filename for n in needles)


def main():
    name = "unishox2-py3"
    data = fetch_json(PYPI_JSON.format(name=name))
    version = data["info"]["version"]
    filenames = [f["filename"] for f in data["urls"]]
    has_sdist = any(f.endswith(".tar.gz") for f in filenames)

    problems = []

    if not has_sdist:
        problems.append(f"{name} {version} has no sdist on PyPI")

    for py in supported_python_versions():
        for label, needle in PLATFORM_CHECKS.items():
            if not any(has_platform_wheel(f, py, needle) for f in filenames):
                problems.append(
                    f"{name} {version}: missing CPython {py} wheel for {label}"
                )

    pinned = pinned_cibuildwheel()
    if pinned is None:
        problems.append("could not find a pypa/cibuildwheel pin in ci.yml")
    else:
        latest = fetch_json(PYPI_JSON.format(name="cibuildwheel"))["info"]["version"]
        if pinned.lstrip("v") != latest:
            problems.append(
                f"cibuildwheel pin is {pinned} but latest on PyPI is {latest}; "
                "new CPython versions may not be buildable"
            )

    if problems:
        print(f"DRIFT DETECTED for {name} {version}:")
        for p in problems:
            print(f"  - {p}")
        print(
            "\nRe-publish with a current cibuildwheel pin, or manually dispatch "
            "the ci workflow, to restore wheel coverage."
        )
        return 1

    print(
        f"{name} {version} covers CPython {supported_python_versions()} on all checked platforms."
    )
    print(f"cibuildwheel pin {pinned} is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
