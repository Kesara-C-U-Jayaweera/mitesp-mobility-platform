import sys
import pandas as pd
import numpy as np
import re
import os
import json
import glob
import joblib
import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Columns the model needs (normalised names)
COL_PASSENGER = "PASSENGER NAME"
COL_TIME = "PICKUP TIME"
COL_LOCATION = "DROP LOCATION"

# Known column-name mappings for different file layouts
COLUMN_MAPS = [
    # Layout A: Excel files from PickMe cost reports
    {
        'Passenger Full Name': COL_PASSENGER,
        'Time': COL_TIME,
        'Drop Location': COL_LOCATION,
        'Pickup Location': 'PICKUP LOCATION',
        'Trip Distance': 'TRIP DISTANCE',
        'Total Fare': 'TOTAL FARE',
        'Vehicle Type': 'VEHICLE TYPE',
        'Phone': 'PHONE',
        'LOB': 'DEPARTMENT',
        'Ride Remark': 'RIDE REMARK',
        'Trip ID': 'TRIP ID',
        'Day of the Week': 'DAY_OF_WEEK',
    },
    # Layout B: Alternate Excel naming
    {
        'Passenger Name': COL_PASSENGER,
        'Pickup Time': COL_TIME,
        'Drop-off Location': COL_LOCATION,
        'Drop Off Location': COL_LOCATION,
    },
]


def _normalise_columns(df):
    """Try each known column map; apply the first one that matches >= 2 columns."""
    current_cols = set(df.columns)
    for cmap in COLUMN_MAPS:
        overlap = current_cols & set(cmap.keys())
        if len(overlap) >= 2:
            df = df.rename(columns=cmap)
            return df
    # No mapping needed - columns already normalised (e.g. history.csv)
    return df


def extract_hour(val):
    """Extract hour (0-23) from various pickup timestamp formats."""
    if pd.isna(val):
        return None
    val_str = str(val).strip()

    # 12-hour format with AM/PM (e.g. '8:24:47 am', '10:40:09 pm')
    m = re.search(r'(\d{1,2}):\d{2}(?::\d{2})?\s*(am|pm)', val_str, re.IGNORECASE)
    if m:
        h = int(m.group(1))
        ampm = m.group(2).lower()
        if ampm == 'pm' and h != 12:
            h += 12
        elif ampm == 'am' and h == 12:
            h = 0
        return h

    # 24-hour format (e.g. '14:24:47')
    m2 = re.search(r'\b([01]?\d|2[0-3]):\d{2}(?::\d{2})?\b', val_str)
    if m2:
        return int(m2.group(1))

    return None


