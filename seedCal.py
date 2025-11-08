import hashlib
import subprocess
from datetime import datetime

remote = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode().strip()

first_commit_epoch = subprocess.check_output(['git', 'log', '--reverse', '--format=%ct']).decode().split('\n')[0].strip()

# Şu anki zamanı YYYYMMDDHHmm formatında
start_time = datetime.now().strftime("%Y%m%d%H%M")

# Seed hesapla
raw_string = f"{remote}|{first_commit_epoch}|{start_time}"
seed = hashlib.sha256(raw_string.encode()).hexdigest()[:12]

# Katsayılar
A = 7  + (int(seed[0:2], 16) % 5)
B = 13 + (int(seed[2:4], 16) % 7)
C = 3  + (int(seed[4:6], 16) % 3)

print(f"Seed: {seed}")
print(f"A={A}, B={B}, C={C}")
print(f"Raw: {raw_string}")
