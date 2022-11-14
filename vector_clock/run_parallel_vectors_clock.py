import subprocess

subprocess.run("python3 vector_process.py -pid 1 --port 6001 & python3 vector_process.py -pid 2 --port 6002", shell=True)