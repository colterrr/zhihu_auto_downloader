import subprocess

port = 8080

p = subprocess.Popen(
    ["mitmdump", "-s", "local.py", "--listen-port", str(port), "--ssl-insecure"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

print(f"Listening on port {port}...")

prefix = "[user downloading]"

for line in p.stdout:
    if line.startswith(prefix):
        print(line[len(prefix):].strip())