from pathlib import Path
import hashlib

def md5_hash(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.md5(f.read()).hexdigest()