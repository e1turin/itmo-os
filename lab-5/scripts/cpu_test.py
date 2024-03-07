#!/usr/bin/python3

MAX_CPU = 4 #cores
TIME = 15 #secs
VARIANT_METHODS = ["explog", "int128"]
COMMAND_TEMPLATE = "stress-ng --cpu {} --cpu-method {} -t {} --metrics {}"
EXTRA_OPTS = [
    # "--verbose", # log concrete steps stress-ng does
    # "--tz",  # termal zone, not work in VM
]

def test():
    for m in VARIANT_METHODS:
        for i in range(0, MAX_CPU + 1):
            command = COMMAND_TEMPLATE.format(i, m, TIME, " ".join(EXTRA_OPTS))
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
