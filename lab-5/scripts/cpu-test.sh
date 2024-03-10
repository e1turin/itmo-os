VARIANT_METHODS = 
STRESSNG_CMD_TMPLT = "stress-ng --cpu {ncpu} --cpu-method {cpum} -t {time} --metrics {ext}"
PERF_CMD_TMPLT = "perf stat -B -ecycles:u,instructions:u -a {cmd}"
PIDSTAT_CMD_TMPL = "pidstat -ul -p {pid} >> {file}"
WARCH_CMD_TMPL = "watch -n {interval} {cmd}"

