import argparse
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile_dir', type=str, default='downloaded/')
    parser.add_argument('--infile_prefix', type=str, default='id_to_metadata')
    args = parser.parse_args()

    filename_pattern = re.compile(f'{args.infile_prefix}_(\d+).json')
    json_files = []
    for file in Path(args.infile_dir).iterdir():
        match = filename_pattern.match(file.name)
        if match:
            json_files.append((str(file), int(match.group(1))))

    json_files.sort(key=lambda x: x[1])

    result = dict()
    for json_file in json_files:
        with open(json_file[0], 'r') as f:
            file_dict = json.load(f)
            for k, v in file_dict.items():
                result[k] = v

    with open(f'{args.infile_prefix}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()
