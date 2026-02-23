import pandas as pd

DB_PATH = "db/FLAT_CMPL.txt"
PARQUET_PATH = "db/complaints.parquet"

column_names = [
    "CMPLID", "ODINO", "MFR_NAME", "MAKETXT", "MODELTXT", "YEARTXT",
    "CRASH", "FAILDATE", "FIRE", "INJURED", "DEATHS", "COMPDESC",
    "CITY", "STATE", "VIN", "DATEA", "LDATE", "MILES", "OCCURENCES",
    "CDESCR", "CMPL_TYPE", "POLICE_RPT_YN", "PURCH_DT",
    "ORIG_OWNER_YN", "ANTI_BRAKES_YN", "CRUISE_CONT_YN", "NUM_CYLS",
    "DRIVE_TRAIN", "FUEL_SYS", "FUEL_TYPE", "TRANS_TYPE",
    "VEH_SPEED", "DOT", "TIRE_SIZE", "LOC_OF_TIRE",
    "TIRE_FAIL_TYPE", "ORIG_EQUIP_YN", "MANUF_DT", "SEAT_TYPE",
    "RESTRAINT_TYPE", "DEALER_NAME", "DEALER_TEL",
    "DEALER_CITY", "DEALER_STATE", "DEALER_ZIP",
    "PROD_TYPE", "REPAIRED_YN", "MEDICAL_ATTN",
    "VEHICLES_TOWED_YN"
]

print("Loading TXT file...")
df = pd.read_csv(
    DB_PATH,
    sep="\t",
    header=None,
    names=column_names,
    dtype=str,
    engine="c",
    on_bad_lines="skip"
)

print("Keeping only required columns...")
df = df[
    [
        "ODINO",
        "MAKETXT",
        "MODELTXT",
        "YEARTXT",
        "COMPDESC",
        "CDESCR",
        "STATE",
        "CRASH",
        "FIRE",
        "INJURED",
        "DEATHS",
        "FAILDATE"
    ]
]

print("Normalizing text...")
df["MAKETXT"] = df["MAKETXT"].str.upper()
df["MODELTXT"] = df["MODELTXT"].str.upper()
df["YEARTXT"] = df["YEARTXT"].astype(str)

print("Saving as Parquet...")
df.to_parquet(PARQUET_PATH, engine="pyarrow", compression="snappy")

print("Done.")