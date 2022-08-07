"""Main method of the module. 

This is called with `python -m ccsdspy`
"""

__author__ = "Daniel da Silva <mail@danieldasilva.org>"

import argparse

from .utils import split_by_apid


def module_main():
    """Main method of the module, run with `python -m ccsdspy [..]"""
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    
    subparser = parser.add_subparsers(dest='command')
    split_parser = subparser.add_parser(
        'split',
        help=('Subcommand to run. Currently only split is supported. Use '
              'split to split mixed APID stream and write files to the '
              'current directory.')
    )
    split_parser.add_argument('file')
    split_parser.add_argument(
        '--valid-apids', help='Valid APIDs seperated by comma'
    )

    args = parser.parse_args()

    # Implemention of split command, which splits a mixed stream and writes
    # to the current directory.
    if args.command == 'split':
        if args.valid_apids:
            toks = args.valid_apids.split(',')
            valid_apids = [int(apid) for apid in toks]
        else:
            valid_apids = None
            
        stream_by_apid = split_by_apid(args.file, valid_apids=valid_apids)

        print('Parsing done!')
        
        for apid in sorted(stream_by_apid):
            if valid_apids and apid not in valid_apids:
                continue

            out_file_name = f'./apid{apid:05d}.tlm'
            print(f'Writing {out_file_name}')

            with open(out_file_name, 'wb') as file_out:
                file_out.write(stream_by_apid[apid].read())


if __name__ == '__main__':
    module_main()
