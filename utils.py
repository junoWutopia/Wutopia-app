from pathlib import Path
import requests
from tqdm import tqdm


def get_path(p) -> Path:
    path = Path(p)
    if not path.exists():
        path.mkdir()
    return path


def download(save_file: Path, response: requests.Response) -> None:
    with tqdm.wrapattr(
            open(save_file, 'wb'),
            'write',
            desc=save_file.name,
            total=int(response.headers['content-length']),
            miniters=1,
    ) as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
