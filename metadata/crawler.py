import argparse
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

DOMAIN = 'https://www.missionjuno.swri.edu'


def get_path(p) -> Path:
    path = Path(p)
    if not path.exists():
        path.mkdir()
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', type=int, default=0)
    parser.add_argument('--outfile_dir', type=str, default='downloaded/')
    parser.add_argument('--outfile_prefix', type=str, default='id_to_metadata')
    parser.add_argument('--min', type=int, default=1)
    parser.add_argument('--max', type=int, default=13990)
    args = parser.parse_args()

    s = requests.Session()

    id_to_metadata = dict()
    for resource_id in range(args.min, args.max + 1):
        r_page = s.get(DOMAIN + f'/junocam/processing?id={resource_id}')
        r_page_soup = BeautifulSoup(r_page.text, 'html.parser')

        metadata = r_page_soup.find('dl', {'id': 'metadataDropdown'})
        pt2 = re.compile('\w+')
        title_h1 = r_page_soup.find('div', {'id': 'junocam_content'})
        if title_h1 is not None:
            title_h1 = title_h1.find('figure')
        if title_h1 is not None:
            title_h1 = title_h1.find('h1')

        metadata_dict = dict()
        if title_h1 is not None:
            metadata_dict['title'] = title_h1.text
        if metadata is not None:
            for div in metadata.contents:
                dt = div.find_next('dt')
                dd = div.find_next('dd')
                tmp = pt2.findall(dt.text)
                metadata_dict['_'.join(tmp)] = dd.text

        id_to_metadata[resource_id] = metadata_dict

        print(resource_id, metadata_dict)

        outfile_dir = get_path(args.outfile_dir)
        with open(outfile_dir / f'{args.outfile_prefix}_{args.worker}.json',
                  'w',
                  encoding='utf-8') as f:
            json.dump(id_to_metadata, f, indent=2)


if __name__ == '__main__':
    main()
