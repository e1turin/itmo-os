# Лабораторная работа №4

Разработка собственной файловой системы.

## Задание

Мануал по разработке в задании к лабе; там же есть/будут мои комментарии по
выполнению

- [TASK.md](./TASK.md)

## Чужие решения

1. Java server + C client: данные хранятся в базе в виде строчек
    - https://github.com/Andryss/NFSAPI/
    - https://github.com/Andryss/OperatingSystemsLabWork4
2. Java + C client (похожее на 1.)
    - https://github.com/vityaman-edu/os-networkfs/blob/8-module-linufs-web-rw/module/linufs_local.c
3. C++ http server + C client: данные хранятся на сервере в ОЗУ, inode просто указывает на какую-то область памяти.
    - https://github.com/Malevrovich/os-awesome-filesystem/

## Референсы

- https://linux-kernel-labs.github.io/refs/heads/master/labs/kernel_modules.html
- https://sysprog21.github.io/lkmpg/
- https://sysprog21.github.io/lkmpg/#the-proc-file-system
- https://www.kernel.org/doc/html/latest/kbuild/modules.html
- http://ruslinux.net/MyLDP/BOOKS/drivers/linux-device-drivers-00.html
- https://developer.ibm.com/technologies/linux/articles/l-linux-kernel/

- - -

## Комментарии

Очевидно, что нужно каким-то образом на сервере хранить данные. Это можно
сделать в тупую аллоцируя в куче место, а можно действительно записывать данные
в базу. СУБД поддерживают возможности записи в них бинарных байлов. 

Еще можно просто так же хранить файлы в файловой системе на сервере, просто
прогонять их через серверное приложение.

На клиенте же нужно разработать модуль ядра, который будет выполнять роль
драйвера файловой системы. 