def _next_model_version():
    """Determine next version number from existing models/ directory."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    existing = glob.glob(os.path.join(MODELS_DIR, "model_v*.pkl"))
    if not existing:
        return 1
    versions = []
    for p in existing:
        m = re.search(r'model_v(\d+)\.pkl$', p)
        if m:
            versions.append(int(m.group(1)))
    return max(versions) + 1 if versions else 1


def discover_data_files():
    """Find all .xlsx and .csv files in the data/ directory."""
    os.makedirs(DATA_DIR, exist_ok=True)
    xlsx_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.xlsx")))
    csv_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    return xlsx_files, csv_files


def load_all_data():
    """Load and combine all data files from data/ with smart column mapping."""
    xlsx_files, csv_files = discover_data_files()
    all_files = xlsx_files + csv_files

    if not all_files:
        raise FileNotFoundError(
            f"No data files found in '{DATA_DIR}'. "
            f"Drop .xlsx or .csv files into the data/ folder."
        )

    dfs = []
    source_log = []

    for fpath in xlsx_files:
        fname = os.path.basename(fpath)
        print(f"    Reading Excel: {fname}")
        try:
            # Try common sheet names
            sheet_names_to_try = ['Individual Trips Summary', 'Sheet1', 0]
            df_file = None
            for sheet in sheet_names_to_try:
                try:
                    df_file = pd.read_excel(fpath, sheet_name=sheet)
                    if len(df_file) > 0:
                        break
                except Exception:
                    continue
            if df_file is not None and len(df_file) > 0:
                df_file = _normalise_columns(df_file)
                dfs.append(df_file)
                source_log.append({"file": fname, "rows": len(df_file), "type": "xlsx"})
                print(f"       {len(df_file)} rows loaded")
            else:
                print(f"       Empty or unreadable, skipping")
        except Exception as e:
            print(f"       Error: {e}")

    for fpath in csv_files:
        fname = os.path.basename(fpath)
        print(f"    Reading CSV: {fname}")
        try:
            df_file = pd.read_csv(fpath, encoding='utf-8')
            df_file = _normalise_columns(df_file)
            dfs.append(df_file)
            source_log.append({"file": fname, "rows": len(df_file), "type": "csv"})
            print(f"       {len(df_file)} rows loaded")
        except Exception as e:
            print(f"       Error: {e}")

    if not dfs:
        raise FileNotFoundError("All data files failed to load. Check file formats.")

    combined = pd.concat(dfs, ignore_index=True)
    if 'TRIP ID' in combined.columns:
        combined['TRIP ID'] = combined['TRIP ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
        valid_t = combined[~combined['TRIP ID'].isin(['', 'nan', 'none', 'null'])].drop_duplicates(subset=['TRIP ID'], keep='first')
        missing_t = combined[combined['TRIP ID'].isin(['', 'nan', 'none', 'null'])]
        combined = pd.concat([valid_t, missing_t], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=[COL_PASSENGER, COL_TIME, COL_LOCATION], keep='first'
    )
    return combined, source_log


def main():
    start_time = datetime.datetime.now()

    print("=" * 60)
    print("Transport Optimization - ML Training Pipeline")
    print("=" * 60)

    # Step 1: Discover & Load Data
    print(f"\n[1] Scanning data/ folder for training data...")
    df, source_log = load_all_data()
    total_source_rows = sum(s["rows"] for s in source_log)
    print(f"\n    Combined: {len(df)} unique rows from {len(source_log)} file(s) "
          f"({total_source_rows} raw rows before dedup)")

    # Step 2: Validate required columns
    for col in [COL_PASSENGER, COL_TIME, COL_LOCATION]:
        if col not in df.columns:
            raise KeyError(
                f"Required column '{col}' not found after normalisation. "
                f"Available: {df.columns.tolist()}"
            )

    # Step 3: Clean
    df_clean = df[[COL_PASSENGER, COL_TIME, COL_LOCATION]].dropna().copy()
    df_clean[COL_PASSENGER] = df_clean[COL_PASSENGER].astype(str).str.strip()
    df_clean[COL_LOCATION] = df_clean[COL_LOCATION].astype(str).str.strip()
    df_clean = df_clean[
        (df_clean[COL_PASSENGER] != "") & (df_clean[COL_LOCATION] != "")
    ].copy()

    print(f"\n[2] Extracting 'Hour' feature from timestamps...")
    df_clean["Hour"] = df_clean[COL_TIME].apply(extract_hour)
    df_clean = df_clean.dropna(subset=["Hour"]).copy()
    df_clean["Hour"] = df_clean["Hour"].astype(int)

    n_passengers = df_clean[COL_PASSENGER].nunique()
    n_locations = df_clean[COL_LOCATION].nunique()
    print(f"    Clean records: {len(df_clean)}")
    print(f"    Unique passengers: {n_passengers}")
    print(f"    Unique drop-off locations: {n_locations}")

    # Step 4: Encode
    print(f"\n[3] Encoding categorical variables...")
    le_passenger = LabelEncoder()
    le_location = LabelEncoder()

    df_clean["passenger_encoded"] = le_passenger.fit_transform(df_clean[COL_PASSENGER])
    df_clean["location_encoded"] = le_location.fit_transform(df_clean[COL_LOCATION])

    X = df_clean[["passenger_encoded", "Hour"]]
    y = df_clean["location_encoded"]

    # Step 5: Train with validation split
    print(f"\n[4] Training RandomForestClassifier with 80/20 validation split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )

    clf = RandomForestClassifier(
        n_estimators=150, max_depth=10, min_samples_split=2, random_state=42
    )
    clf.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, clf.predict(X_train))
    test_acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"    Training accuracy:   {train_acc * 100:.2f}%")
    print(f"    Validation accuracy: {test_acc * 100:.2f}%")

    # Step 6: Build lookup
    name_lookup = {name.lower(): name for name in le_passenger.classes_}

    # Step 7: Save versioned model
    version = _next_model_version()
    print(f"\n[5] Saving model v{version}...")

    os.makedirs(MODELS_DIR, exist_ok=True)

    model_path = os.path.join(MODELS_DIR, f"model_v{version}.pkl")
    encoders_path = os.path.join(MODELS_DIR, f"encoders_v{version}.pkl")

    joblib.dump(clf, model_path, compress=3)
    joblib.dump({
        "passenger_encoder": le_passenger,
        "location_encoder": le_location,
        "name_lookup": name_lookup
    }, encoders_path, compress=3)

    # Also save to root for backward compatibility
    joblib.dump(clf, os.path.join(BASE_DIR, "model.pkl"), compress=3)
    joblib.dump({
        "passenger_encoder": le_passenger,
        "location_encoder": le_location,
        "name_lookup": name_lookup
    }, os.path.join(BASE_DIR, "encoders.pkl"), compress=3)

    print(f"    Saved: {model_path}")
    print(f"    Saved: {encoders_path}")

    # Step 8: Save metadata
    elapsed = (datetime.datetime.now() - start_time).total_seconds()

    meta = {
        "version": version,
        "trained_at": datetime.datetime.now().isoformat(),
        "training_duration_sec": round(elapsed, 2),
        "data_sources": source_log,
        "total_raw_rows": total_source_rows,
        "unique_training_rows": len(df_clean),
        "unique_passengers": n_passengers,
        "unique_locations": n_locations,
        "train_accuracy": round(train_acc * 100, 2),
        "validation_accuracy": round(test_acc * 100, 2),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "model_file": f"model_v{version}.pkl",
        "encoders_file": f"encoders_v{version}.pkl",
    }

    meta_path = os.path.join(MODELS_DIR, f"meta_v{version}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Also save as latest metadata for quick access
    latest_meta_path = os.path.join(BASE_DIR, "model_meta.json")
    with open(latest_meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"    Saved metadata: {meta_path}")

    # Step 9: Validation samples
    print(f"\n[6] Validation Test on Sample Passengers:")
    sample_passengers = df_clean[COL_PASSENGER].unique()[:5]
    for p_name in sample_passengers:
        p_code = le_passenger.transform([p_name])[0]
        for h in [8, 21]:
            feat = pd.DataFrame([[p_code, h]], columns=["passenger_encoded", "Hour"])
            pred_code = clf.predict(feat)[0]
            pred_loc = le_location.inverse_transform([pred_code])[0]
            disp_loc = (pred_loc[:45] + '...') if len(pred_loc) > 45 else pred_loc
            safe_name = str(p_name).replace('\ufeff', '').strip()
            safe_loc = str(disp_loc).replace('\ufeff', '').strip()
            print(f"    {safe_name:<12} | {h:02d}:00 | -> {safe_loc}")

    print(f"\n{'=' * 60}")
    print(f"SUCCESS: Model v{version} trained and saved!")
    print(f"   Accuracy: {test_acc * 100:.1f}% | Passengers: {n_passengers} | Locations: {n_locations}")
    print(f"   Duration: {elapsed:.1f}s | Data sources: {len(source_log)} file(s)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
