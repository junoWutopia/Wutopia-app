import argparse
import json
from pathlib import Path
import re
from typing import Union


def metadata_key_to_id(
        id_to_metadata: dict[str, dict[str, str]],
        metadata_key: str,
        allow_multiple: bool = False) -> dict[str, Union[int, list[int]]]:
    ret = dict()
    for resource_id, metadata in id_to_metadata.items():
        if metadata_key in metadata:
            metadata_value = metadata[metadata_key]

            if allow_multiple:
                if metadata_value not in ret.keys():
                    ret[metadata_value] = [int(resource_id)]
                else:
                    ret[metadata_value].append(int(resource_id))
            else:
                assert (metadata_value not in ret.keys())
                ret[metadata_value] = int(resource_id)
    return ret


def main():
    with open('id_to_metadata.json', 'r', encoding='utf-8') as f:
        id_to_metadata = json.load(f)

    with open('title_to_id2.json', 'w', encoding='utf-8') as f:
        json.dump(metadata_key_to_id(id_to_metadata, 'title', True),
                  f,
                  indent=2)

    with open('product_id_to_id2.json', 'w', encoding='utf-8') as f:
        json.dump(metadata_key_to_id(id_to_metadata, 'PRODUCT_ID', False),
                  f,
                  indent=2)


if __name__ == '__main__':
    main()
