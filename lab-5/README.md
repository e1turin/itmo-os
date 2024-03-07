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

Думаю ...

```???
stress-ng --taskset 0,1,5-7 --matrix 5
```

```

```

