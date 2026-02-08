# CCSDSPy AI Coding Instructions

## Project Overview
CCSDSPy is a Python library for reading tightly packed bits in CCSDS (Consultative Committee for Space Data Systems) format, used by NASA and ESA missions. It provides an object-oriented API for decoding fixed-length and variable-length packets from binary files.

## Core Architecture
- **Packet Types**: `FixedLength` for uniform packets, `VariableLength` for dynamic packets
- **Field Definitions**: `PacketField` for scalar fields, `PacketArray` for multidimensional arrays
- **Data Types**: `uint`, `int`, `float`, `str`, `fill` (padding)
- **Decoding**: Bit-level parsing with configurable byte order (big/little endian or custom)
- **Post-processing**: `Converter` subclasses for calibration, enums, datetime parsing

## Key Patterns
### Packet Definition
```python
from ccsdspy import FixedLength, PacketField, PacketArray

pkt = FixedLength([
    PacketField(name='SHCOARSE', data_type='uint', bit_length=32),
    PacketField(name='VOLTAGE', data_type='int', bit_length=8),
    PacketArray(name='SENSOR_GRID', data_type='uint', bit_length=16, 
                array_shape=(32, 32), array_order='C'),
])
```

### Loading Data
```python
result = pkt.load('data.bin')  # Returns dict of numpy arrays
```

### CSV-Based Definitions
Packets can be defined via CSV files with columns: `name,data_type,bit_length[,bit_offset]`

## Development Workflow
- **Install**: `pip install -e '.[dev]'` for development dependencies
- **Test**: `pytest --pyargs ccsdspy --cov ccsdspy`
- **Lint**: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
- **Format**: `black --check --diff ccsdspy`
- **Docs**: `sphinx-build docs docs/_build/html -W -b html`

## Conventions
- **Imports**: Use relative imports within package (`from .. import ...`)
- **Naming**: Descriptive field names matching telemetry mnemonics
- **Bit Offsets**: Automatic calculation unless specified; includes 48-bit primary header
- **Byte Order**: "big" (default), "little", or custom string like "4321"
- **Array Order**: 'C' (row-major) or 'F' (column-major) for PacketArray
- **Error Handling**: Raise `ValueError`/`TypeError` for invalid inputs, log warnings for data issues

## Testing
- Use `pytest` with descriptive test function names
- Test exception raising with `pytest.raises()`
- Mock binary data using `io.BytesIO` and `struct.pack()`
- Reference test data in `ccsdspy/tests/data/`

## Dependencies
- **Core**: `numpy`, `pyyaml`, `appdirs`
- **Dev**: `pytest`, `black`, `flake8`, `coverage`, `sphinx`

## File Structure
- `ccsdspy/packet_types.py`: Main packet classes
- `ccsdspy/packet_fields.py`: Field definitions
- `ccsdspy/decode.py`: Internal decoding logic
- `ccsdspy/converters.py`: Post-processing converters
- `ccsdspy/utils.py`: Packet utilities
- `ccsdspy/tests/`: Comprehensive test suite with data fixtures</content>
<parameter name="filePath">/Users/schriste/Developer/repos/ccsdspy/.github/copilot-instructions.md