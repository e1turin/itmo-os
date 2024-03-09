# Лабораторная работа №5. Тестирование системы.

## Описание задания

- [TASK.md](./TASK.md)

там же в описании задания могут быть мои комментарии.

## Вариант

```
cpu:     [explog,int128]; 
cache:   [l1cache,cache-ways]; 
io:      [io-uring,ioport];
memory:  [zlib-mem-level,fork-vm]; 
network: [dccp,netlink-proc]; 
pipe:    [pipeherd,sigpipe]; 
sched:   [resched,schedpolicy]
```


### Комментарии

#### Гайды

- [wiki.ubuntu.com/Kernel/Reference/stress-ng](https://wiki.ubuntu.com/Kernel/Reference/stress-ng)
- [RedHat documentation. Chapter 29. Stress testing real-time systems with stress-ng](https://access.redhat.com/documentation/ru-ru/red_hat_enterprise_linux_for_real_time/8/html/optimizing_rhel_8_for_real_time_for_low_latency_operation/assembly_stress-testing-real-time-systems-with-stress-ng_optimizing-rhel8-for-real-time-for-low-latency-operation)
- https://github.com/ColinIanKing/stress-ng
    - https://github.com/ColinIanKing/stress-ng/blob/master/presentations/kernel-recipes-2023/kernel-recipes-2023.pdf
    - https://github.com/ColinIanKing/stress-ng/blob/master/presentations/linux-foundation-webinar-2022-05-19/stress-ng-2021.pdf

#### Оценивание

Показаели в `stress-ng`, aka BOGO ops, мало что значат и поэтому их нельзя
использовать для оценки производительности системы --- об этом заявляется 
в 3 параграйе man для утилиты: 

> stress-ng  can  also measure test throughput rates; this can be useful to
> observe performance changes across different operating system releases or
> types of hardware. However, it has never been  intended to be used as a
> precise benchmark test suite, so do NOT use it in this manner.

Так что, для измерения показателей системы нужно использовать другие утилиты для мониторинга.

`stress-ng` позволяет ограничить время работы нагрузочных тестов с помощью
опции `--timeout` (`-t`). Для тестировани, думаю стоит измерять показатели за
одинаковые промежутуки времени, но само значение этого параметра не так важно.

При этом, каждый параметр $\pm$ одинакого по времени нагружает систему, поэтому
можно на графиках изобразить просто уровни загруженности подсистем при каждом
из тесте с указанными параметрами.

Еще `stress-ng` имеет флажок `--perf` (требует прав суперпользователя), который
выводит статистику по счетчикам ядра.
- но чето статистика меняется от запуска к запуску прям значительно

#### Нагрузка CPU

Для нагрузки CPU выдаются варианты задач которые процессор будет решать (методы).

`-c N, --cpu N`
> start N workers exercising the CPU by sequentially  working  through  all
> the  different  CPU stress  methods.  Instead of exercising all the CPU
> stress methods, one can specify a specific CPU stress method with the
> `--cpu-method` option.

- N=0 создает воркера под каждое ядро процессора
- не знаю, правильно ли таким образом создавать воркеров для методов нагрузки
- Эта опция задает количество процессов, если другие опции создающие воркеров не указаны.

```sh
stress-ng --cpu 0 -t 20
```

`--cpu-method <method>`:
> specify a cpu stress method. By default, all the stress methods  are  exer‐
> cised  sequentially,  however one can specify just one method to be used if
> required.  Available cpu stress methods are described as follows: <...>

`explog`:
> iterate on n = exp(log(n) ÷ 1.00002)

`int128`:
> 1000 iterations of a mix of 128 bit integer operations (GCC only).

Нагрузка:

```sh
# cpu
stress-ng --cpu 0 --cpu-method explog -t 20
stress-ng --cpu 0 --cpu-method int128 -t 20
```


Чтобы построить графики нагрузки CPU, думаю можно измерять температуру ядра
(опция `--tz` в stress-ng) или количество исполненных инструкций и циклов исполнения.
Но оба из этих подходов требуют запуска кода на хостовой системе.

```sh
stress-ng --taskset 0,1,5-7 --matrix 5

# to measure cycles & instructions overl all (-a) system
sudo perf stat -B -ecycles:u,instructions:u -a sleep 5
```

```sh
# single command
## explog
(stress-ng --cpu 1 --cpu-method explog -t 20 &) &&
    (export PID=`ps -a | grep stress-ng | tail -n 1 | 
        python3 -c "print(input().split()[0])"` && 
     timeout 20 watch -n 1 "pidstat -ul -p $PID >> cpu-test-explog.log")

## int128
(stress-ng --cpu 1 --cpu-method int128 -t 20 &) &&
    (export PID=`ps -a | grep stress-ng | tail -n 1 | 
        python3 -c "print(input().split()[0])"` && 
     watch -n 1 "pidstat -ul -p $PID >> cpu-test-int128.log")
```

#### Нагрузка кеша

Для нагрузки кеша процессора:

`--cache-ways`:
>  specify  the  number of cache ways to exercise. This allows a subset of the
>  overall cache size to be exercised.

`--l1cache N`:
>  start  N  workers  that  exercise the CPU level 1 cache with reads and
>  writes. A cache aligned buffer that is twice the level 1 cache size is read
>  and then written  in  level  1  cache  set sized  steps  over each level 1
>  cache set. This is designed to exercise cache block evictions. The bogo-op
>  count measures the number of million cache lines  touched. Where possible,
>  the level  1  cache  geometry is determined from the kernel, however, this
>  is not possible on some architectures or kernels, so one may need to specify
>  these manually. One can specify 3 out  of the 4 cache geometric parameters,
>  these are as follows: <...>

- нужно дополнительно указать воркеров

Нагрузка:

```sh
stress-ng --l1cache 10
stress-ng --l1cache 10 --cache-ways 5
# or
stress-ng --cache 10 --cache-ways 5
```

#### Нагрузка подсистемы ввода-вывода

`--io-uring N`:
> start  N workers that perform iovec write and read I/O operations using the
> Linux io-uring in‐ terface. On each bogo-loop 1024 × 512 byte writes and 
> 1024 × reads are performed on  a  tempo‐ rary file.

`--ioport N`:
> start N workers than perform bursts of 16 reads and 16 writes of ioport 0x80
> (x86  Linux  systems only).  I/O performed on x86 platforms on port 0x80
> will cause delays on the CPU performing the I/O.

- нужно дополнительно определить воркеров (хз почему)
- требует привелегий

Нагрузка:

```sh
stress-ng --io-uring 10
stress-ng --cpu 0 --ioport 10
```

#### Нагрузка подсистемы памяти

`--fork-vm`:
> enable  detrimental performance virtual memory advice using `madvise` on all
> pages of the forked process. Where possible this will try to set every page
> in the new process with using  madvise `MADV_MERGEABLE`, `MADV_WILLNEED`,
> `MADV_HUGEPAGE` and `MADV_RANDOM` flags. Linux only.

- нужно дополнительно определить воркеров

`--zlib-mem-level L`:
> specify the reserved compression state memory for zlib.  Default is 8.
>
> Values:
> - 1 = minimum memory usage
> - 9 = maximum memory usage

- нужно дополнительно определить воркеров

```sh
stress-ng --cpu 0 --fork-vm 
stress-ng --cpu 0 --zlib-mem-level 8
```

#### Нагрузка на сетевую подсистему

`--dccp N`:
> start  N  workers  that  send  and receive data using the Datagram Congestion
> Control Protocol (DCCP) (RFC4340). This involves a pair of client/server
> processes  performing  rapid  connect, send and receives and disconnects on
> the local host.

`--netlink-proc N`:
> start N workers that spawn child processes and monitor fork/exec/exit process
> events  via  the proc netlink connector. Each event received is counted as a
> bogo op. This stressor can only be run on Linux and requires `CAP_NET_ADMIN`
> capability.

- нужно дополнительно определить воркеров (хз почему)

```sh
stress-ng --dccp 10 -t 20
stress-ng --cpu 0 --netlink-proc 10 -t 20
```

#### Нагрузка на pipe (межпроцессное общение)

`--pipeherd N`:
> start N workers that pass a 64 bit token counter to/from 100 child  processes
> over  a  shared pipe. This forces a high context switch rate and can trigger
> a "thundering herd" of wakeups on processes that are blocked on pipe waits.

`--sigpipe N`
> start  N  workers  that repeatedly spawn off child process that exits before
> a parent can com‐ plete a pipe write, causing a SIGPIPE signal.  The  child
> process  is  either  spawned  using clone(2) if it is available or use the
> slower fork(2) instead.

```sh
stress-ng --pipeherd 10 -t 20
stress-ng --sigpipe 10 -t 20
```

#### Нагрузка на планировщик

`--resched N`:
> start N workers that exercise process rescheduling. Each stressor spawns a
> child  process  for each of the positive nice levels and iterates over the
> nice levels from 0 to the lowest priority level (highest nice value). For
> each of the nice levels 1024 iterations  over  3  non-real time  scheduling
> polices `SCHED_OTHER`, `SCHED_BATCH` and `SCHED_IDLE` are set and a
> `sched_yield` occurs to force heavy rescheduling activity.  When the -v
> verbose option is used  the  distribu‐ tion  of  the number of yields across
> the nice levels is printed for the first stressor out of the N stressors.

`--schedpolicy N`:
> start N workers that work set the worker to  various  available  scheduling
> policies  out  of `SCHED_OTHER`,  `SCHED_BATCH`,  `SCHED_IDLE`, `SCHED_FIFO`,
> `SCHED_RR` and `SCHED_DEADLINE`.  For the real time scheduling policies a random
> sched priority is selected between the minimum  and  maximum scheduling
> priority settings.

```sh
stress-ng --resched 10 -t 20
stress-ng --schedpolicy 10 -t 20
```

#### Мониторинг

Для мониторинга можно использовать разные утилиты. Наверное, для измерения
нагрузки конкретной подсистемы стоит использовать специализированную для нее
утилиту.


cpu: 
- `sar 1 20 -u` --- CPU utilization
- `sar 1 20 -q CPU`
- `sar 1 20 -w` --- Task creation and system switching activity
- `sar 1 20 -m` --- Powermanagement statistics
- `pidstat -G stress-ng -u`
- `stress-ng --tz` --- Измерение температуры на ядрах
- `vmstat 1 20` --- time in various code sections
- `mpstat -u` --- CPU utilization

cache:   
- `vmstat 1 20` --- amount of memory used as cache

io:      
- `sar 1 20 -q IO`
- `sar 1 20 -b` --- I/O and transfer reate statistics
- `pidstat -G stress-ng -d`
- `iostat`
- `vmstat 1 20` --- time spent to IO
- `sudo iotop` --- TUI for monitoring

memory:  
- `sar 1 20 -r` --- Memory utilization
- `sar 1 20 -S` --- Swap utilization
- `sar 1 20 -B` --- Paging statistics
- `sar 1 20 -W` --- Swapping statistics
- `sar 1 20 -q MEM`
- `pidstat -G stress-ng -r`
- `free` --- вроде бы можно видеть изменения в количестве страниц в свопе.
- `pmap` --- Report memory map of process (не мой случай, похоже)

network: 
- `sar 1 20 -n ALL`
- `nload -m -t 1000` --- Уровень загруженности сетевых устройств, уровень
  трафика. (обновляется раз в 1000ms, неудобно для логирования)
- `iptraf` --- TUI для просмотра пакетов трафика в реальном времени

pipe:    
- как в IO мб?

sched:   
- `sar 1 20 -I SUM` --- Statistics for interrupts (or ALL)
- `vmstat` --- Number of context switch and interrupts per second

> `sar` (system activity reporter): общесистемное средство, собирающая
> статистику по пейджингу (-В) и свопингу (-W), вводу-выводу (-b,-d),
> смонтированным системам (-F), прерываниям (-1), управлению питанием (-m),
> сети (-n), процессорам (-P,-u), очереди процессов и загрузке (-g,-w), памяти
> (-r), области подкачки (-s), терминалам (-y) 
> 
> Можно настроить сбор исторических результатов (crontab) 
>
> Пример: заг -q 1 1 (одно измерение за одну секунду) 

> - Процессор: `ps`, `top`, `tiptop`, `turbostat`, `rdmsr`, `numastat`,
>   `uptime` 
> - Виртуальная память: `vmstat`, `slabtop`, `pidstat`, `free` 
> - Дисковая подсистема: `iostat`, `iotop`, `blktrace` 
> - Сеть: `netstat`, `tcpdump`, `iptraf`, `ethtool`, `nicstat`, `iр` 
> - Интерактивные (типа top) или с указанием количества запуска и интервала
>   (типа `sar`) 
> - Некоторые работают только с правами root! 


GPT:
> Для мониторинга различных подсистем в Linux существует множество утилит,
> которые позволяют отслеживать состояние системы. Вот некоторые из наиболее
> распространенных утилит для мониторинга различных подсистем:
> 
> 1. **CPU**:
>    - `top` - Отображает текущую активность процессов и загрузку CPU.
>    - `htop` - Улучшенная версия `top` с интерактивным интерфейсом.
>    - `mpstat` - Отображает использование CPU по ядрам.
>    - `sar` - Системный монитор с широкими возможностями анализа
>      производительности.
> 2. **Память (Memory)**:
>    - `free` - Показывает использование памяти и подкачки.
>    - `vmstat` - Отображает статистику по виртуальной памяти.
>    - `pmap` - Показывает отображение памяти процесса.
> 3. **IO (Input/Output)**:
>    - `iostat` - Отображает статистику ввода/вывода дисков.
>    - `iotop` - Показывает активность ввода/вывода процессов.
>    - `blktrace` - Утилита для трассировки блочных устройств.
> 4. **Network**:
>    - `iftop` - Отображает использование сети по интерфейсам.
>    - `nload` - Показывает текущую нагрузку сети в реальном времени.
>    - `iptraf` - Утилита для мониторинга сетевого трафика.
> 5. **Scheduler (Sched)**:
>    - `schedtop` - Отображает информацию о планировщике задач.
>    - `schedstat` - Показывает статистику планировщика.

6. **Cache**:
>    - `cachestat` - Отображает статистику использования кэша.
>    - `perf` - Мощный инструмент для анализа производительности, включая
>      кэширование.
>
> Каждая из этих утилит предоставляет уникальную информацию о соответствующей
> подсистеме и может быть использована для мониторинга и анализа
> производительности системы. Вы можете комбинировать их в зависимости от ваших
> конкретных потребностей и задач мониторинга.

#### Тесты


CPU:

```sh
# sar
(stress-ng --cpu 0 --cpu-method explog -t 20 &) && 
    (sar 1 20 -u >> cpu-explog-sar.log)
(stress-ng --cpu 0 --cpu-method int128 -t 20 &) &&
    (sar 1 20 -u >> cpu-int128-sar.log)

# pidstat
(stress-ng --cpu 0 --cpu-method explog -t 20 &) && 
    (timeout 20 watch -n 1 "pidstat -G stress-ng -u >> cpu-explog-pidstat.log")
(stress-ng --cpu 0 --cpu-method int128 -t 20 &) &&
    (timeout 20 watch -n 1 "pidstat -G stress-ng -u >> cpu-int128-pidstat.log")

# vmstat
(stress-ng --cpu 0 --cpu-method explog -t 20 &) && 
    (vmstat 1 20 >> cpu-explog-vmstat.log)
(stress-ng --cpu 0 --cpu-method int128 -t 20 &) &&
    (vmstat 1 20 >> cpu-int128-vmstat.log)

# mpstat
(stress-ng --cpu 0 --cpu-method explog -t 20 &) && 
    (timeout 20 watch -n 1 "mpstat -u  >> cpu-explog-mpstat.log")
(stress-ng --cpu 0 --cpu-method int128 -t 20 &) &&
    (timeout 20 watch -n 1 "mpstat -u >> cpu-int128-mpstat.log")

```

IO:

```sh
# pidstat
(stress-ng --io-uring 10 &) && 
    (timeout 20 watch -n 1 "pidstat -G stress-ng -d >> io-io-uring-pidstat.log")
(stress-ng --cpu 0 --ioport 10 &) &&
    (timeout 20 watch -n 1 "pidstat -G stress-ng -d >> io-ioport-pidstat.log")

#iostat
(stress-ng --io-uring 10 &) &&
    (timeout 20 watch -n 1 "iostat >> io-io-uring-iostat.log")
(stress-ng --cpu 0 --ioport 10 &) &&
    (timeout 20 watch -n 1 "iostat >> io-ioport-iostat.log")
```

Network:

```sh

(stress-ng --dccp 10 -t 20 &) && 
    (sar 1 20 -n ALL >> network-dccp-sar.log)

(stress-ng --cpu 0 --netlink-proc 10 -t 20 &) && 
    (sar 1 20 -n ALL >> network-netlink-proc-sar.log)
```

