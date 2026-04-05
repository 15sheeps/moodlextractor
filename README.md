# Moodle Question Exporter

Экспортирует вопросы из Moodle в HTML-файл с встроенными изображениями (base64).

## Использование

```bash
python script.py -name "output" -url "https://moodle.site/question/bank.php" -quality 85 -sesskey "ваш_sesskey" -session "ваш_cookie"
