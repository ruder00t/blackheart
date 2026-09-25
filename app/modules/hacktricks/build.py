"""Build the offline HackTricks site from the upstream repo tarball.

Reuses tools/build_hacktricks.py (loaded by file path so tools/ needn't be a
package). Network is touched only on Update; the caller soft-fails and keeps any
existing build. Needs python-markdown + pygments installed.
"""
import importlib.util
import shutil
from pathlib import Path

from app.core import offlinedocs as od

TARBALL = "https://codeload.github.com/HackTricks-wiki/hacktricks/tar.gz/refs/heads/master"


def _load_builder():
    root = Path(__file__).resolve().parents[3]           # project root
    path = root / "tools" / "build_hacktricks.py"
    spec = importlib.util.spec_from_file_location("bh_build_hacktricks", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(out_dir):
    """Download + render into out_dir. Returns page count."""
    builder = _load_builder()                            # raises if markdown missing
    tmp, repo = od.fetch_repo(TARBALL)                   # repo/ contains src/SUMMARY.md
    try:
        pages = builder.build(repo, str(out_dir))
        return pages or 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
