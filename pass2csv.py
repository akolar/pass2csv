#!/usr/bin/env python

import argparse
import collections
import csv
import gnupg
import logging
import os

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(description='Export pass database to '
                                     'a CSV file')
    parser.add_argument('output', help='path to the output file')
    parser.add_argument('-p', '--password-store', default='~/.password-store',
                        help='path to pass directory [default: %(default)s]',
                        metavar='path')
    parser.add_argument('-k', '--keywords', default=['username', 'url'],
                        help='list of keywords on begining of each line in a '
                             '.gpg file [default: %(default)s]',
                        metavar='keywords', nargs='*')
    parser.add_argument('-g', '--gpg-keyring', default='~/.gnupg',
                        help='path to GnuPG keyring [default: %(default)s]',
                        metavar='path')
    return parser.parse_args()


def get_file_list(pass_path):
    logger.info('Searching for .gpg files in %s', pass_path)
    filelist = []

    for root, dirs, files in os.walk(pass_path):
        filelist += [os.path.join(root.replace(pass_path, '')[1:], f)
                     for f in files if f.endswith('.gpg')]

    logger.info('Found %d matching files', len(filelist))
    return filelist


def extract_title(name):
    try:
        folder, title = name.rsplit('/', maxsplit=1)
    except ValueError:
        folder = ''
        title = name

    title = title.rstrip('.gpg')
    return folder, title


def convert_file(gpg, pass_path, name, keywords):
    logger.debug('Converting %s...', name)

    with open(os.path.join(pass_path, name), 'rb') as f:
        decrypted = str(gpg.decrypt_file(f))

    lines = decrypted.split('\n')
    folder, title = extract_title(name)

    data = {
        'folder': folder,
        'title': title,
        'password': lines[0],
        'comments': ''
    }

    for line in lines[1:]:
        split = line.split(':', maxsplit=1)
        kw = split[0]

        if kw.lower() in keywords:
            data[kw] = split[1].strip()
        elif (kw.lower() == 'password') or (kw.startswith('--')):
            pass
        elif line != '':
            data['comments'] += line + '\\n'

    return data


def setup_gpg(path):
    logger.debug('Setting up GPG in keyring %s', path)

    gpg = gnupg.GPG(gnupghome=path)
    return gpg


def write_csv(path, keywords, data):
    logger.info('Writing data to %s...', path)

    header = ['folder', 'title'] + keywords + ['password', 'comments']
    logging.debug('Header column is %s', header)

    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for website in data:
            values = [website.get(k, '') for k in header]
            writer.writerow(values)


def main():
    args = parse_args()
    logger.debug('Arguments: %s', args)

    password_store = os.path.expanduser(args.password_store)
    gpg = setup_gpg(os.path.expanduser(args.gpg_keyring))
    targets = get_file_list(password_store)

    logger.info('Converting files...')
    converted_data = []
    for target in targets:
        converted_data.append(convert_file(gpg, password_store,
                                           target, args.keywords))
    logger.info('Conversion finished')

    write_csv(os.path.expanduser(args.output), args.keywords, converted_data)


if __name__ == '__main__':
    main()
