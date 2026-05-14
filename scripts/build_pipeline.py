import os
import shutil
import subprocess

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("--- STARTING PRODUCTION DATA PIPELINE (INDIA) ---")

# 1. Generate Bronze Raw Data
run_cmd("python scripts/generate_india_ev_data.py")

# 2. Run Spark ETL Engine (Bronze -> Silver -> Gold)
run_cmd("python services/spark_engine.py")

# 3. Finalize Gold Layer
os.makedirs("data/gold_india", exist_ok=True)
for f in os.listdir("data/gold"):
    src = os.path.join("data/gold", f)
    dst = os.path.join("data/gold_india", f)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        shutil.copy(src, dst)

print("--- PIPELINE COMPLETED ---")
