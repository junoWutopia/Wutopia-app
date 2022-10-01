import re
from typing import Literal, Union


from pathlib import Path
import requests
from tqdm import tqdm


def get_path(p) -> Path:
    path = Path(p)
    if not path.exists():
        path.mkdir()
    return path


def download(mode: Literal['dir', 'file'],
             save_path: Union[str, Path],
             response: requests.Response) -> None:
    if isinstance(save_path, str):
        save_path = Path(save_path)

    filename_pattern = re.compile('(?<=filename=").*(?=")')

    if mode == 'dir':
        save_dir = get_path(save_path)
        dl_header = response.headers['Content-Disposition']
        filename = filename_pattern.search(dl_header).group(0)
    else:
        save_dir = get_path(save_path.parent)
        filename = save_path.name

    with tqdm.wrapattr(
            open(save_dir / filename, 'wb'),
            'write',
            desc=filename,
            total=int(response.headers['content-length']),
            miniters=1,
    ) as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
