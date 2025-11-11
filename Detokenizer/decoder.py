import subprocess
with open("input.txt", "r") as infile, open("output.txt", "w") as outfile:
    subprocess.run(["bash", "postprocess.sh"], stdin=infile, stdout=outfile)
