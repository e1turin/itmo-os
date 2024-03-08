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

- - -

### Комментарии

Для нагрузки CPU выдаются варианты параметра `--cpu-method <method>`:

> specify a cpu stress method. By default, all the stress methods  are  exer‐
> cised  sequentially,  however one can specify just one method to be used if
> required.  Available cpu stress methods are described as follows: <...>
>
> - `explog` - iterate on n = exp(log(n) ÷ 1.00002)
> - `int128` - 1000 iterations of a mix of 128 bit integer operations (GCC only).

Чтобы построить графики нагрузки CPU, думаю можно измерять температуру ядра
(опция `--tz` в stress-ng) или количество исполненных инструкций и циклов исполнения.
Но оба из этих подходов требуют запуска кода на хостовой системе.

```sh
stress-ng --taskset 0,1,5-7 --matrix 5

# to measure cycles & instructions overl all (-a) system
sudo perf stat -B -ecycles:u,instructions:u -a sleep 5

# single command
## explog
(stress-ng --cpu 1 --cpu-method explog -t 20 &) &&
    (export PID=`ps -a | grep stress-ng | tail -n 1 | 
        python3 -c "print(input().split()[0])"` && 
     watch -n 1 "pidstat -ul -p $PID >> cpu-test-explog.log")

## int128
(stress-ng --cpu 1 --cpu-method int128 -t 20 &) &&
    (export PID=`ps -a | grep stress-ng | tail -n 1 | 
        python3 -c "print(input().split()[0])"` && 
     watch -n 1 "pidstat -ul -p $PID >> cpu-test-int128.log")


```

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
