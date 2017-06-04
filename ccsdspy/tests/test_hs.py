"""Run end-to-end test of decoding fixed-length packets
using the test data in the data/hs directory.
"""
import csv
import glob
import json
import os
from collections import OrderedDict
import numpy as np
from astropy.table import Table
from .. import FixedLength, PacketField


def _run_apid_test(apid):
    """Driver for running an APID test. Each apidXXX directory under
    `data/hs` contains:

            defs.csv     -- packet definition with conversions.
            xxxx.tlm     -- binary CCSDS file
            xxxx.cvt.csv -- CSV holding contents of what CCSDS file should
                            decode to after conversions.
    """
    
    # Setup paths for the definitions, truth, and CCSDS files
    # in the APID directory.
    apid_dir = os.path.join('ccsdspy', 'tests', 'data', 'hs',
                            'apid{:03d}'.format(apid))
    
    defs_file_path = os.path.join(apid_dir, 'defs.csv')    
    truth_file_path = glob.glob(os.path.join(apid_dir, '*.cvt.csv')).pop()
    ccsds_file_path = glob.glob(os.path.join(apid_dir, '*.tlm')).pop()

    assert all(os.path.exists(path) for path in (
        apid_dir,
        defs_file_path,
        truth_file_path,
        ccsds_file_path,
    ))

    
    # Load the definitions, the truth data (in CSV format), and the
    # decoded file.
    defs = _load_apid_defs(defs_file_path)
    truth = _load_apid_truth(truth_file_path, defs)
    decoded = _decode_ccsds_file(ccsds_file_path, defs)

    # That's it for now. We just test that it runs without
    # exception.
    
    
def _load_apid_truth(truth_file_path, defs):
    """Load APID truth CSV and return a Table"""
    # We load the CSV using the Python CSV module due to a segfault bug in
    # astropy.asii.read(): See gh #3611.
    with open(truth_file_path) as fh:
        lines = fh.readlines()

    colnames = lines[0][:-1].split(',')
    table_dict = OrderedDict([(colname, []) for colname in colnames])

    # Loop through CSV lines, read all as string
    with open(truth_file_path) as fh:
        reader = csv.reader(fh)
        first_line = True

        for row in reader:
            if first_line:                
                first_line = False
                continue

            for key, row_value in zip(table_dict.keys(), row):
                table_dict[key].append(row_value)

    # Drop columns we don't need. We only need the columns we decode,
    # taken from the defs.
    keep_cols = set(defs['name'])

    for colname in colnames:
        if colname not in keep_cols:
            del table_dict[colname]
    
    # Set the correct types using types from defs.
    for row in defs:
        key = row['name']
        data_type = row['data_type']
        cal = row['calibration']

        if cal:
            dtype = np.array(cal.values()).dtype
            table_dict[key] = np.array(table_dict[key], dtype=dtype)
        elif data_type == 'uint':
            table_dict[key] = np.array(table_dict[key], dtype=np.uint)
        elif data_type == 'int':
            table_dict[key] = np.array(table_dict[key], dtype=np.int)
        elif data_type == 'str':
            table_dict[key] = np.array(table_dict[key], dtype=str)
        elif data_type == 'float':
            table_dict[key] = np.array(table_dict[key], dtype=float)
        else:
            raise RuntimeError('Type {} implemented'.format(data_type))
        
    # Create table and return
    return Table(table_dict)

    
def _load_apid_defs(defs_file_path):
    """Load APID definitions (defs.csv) and return a Table"""
    # We load the CSV using the Python CSV module due to a segfault bug in
    # astropy.asii.read(): See gh #3611.
    table_dict = OrderedDict([
        ('name', []),
        ('data_type', []),
        ('bit_offset', []),
        ('bit_length', []),
        ('calibration', [])
    ])

    # Loop through CSV lines, read all as strings.
    with open(defs_file_path) as fh:
        reader = csv.reader(fh)
        first_line = True

        for row in reader:
            if first_line:                
                first_line = False
                continue

            for key, row_value in zip(table_dict.keys(), row):
                table_dict[key].append(row_value)

    # Change from string to final type.
    table_dict['name'] = [name.upper() for name in table_dict['name']]
    table_dict['bit_offset'] = [int(n) for n in table_dict['bit_offset']]
    table_dict['bit_length'] = [int(n) for n in table_dict['bit_length']]
    
    decode_cal = lambda cal: json.loads(cal) if cal else None
    table_dict['calibration'] = [decode_cal(v) for v
                                 in table_dict['calibration']]

    # Create table and return
    return Table(table_dict)


def _decode_ccsds_file(ccsds_file_path, defs):
    pkt_fields = []

    for row in defs:
        pkt_fields.append(
            PacketField(name=row['name'],
                        data_type=row['data_type'],
                        bit_length=row['bit_length'],)
                        #bit_offset=row['bit_offset'])
        )

    pkt = FixedLength(pkt_fields)
    decoded = pkt.load(ccsds_file_path)
  
    return decoded


def test_hs_apid001():
    _run_apid_test(1)
    
def test_hs_apid010():
    _run_apid_test(10)

def test_hs_apid035():
    _run_apid_test(35)

def test_hs_apid130():
    _run_apid_test(130)

def test_hs_apid251():
    _run_apid_test(251)

def test_hs_apid895():
    _run_apid_test(895)
