# Attendance Journal

![Tests](https://github.com/Taipan27/attendance-journal/actions/workflows/test.yml/badge.svg)
![Build](https://github.com/Taipan27/attendance-journal/actions/workflows/build.yml/badge.svg)
![Lint](https://github.com/Taipan27/attendance-journal/actions/workflows/lint.yml/badge.svg)

---

## 📌 Описание проекта

**Attendance Journal** — это десктопное приложение для учёта посещаемости студентов и управления расписанием. Интерфейс реализован на PyQt5, данные хранятся в формате JSON.

### Основной функционал:
- 👤 Авторизация и регистрация старосты
- 📅 Настройка расписания занятий (день недели, предмет, тип, время и продолжительность)
- 📓 Ведение журнала посещаемости студентов
- 📝 Редактирование информации о студентах
- 📊 Автоматический расчёт статистики посещаемости
- 💾 Сохранение данных локально в JSON

---

## ⚙️ Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
python main.py
```

---

## 🧪 Настроенные Workflows (CI/CD)

| Workflow     | Назначение                                                                 | Событие запуска                          |
|--------------|----------------------------------------------------------------------------|------------------------------------------|
| `test.yml`   | Автоматически запускает тесты с помощью `pytest`, чтобы убедиться, что всё работает корректно | При каждом push и pull request в ветку `main` |
| `build.yml`  | Выполняет сборку проекта с помощью `pyinstaller`                           | При push в ветку `main`                 |
| `lint.yml`   | Проверяет код на ошибки и соответствие PEP8 с помощью `flake8`              | При каждом push и pull request          |

---

## 📁 Структура проекта

```
attendance-journal/
├── main.py               # Главный исполняемый файл
├── users.json            # Данные о пользователях и расписаниях
├── requirements.txt      # Зависимости проекта
├── .github/
│   └── workflows/
│       ├── test.yml      # Тестирование
│       ├── build.yml     # Сборка
│       └── lint.yml      # Проверка кода
└── README.md             # Документация проекта
```

---

## 🛠️ Используемые технологии

- Python 3.10+
- PyQt5
- JSON
- Git & GitHub
- GitHub Actions

---

## 💬 Контакты
Автор: **Taipan27**

---

## 📄 Лицензия
Этот проект лицензирован под лицензией MIT. См. файл LICENSE для получения подробностей.
