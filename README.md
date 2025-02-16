# Avito QA Engineer Internship

## Требования
- Python 3.6+
- Установленный пакетный менеджер pip
- Доступ в интернет

## Установка

### 1. Склонируйте репозиторий или скачайте
```bash
git clone 
```

### 2. Перейдите в папку с репозиторием

### 3. Создайте виртуальное окружение
```bash
python -m venv .venv
```

### 4. Активируйте виртуальное окружение
- На Windows через cmd.exe:
```bash
C:\> <venv>\Scripts\activate.bat
```
- На POSIX через bash/zsh:
```bash
source <venv>/bin/activate
```

### 5. Установите зависимости
```bash
pip install -r requirements.txt
```

## Использование
Для запуска всех тестов выполните команду:
```bash
pytest
```

Для более подробного отчета можно использовать флаг `-v`:
```bash
pytest -v
```