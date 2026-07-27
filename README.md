### Hexlet tests and linter status:
[![Actions Status](https://github.com/kirillchistov/python-project-50/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/kirillchistov/python-project-50/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/89fb74bf24d683a10a5a/maintainability)](https://codeclimate.com/github/kirillchistov/python-project-50/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/89fb74bf24d683a10a5a/test_coverage)](https://codeclimate.com/github/kirillchistov/python-project-50/test_coverage)
![Github Actions](https://github.com/kirillchistov/python-project-50/actions/workflows/pyci.yml/badge.svg)

[![Quality gate status](https://sonarcloud.io/api/project_badges/measure?project=kirillchistov_python-project-50&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=kirillchistov_python-project-50)

## Gendiff Difference Calculator «Вычислитель отличий»
— Это программа, которая определяет разницу между двумя структурами данных. Это популярная задача, для которой существуют онлайн-сервисы вроде jsondiff; похожий механизм используется при выводе тестов и при отслеживании изменений в конфигурационных файлах.

## Возможности утилиты:
- Поддержка разных входных форматов: YAML, JSON
- Генерация отчёта в форматах plain text, stylish и JSON

## Пример использования:

```bash
gendiff filepath1.json filepath2.json
```

```text
{
  - follow: false
    host: hexlet.io
  - proxy: 123.234.53.22
  - timeout: 50
  + timeout: 20
  + verbose: true
}
```

Как библиотека:

```python
from gendiff import generate_diff

diff = generate_diff(file_path1, file_path2)
print(diff)
```

## Демонстрация:
[![asciicast](https://asciinema.org/a/3DlY2swpPq8uPGE3)](https://asciinema.org/a/3DlY2swpPq8uPGE3)

## Шаг 6:
- [x] Подключите линтер (файл конфигурации). Должна работать команда make lint
- [x] Подключите Github Actions, SonarQube и бейджики (badges) для них. Все эти настройки выполняются через кнопки в интерфейсе. В качестве эталона можете взять экшн нашего бойлерплейт-пакета
- [x] Напишите тесты, которые проверяют корректность сравнения плоских JSON-файлов
- [x] Добавьте запуск тестов и линтера на Github Actions
- [x] Настройте отправку покрытия кода на SonarQube, добавьте в README бэйджик для Test Coverage


## Шаг 5:
- [x] Реализуйте возможность использования пакета как библиотеки.
- [x] Реализуйте поиск различий между двумя плоскими (только пары ключ-значение) json-файлами. Вывод должен быть таким, как показано сверху
- [x] Добавьте в ридми [аскинему с примером работы пакета](https://asciinema.org/a/3DlY2swpPq8uPGE3)

## Шаг 4:
- [x] Создайте файлы на основе данных приведенных выше
- [x] Реализуйте чтение и парсинг файлов
- [x] Не создавайте слишком много файлов с кодом. На этом этапе решение занимает пару десятков строк. Выносить имеет смысл только тогда, когда код начинает мешаться.
- [x] Результат:  программа умеет читать JSON-файлы и парсить их содержимое. При запуске gendiff filepath1.json filepath2.json приложение принимает аргументы и обращается к файлам.

## Шаг 3:
- [x] Модифицируйте скрипт (точку входа) gendiff так, чтобы при запуске с флагом -h выводилась справка, как указано выше
- [x] Выполните сборку пакета

## Шаг 2:
- [x] Склонируйте созданный репозиторий проекта локально и инициализируйте ваш пакет внутри корневой директории проекта. Используйте для этого команду uv init. Задайте имя пакета в pyproject.toml — hexlet-code
- [x] Создайте скрипт, точку входа, gendiff, который будет запускать ваше приложение. Скрипт при запуске с флагом -h выводит справку, как указано выше.

## Шаг 1: Инициализация
- [x] Посмотрите и разоберитесь в [демонстрации работы проекта](https://asciinema.org/a/Pe6QypnLEmFWssNAjCOJN1iii)
- [x] Подготовьте рабочее окружение к разработке: убедитесь, что установлен и настроен редактор кода и окружение готово к работе с проектом.
