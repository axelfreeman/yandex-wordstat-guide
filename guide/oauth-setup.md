# OAuth: Как получить доступ к Wordstat API

## Шаг 1: Создать приложение в Яндекс.OAuth

1. Откройте https://oauth.yandex.ru/
2. Нажмите «Создать приложение»
3. Название: `wordstat-collector`
4. Платформа: Веб-сервис
5. Права: выберите `search-api.webSearchUser`

После создания вы получите:
- **Client ID** — публичный идентификатор
- **Client Secret** — секретный ключ

## Шаг 2: Получить IAM-токен

```bash
# Обменять OAuth-токен на IAM-токен
curl -d '{"yandexPassportOauthToken":"y0_..."}' \
  https://iam.api.cloud.yandex.net/iam/v1/tokens

# Ответ:
# {"iamToken":"t1.9...","expiresAt":"2026-07-21T15:00:00Z"}
```

IAM-токен живёт 12 часов. Для production используйте сервисный аккаунт с API-ключом.

## Шаг 3: Создать API-ключ (для production)

1. Яндекс.Облако → Сервисные аккаунты → Создать
2. Имя: `wordstat-bot`
3. Роль: `search-api.webSearchUser`
4. Сервисный аккаунт → Создать API-ключ
5. Сохранить значение (показывается один раз)

## Шаг 4: Пополнить баланс

1. Яндекс.Облако → Биллинг
2. Пополнить на 500 ₽
3. Этого хватит на ~4 месяца активного использования

## Шаг 5: Проверить

```bash
export WORDSTAT_API_KEY="AQVN..."
export WORDSTAT_FOLDER_ID="b1g..."

curl -sX POST 'https://searchapi.api.cloud.yandex.net/v2/wordstat/topRequests' \
  -H "Authorization: Api-Key $WORDSTAT_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "{\"phrase\":\"тест\",\"numPhrases\":2,\"folderId\":\"$WORDSTAT_FOLDER_ID\"}"
```

Успешный ответ:
```json
{"results": [{"phrase": "тест", "count": "1234"}], "totalCount": "1234"}
```
