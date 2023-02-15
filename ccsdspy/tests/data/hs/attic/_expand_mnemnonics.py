"""This was a data cleaning script."""
import pandas as pd
from collections import OrderedDict

if __name__ == "__main__":
    df = pd.read_csv("SSAT_Mnemonics.csv")
    apids = set(df["packet_display_name"])

    for apid in apids:
        mask = df["packet_display_name"] == apid
        df_s = df[mask]

        defs = OrderedDict(
            [
                ("name", []),
                ("data_type", []),
                ("bit_offset", []),
                ("bit_length", []),
                ("calibration", []),
            ]
        )

        for i, row in df_s.iterrows():
            # Skip primary header
            if row["mnemonic"].split("_", 1)[-1].upper() in (
                "PKTVNO",
                "PCKT",
                "SHDF",
                "APID",
                "SEGF",
                "CNT",
                "PLEN",
            ):
                continue

            name = row["mnemonic"].lower()
            data_type = row["#datatype"].lower()
            bit_offset = (row["byte_offset"] - 6) * 8 + row["bit_offset"]
            bit_length = row["bit_length"]
            calibration = row["mnemonic_calibration_values"]

            if data_type == "char":
                data_type = "str"

            dim = row["dimension"]

            if dim == 1:
                defs["name"].append(name)
                defs["data_type"].append(data_type)
                defs["bit_offset"].append(bit_offset)
                defs["bit_length"].append(bit_length)
                defs["calibration"].append(calibration)
            else:
                if data_type != "float":
                    bit_length = int(bit_length / dim)

                for j in range(dim):
                    defs["name"].append(f"{name}[{j}]")
                    defs["data_type"].append(data_type)
                    defs["bit_offset"].append(bit_offset)
                    defs["bit_length"].append(bit_length)
                    defs["calibration"].append(calibration)

        out_filename = f"apid{apid:03d}/defs.csv"
        pd.DataFrame(defs).to_csv(out_filename, index=0)
        print
