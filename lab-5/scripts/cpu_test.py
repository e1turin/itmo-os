#!/usr/bin/python3

MAX_CPU = 4 #cores
TIME = 15 #secs
VARIANT_METHODS = ["explog", "int128"]
MASTER_CMD_TMPLT = "perf stat -B -ecycles:u,instructions:u -a {}"
CMD_TMPLT = "stress-ng --cpu {} --cpu-method {} -t {} --metrics {}"
EXTRA_OPTS = [
    # "--verbose", # log concrete steps stress-ng does
    # "--tz",  # termal zone, not work in VM
]

def test():
    for m in VARIANT_METHODS:
        for i in range(0, MAX_CPU + 1):
            command = CMD_TMPLT.format(i, m, TIME, " ".join(EXTRA_OPTS))
            command = MASTER_CMD_TMPLT.format(command)
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
