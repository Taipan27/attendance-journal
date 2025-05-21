# Attendance Journal

Приложение для учёта посещаемости студентов и управления расписанием. Реализовано на PyQt5.

## 🚀 Функциональность

- Авторизация и регистрация старосты
- Настройка расписания занятий (день недели, предмет, тип, время и продолжительность)
- Ведение журнала посещаемости студентов
- Возможность редактирования информации о студентах
- Автоматический расчёт статистики посещаемости
- Сохранение данных в JSON-файл

## 🛠️ Используемые технологии

- Python 3
- PyQt5
- JSON (для хранения данных)
- Git & GitHub

## 🧱 Структура проекта

attendance-journal/
│
├── main.py # Главный исполняемый файл
├── users.json # Хранение пользователей и данных
├── README.md # Этот файл
├── .gitignore # Игнорируемые файлы и папки
└── LICENSE # MIT License

## 📦 Установка и запуск

1. Установите зависимости:

   ```bash
   pip install PyQt5
2. Запуск приложения

   ```bash
   python main.py
# Attendance-Journal

![Tests](https://github.com/Taipan27/attendance-journal/actions/workflows/test.yml/badge.svg)
![Lint](https://github.com/Taipan27/attendance-journal/actions/workflows/lint.yml/badge.svg)
![Deploy](https://github.com/Taipan27/attendance-journal/actions/workflows/deploy.yml/badge.svg)

> Автоматизация CI/CD построена на GitHub Actions:
> * **Tests** – pytest + coverage  
> * **Lint**  – flake8 (PEP 8)  
> * **Deploy** – сборка zip-релиза при пуше тега `v*`  

### Как это работает

| Workflow | Триггер | Job-ы | Результат |
|-----------|---------|-------|-----------|
| `test.yml` | `push`, `pull_request` | checkout ➜ install ➜ **pytest** | падает, если тест не прошёл |
| `lint.yml` | `push`, `pull_request` | checkout ➜ **flake8** | падает, если стиль нарушен |
| `deploy.yml` | `push` тега `v*` | checkout ➜ zip ➜ **release** | создаёт релиз с архивом |

