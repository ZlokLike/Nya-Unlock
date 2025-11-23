# Nya.Unlock - MultiTool System Utility

![Version](https://img.shields.io/badge/version-1.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Admin](https://img.shields.io/badge/requires-admin%20rights-orange)

## 🇷🇺 Русская версия

### Описание
Nya.Unlock - это многофункциональная системная утилита для Windows, предоставляющая расширенные возможности управления системой, восстановления и борьбы с вирусными заражениями. Программа разработана для работы в обычном режиме, режиме администратора и даже в среде восстановления Windows.

### 🦠 **Антивирусные возможности и восстановление системы**

#### **Обход вирусных блокировок:**
- Разблокировка диспетчера задач (часто блокируется вирусами)
- Восстановление доступа к дискам и разделам
- Снятие ограничений реестра, наложенных вредоносным ПО
- Обход блокировок системных утилит

#### **Восстановление после вирусных атак:**
- **Восстановление шрифтов** - возврат к стандартным шрифтам Windows после замены их вирусами
- **Восстановление курсора** - сброс изменений, внесенных вредоносным ПО
- **Исправление настроек мыши** - восстановление нормального поведения кнопок мыши
- **Очистка автозагрузки** - удаление вирусных записей из автозагрузки

#### **Удаление вирусных процессов:**
- Принудительное завершение вредоносных процессов
- Заморозка подозрительной активности
- Управление службами, созданными вирусами
- Удаление вирусных служб из системы

### Основные возможности

#### 🛠️ **Инструменты разблокировки системы**
- **Восстановление шрифтов** - возврат к стандартным шрифтам Windows с созданием резервной копии нестандартных
- **Восстановление курсора** - сброс настроек курсора к стандартным значениям
- **Исправление кнопок мыши** - восстановление нормального порядка кнопок мыши
- **Разблокировка диспетчера задач** - удаление ограничений на запуск диспетчера задач
- **Разблокировка дисков** - восстановление доступа к скрытым дискам и разделам

#### ⚡ **Диспетчер задач**
- Просмотр всех запущенных процессов с детальной информацией (PID, CPU, память, статус)
- Управление процессами: завершение, заморозка/разморозка
- Отметка критических процессов для предотвращения случайного завершения
- Управление службами Windows: запуск, остановка, удаление

#### 🔧 **Управление автозагрузкой**
- Просмотр и редактирование записей автозагрузки в реестре (HKCU/HKLM)
- Управление папками автозагрузки для текущего пользователя и всех пользователей
- Просмотр задач автозагрузки в Планировщике заданий
- Добавление и удаление программ из автозагрузки

#### 🛡️ **MBR Recovery**
- Создание резервных копий Master Boot Record
- Восстановление MBR из бэкапа
- Восстановление стандартного MBR Windows
- Поддержка работы с физическими дисками

#### 🖥️ **Встроенная консоль**
- Полнофункциональная консоль с поддержкой русских символов
- Прямое выполнение команд CMD
- Поддержка горячих клавиш для навигации

#### 📁 **Утилиты**
- **Explorer++** - улучшенный файловый менеджер
- Автоматическая загрузка и установка утилит

### Системные требования
- **ОС:** Windows 7/8/10/11
- **Права:** Рекомендуются права администратора для полного функционала
- **Память:** Не менее 512MB ОЗУ

### Установка и запуск

#### Автономная версия:
```bash
# Запуск с правами администратора
Nya.Unlock.exe
```

#### Из исходного кода:
```bash
python main.py
```

### Безопасность
⚠️ **ВНИМАНИЕ:** Некоторые функции (удаление служб, восстановление MBR) могут привести к нестабильной работе системы. Используйте с осторожностью!

---

## 🇺🇸 English Version

### Description
Nya.Unlock is a multifunctional system utility for Windows that provides advanced system management, recovery, and anti-virus capabilities. The program is designed to work in normal mode, administrator mode, and even in Windows Recovery Environment.

### 🦠 **Anti-virus Capabilities and System Recovery**

#### **Bypassing Virus Blockades:**
- Task Manager unlock (often blocked by viruses)
- Restore access to drives and partitions
- Remove registry restrictions imposed by malware
- Bypass system utility blocks

#### **Recovery After Virus Attacks:**
- **Font Restoration** - revert to standard Windows fonts after virus modifications
- **Cursor Restoration** - reset changes made by malicious software
- **Mouse Settings Fix** - restore normal mouse button behavior
- **Startup Cleaning** - remove virus entries from startup

#### **Virus Process Removal:**
- Force termination of malicious processes
- Freeze suspicious activity
- Management of virus-created services
- Removal of virus services from system

### Key Features

#### 🛠️ **System Unlock Tools**
- **Font Restoration** - revert to standard Windows fonts with backup of non-standard fonts
- **Cursor Restoration** - reset cursor settings to default values
- **Mouse Button Fix** - restore normal mouse button order
- **Task Manager Unlock** - remove restrictions on Task Manager launch
- **Drive Unlock** - restore access to hidden drives and partitions

#### ⚡ **Task Manager**
- View all running processes with detailed information (PID, CPU, memory, status)
- Process management: terminate, freeze/unfreeze
- Mark critical processes to prevent accidental termination
- Windows services management: start, stop, delete

#### 🔧 **Startup Management**
- View and edit startup entries in registry (HKCU/HKLM)
- Manage startup folders for current user and all users
- View startup tasks in Task Scheduler
- Add and remove programs from startup

#### 🛡️ **MBR Recovery**
- Create Master Boot Record backups
- Restore MBR from backup
- Restore standard Windows MBR
- Support for working with physical disks

#### 🖥️ **Built-in Console**
- Fully functional console with Russian character support
- Direct CMD command execution
- Hotkey support for navigation

#### 📁 **Utilities**
- **Explorer++** - enhanced file manager
- Automatic utility download and installation

### System Requirements
- **OS:** Windows 7/10/11
- **Rights:** Administrator rights recommended for full functionality
- **Memory:** At least 512MB RAM

### Installation and Launch

#### Standalone version:
```bash
# Run with administrator rights
Nya.Unlock.exe
```

#### From source code:
```bash
python main.py
```

### Security
⚠️ **WARNING:** Some features (service deletion, MBR restoration) may lead to system instability. Use with caution!

---
```
## 📁 Project Structure
Nya.Unlock/
├── main.py                 # Main application file
├── bin/                    # Utilities directory
│   └── explorerpp/         # Explorer++ file manager
└── README.md              # This file
```
## 🐛 Bug Reports and Support
For bug reports and feature requests, please create an issue in the project repository.
