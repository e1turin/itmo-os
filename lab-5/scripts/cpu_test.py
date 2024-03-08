#!/usr/bin/python3

MAX_CPU = 4 #cores
TIME = 15 #secs
VARIANT_METHODS = ["explog", "int128"]
STRESSNG_CMD_TMPLT = "stress-ng --cpu {ncpu} --cpu-method {cpum} -t {time} --metrics {ext}"
PERF_CMD_TMPLT = "perf stat -B -ecycles:u,instructions:u -a {cmd}"
PIDSTAT_CMD_TMPL = "pidstat -ul -p {pid} >> {file}"
WARCH_CMD_TMPL = "watch -n {interval} {cmd}"
EXT_OPTS = [
    # "--verbose", # log concrete steps stress-ng does
    # "--tz",  # termal zone, not work in VM
]

def test():
    for m in VARIANT_METHODS:
        for i in range(0, MAX_CPU + 1):
            command = STRESSNG_CMD_TMPLT.format(ncpu=i, cpum=m, time=TIME, ext=" ".join(EXT_OPTS))
            # command = PERF_CMD_TMPLT.format(cmd=command)

            print(command)
            result = os.popen(command).read()
            print(result)

if __name__ == "__main__":
    import os

    try:
        test()
    except KeyboardInterrupt:
        print("< stopped >")
        print()
    except Exception as ex:
        print(ex)
