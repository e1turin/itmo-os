# Задание 4. Сетевая файловая система

Ядро Linux — монолитное (https://en.wikipedia.org/wiki/Monolithic_kernel). Это
означает, что все его части работают в общем адресном пространстве. Однако, это
не означает, что для добавления какой-то возможности необходимо полностью
перекомпилировать ядро. Новую функциональность можно добавить в виде модуля
ядра.

Такие модули можно легко загружать и выгружать по необходимости прямо во время
работы системы.

С помощью модулей можно реализовать свои файловые системы, причём со стороны
пользователя такая файловая система ничем не будет отличаться от `ext4`
[https://en.wikipedia.org/wiki/Ext4](https://en.wikipedia.org/wiki/Ext4) или `NTFS`
[https://en.wikipedia.org/wiki/NTFS](https://en.wikipedia.org/wiki/NTFS). В
этом задании мы с Вами реализуем упрощённый аналог `NFS`
[https://en.wikipedia.org/wiki/Network_File_System](https://en.wikipedia.org/wiki/Network_File_System):
все файлы будут храниться на удалённом сервере, однако пользователь сможет
пользоваться ими точно так же, как и файлами на собственном жёстком диске.

*__Мы рекомендуем при выполнении этого домашнего задания использовать отдельную
виртуальную машину: любая ошибка может вывести всю систему из строя, и вы
можете потерять ваши данные. Для выполнения лабораторной работы понадобится 2
виртуальных машины, объединенных в сеть. На одну из виртуальных машин нужно
будет установить nfs-server.__*

Мы проверили работоспособность всех инструкций для дистрибутива Ubuntu 22.04
x64 [https://releases.ubuntu.com/22.04/](https://releases.ubuntu.com/22.04/) и
ядра версии 5.15.0-53. Возможно, при использовании других дистрибутивов, вы
столкнётесь с различными ошибками и особенностями, с которыми вам придётся
разобраться самостоятельно.

## Часть 1. Сервер файловой системы

Для получения токенов и тестирования вы можете воспользоваться консольной
утилитой curl [https://curl.se](https://curl.se).

Сервер поддерживает два типа ответов:

- Бинарные данные: набор байт (`char*`), который можно скастить в структуру,
  указанную в описании ответа. Учтите, что первое поле ответа (первые 8 байт) —
  код ошибки.
- JSON-объект [https://www.json.org/json-en.html](https://www.json.org/json-en.html):
  человекочитаемый ответ. Для его получения необходимо передавать GET-параметр
  `json`.

Формат JSON предлагается использовать только для отладки, поскольку текущая
реализация функции `networkfs_http_call` работает только с бинарным форматом.
Однако, вы можете её доработать и реализовать собственный JSON-парсер.

Поскольку в ядре используются не совсем привычные функции для работы с сетью,
мы реализовали для вас собственный HTTP-клиент в виде функции
`networkfs_http_call` (`http.c:120` (http.c#L120)):

- `const char *token` — ваш токен
- `const char *method` — название метода без неймспейса `fs` (`list`, `create`, ...)
- `char *response_buffer` — буфер для сохранения ответа от сервера
- `size_t buffer_size` — размер буфера
- `size_t arg_size` — количество аргументов
- далее должны следовать 2 $\times$ `arg_size` аргументов типа `const char*` —
  пары `param1`, `value1`, `param2`, `value2`, ... — параметры запроса

Функция возвращает 0, если запрос завершён успешно; положительное число — код
ошибки из документации API, если сервер вернул ошибку; отрицательное число —
код ошибки из `http.h` (http.h#L6) или `errno-base.h` (`ENOMEM`, `ENOSPC`) в случае
ошибки при выполнении запроса (отсутствие подключения, сбой в сети, некорректный
ответ сервера, ...).

## Часть 2. Знакомство с простым модулем

Давайте научимся компилировать и подключать тривиальный модуль. Для компиляции
модулей ядра нам понадобятся утилиты для сборки и заголовочные файлы.

Установить их можно так:

```sh
sudo apt-get install build-essential linux-headers-`uname -r`
```

Мы уже подготовили основу для вашего будущего модуля в файлах `entrypoint.c`
(entrypoint.c) и `Makefile` (Makefile). Познакомьтесь с ней.

Ядру для работы с модулем достаточно двух функций — одна должна
инициализировать модуль, а вторая — очищать результаты его работы. Они
указываются с помощью `module_init` и `module_exit`.

Важное отличие кода для ядра Linux от user-space-кода — в отсутствии в нём
стандартной библиотеки `libc`. Например, в ней же находится функция `printf`. Мы
можем печатать данные в системный лог с помощью функции `printk`
[https://www.kernel.org/doc/html/latest/core-api/printk-basics.html](https://www.kernel.org/doc/html/latest/core-api/printk-basics.html).
В Makefile указано, что наш модуль networkfs состоит из двух единиц трансляции
— `entrypoint` и `http`. Вы можете самостоятельно добавлять новые единицы,
чтобы декомпозировать ваш код удобным образом.

Соберём модуль:

Установить их можно так:

```sh
sudo make
```

Если наш код скомпилировался успешно, в текущей директории появится файл
`networkfs.ko` — это и есть наш модуль.

Осталось загрузить его в ядро:

```sh
sudo insmod networkfs.ko
```

Однако, мы не увидели нашего сообщения. Оно печатается не в терминал, а в
системный лог — его можно увидеть командой `dmesg`:

```sh
$ dmesg
<...>
[ 123.456789] Hello, World!

```

Для выгрузки модуля нам понадобится команда `rmmod`:

```sh
$ sudo rmmod networkfs
$ dmesg
<...>
[ 123.987654] Goodbye!
```

## Часть 3. Подготовка файловой системы

Операционная система предоставляет две функции для управления файловыми
системами:

- `register_filesystem` [https://www.kernel.org/doc/htmldocs/filesystems/API-re
gister-filesystem.html](https://www.kernel.org/doc/htmldocs/filesystems/API-re
gister-filesystem.html) — сообщает о появлении нового драйвера файловой
системы
- `unregister_filesystem` [https://www.kernel.org/doc/htmldocs/filesystems/API
-unregister-filesystem.html](https://www.kernel.org/doc/htmldocs/filesystems/API
-unregister-filesystem.html) — удаляет драйвер файловой системы 

В этой части мы начнём работать с несколькими структурами ядра:

- `inode` (https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L624) —
  описание метаданных файла: имя файла, расположение, тип файла (в нашем случае
  — регулярный файл или директория)
- `dentry` [https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/dcache.h#L91](https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/dcache.h#L91)
  — описание директории: список inode внутри неё, информация о родительской
  директории, ...
- `super_block` [https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L146](https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L146)
  — описание всей файловой системы: информация о корневой директории, …

Функции `register_filesystem` и `unregister_filesystem` принимают структуру с
описанием файловой системы. Начнём с такой:

```c
struct file_system_type networkfs_fs_type =
{
.name = "networkfs",
.mount = networkfs_mount,
.kill_sb = networkfs_kill_sb
};
```

Для монтирования файловой системы в этой структуре мы добавили два поля. Первое
— `mount` — указатель на функцию, которая вызывается при монтировании.

Например, она может выглядеть так:

```c
struct dentry* networkfs_mount(struct file_system_type *fs_type, 
                               int flags, const char *token, void *data)
{
    struct dentry *ret;
    ret = mount_nodev(fs_type, flags, data, networkfs_fill_super);
    if (ret == NULL)
    {
        printk(KERN_ERR "Can't mount file system");
    }
    else
    {
        printk(KERN_INFO "Mounted successfuly");
    }
    return ret;
}
```

Эта функция будет вызываться всякий раз, когда пользователь будет монтировать нашу
файловую систему. Например, он может это сделать следующей командой
(документация [https://linux.die.net/man/8/mount](https://linux.die.net/man/8/mount)):

```sh
sudo mount -t networkfs <token> <path>
```

Опция `-t` нужна для указания имени файловой системы — именно оно указывается в
поле name. Также мы передаём токен, полученный в прошлой части, и локальную
директорию, в которую ФС будет примонтирована. Обратите внимание, что эта
директория должна быть пуста.

Мы используем функцию `mount_nodev`
[https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L2476](https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L2476),
поскольку наша файловая система не хранится на каком-либо физическом устройстве:

```sh
struct dentry* mount_nodev(struct file_system_type *fs_type, 
                           int flags, void *data, 
                           int (*fill_super)(struct super_block *, void *, int));
```

Последний её аргумент — указатель на функцию `fill_super`. Эта функция должна
заполнять структуру `super_block` информацией о файловой системе. Давайте
начнём с такой функции:

```c
int networkfs_fill_super(struct super_block *sb, void *data, int silent)
{
    struct inode *inode;
    inode = networkfs_get_inode(sb, NULL, S_IFDIR, 1000);
    sb->s_root = d_make_root(inode);
    if (sb->s_root == NULL)
    {
        return -ENOMEM;
    }
    printk(KERN_INFO "return 0\n");
    return 0;
}
```

Аргументы `data` и `silent` нам не понадобятся. В этой функции мы используем
ещё одну (пока) неизвестную функцию — `networkfs_get_inode`. Она будет
создавать новую структуру `inode`, в нашем случае — для корня файловой системы:

```c
struct inode *networkfs_get_inode(struct super_block *sb, const struct inode *dir, 
                                  umode_t mode, int i_ino)
{
    struct inode *inode;
    inode = new_inode(sb);
    inode->i_ino = i_ino;
    if (inode != NULL)
    {
        inode_init_owner(inode, dir, mode);
    }
    return inode;
}
```

Давайте поймём, что эта функция делает. Файловой системе нужно знать, где
находится корень файловой системы. Для этого в поле `s_root` мы записываем
результат функции `d_make_root` [https://elixir.bootlin.com/linux/v5.15.53/source/fs/dcache.c#L2038](https://elixir.bootlin.com/linux/v5.15.53/source/fs/dcache.c#L2038)),
передавая ему корневую inode. На сервере корневая директория всегда имеет номер
1000.

Для создания новой `inode` используем функцию `new_inode`
[https://elixir.bootlin.com/linux/v5.15.53/source/fs/inode.c#L961](https://elixir.bootlin.com/linux/v5.15.53/source/fs/inode.c#L961).
Кроме этого, с помощью функции `inode_init_owner`
[https://elixir.bootlin.com/linux/v5.15.53/source/fs/inode.c#L2159](https://elixir.bootlin.com/linux/v5.15.53/source/fs/inode.c#L2159)
зададим тип ноды — укажем, что это директория.

На самом деле, `umode_t` содержит битовую маску, все значения которой доступны
в заголовочном файле `linux/stat.h`
[https://elixir.bootlin.com/linux/v5.15.53/source/include/uapi/linux/stat.h#L9](https://elixir.bootlin.com/linux/v5.15.53/source/include/uapi/linux/stat.h#L9)
— она задаёт тип объекта и права доступа.

Второе поле, которое мы определили в `file_system_type` — поле `kill_sb` —
указатель на функцию, которая вызывается при отмонтировании файловой системы. В
нашем случае ничего делать не нужно:

```c
void networkfs_kill_sb(struct super_block *sb)
{
    printk(KERN_INFO "networkfs super block is destroyed. Unmount
    successfully.\n");
}
```

Не забудьте зарегистрировать файловую систему в функции инициализации модуля, и
удалять её при очистке модуля. Наконец, соберём и примонтируем нашу файловую
систему:

```sh
$ sudo make
$ sudo insmod networkfs.ko
$ sudo mount -t networkfs 8c6a65c8-5ca6-49d7-a33d-daec00267011 /mnt/ct
```

Если вы всё правильно сделали, ошибок возникнуть не должно. Тем не менее, перейти
в директорию `/mnt/ct` не выйдет — ведь мы ещё не реализовали никаких
функций для навигации по ФС.

Теперь отмонтируем файловую систему:

```c
$ sudo umount /mnt/ct
```

## Часть 4. Вывод файлов и директорий

[[--TODO]]


