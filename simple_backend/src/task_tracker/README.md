
- что улучшилось после того, как список из оперативной памяти изменился на файл проекта?

    -сохраняются введеные данные после выключения бэкенда.
    -сохраняется ранее развернутый выпадающий список

- избавились ли мы таким способом от хранения состояния или нет?

    -думаю да из-за того, что сгружается инфа в отдельный файл и его можно использовать.

- где еще можно хранить задачи и какие есть преимущества и недостатки этих подходов?

    Базы данных:
    Преимущества: гарантированная целостность данных, поддержка многопользовательского доступа, масштабируемость, удобный язык запросов.
    Недостатки: требует настройки и поддержки, может быть излишним для простых проектов.

    Облачные сервисы хранения:
    Преимущества: не нужно беспокоиться о серверном оборудовании, автоматическое масштабирование, доступ из любой точки.
    Недостатки: зависимость от стороннего сервиса, возможные задержки, ограничения бесплатных тарифов.

- Прочитайте что такое "состояние гонки" и напишите в readme файле о том, какие проблемы остались в бекенде на данном этапе проекта. Есть ли у вас какое-то решение этой проблемы?

    Может возникнуть конфликт при одновременном создании, удалении, изменении и тд
    нет блокировки файла во время чтения или записи
    если запись прервется из-за ошибки, то данные могут быть неполными(неполная запись)

    Решение:
    Использование блокировок
    Использование очередей задач
    Интеграция с облачными сервисами
