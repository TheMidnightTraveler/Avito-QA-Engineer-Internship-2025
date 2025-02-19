# Найденные баги

## 1. Имя каждого созданного объявления имеет значение "dsdsd"
- **Эндпоинт**: `POST /api/1/item`
- **Серьезность**: Значительная  
- **Шаги воспроизведения**:
  1. Отправить `POST`-запрос на `/api/1/item` с телом, в котором `name` отличается от `"dsdsd"`:
     ```json
     {
       "name": "Тестовое имя",
       "sellerId": 123456,
       "price": 1000,
       "statistics": {...}
     }
     ```
  2. Получить ответ, содержащий `id` созданного объявления.
  3. Отправить `GET`-запрос `/api/1/item/{id}`.
- **Ожидаемый результат**: Значение `name` соответствует указанному при создании объявления.  
- **Фактический результат**: Значение `name` всегда равно `"dsdsd"`.

---

## 2. Объявление создается при отсутствии обязательных полей
- **Эндпоинт**: `POST /api/1/item`
- **Серьезность**: Критическая  
- **Шаги воспроизведения**:
  1. Отправить `POST`-запрос на `/api/1/item` с телом, в котором отсутствует одно или несколько обязательных полей (например, `sellerId`):
     ```json
     {
       "name": "Тестовое имя",
       "price": 1000,
       "statistics": {...}
     }
     ```
  2. Получить ответ, содержащий `id` созданного объявления.
  3. Отправить `GET`-запрос `/api/1/item/{id}`.
- **Ожидаемый результат**: Статус ответа — `400 Bad Request`.  
- **Фактический результат**: Статус ответа — `200 OK`, объявление создается.  
  - Отсутствующие поля принимают значения:  
    - `sellerId`, `price`, `contacts`, `likes`, `viewCount` → `0`  
    - `name` → `"dsdsd"`  

---

## 3. Объявление создается при `sellerId`, меньшем минимально допустимого значения (111111)
- **Эндпоинт**: `POST /api/1/item`
- **Серьезность**: Значительная  
- **Шаги воспроизведения**:
  1. Отправить `POST`-запрос на `/api/1/item` с `sellerId = 111110`, остальные поля корректны.
- **Ожидаемый результат**: Статус ответа — `400 Bad Request`.  
- **Фактический результат**: Статус ответа — `200 OK`, объявление создается с некорректным `sellerId`.

---

## 4. Объявление создается при `sellerId`, большем максимально допустимого значения (999999)
- **Эндпоинт**: `POST /api/1/item`
- **Серьезность**: Значительная  
- **Шаги воспроизведения**:
  1. Отправить `POST`-запрос на `/api/1/item` с `sellerId = 1000000`, остальные поля корректны.
- **Ожидаемый результат**: Статус ответа — `400 Bad Request`.  
- **Фактический результат**: Статус ответа — `200 OK`, объявление создается с некорректным `sellerId`.

---

## 5. Объявление создается с отрицательной ценой
- **Эндпоинт**: `POST /api/1/item`
- **Серьезность**: Значительная  
- **Шаги воспроизведения**:
  1. Отправить `POST`-запрос на `/api/1/item` с `price = -100`, остальные поля корректны.
- **Ожидаемый результат**: Статус ответа — `400 Bad Request`.  
- **Фактический результат**: Статус ответа — `200 OK`, объявление создается с отрицательной ценой.

---

## 6. Поле `messages` в теле ответа имеет значение `null` вместо `{}` (пустого словаря)
- **Эндпоинт**: `GET /api/1/item/{id}`
- **Серьезность**: Незначительная  
- **Шаги воспроизведения**:
  1. Отправить `GET`-запрос `/api/1/item/{id}` с `id` несуществующего объявления (например, `11111111-1111-1111-1111-111111111111`).
- **Ожидаемый результат**: Статус ответа — `404 Not Found`, тело ответа:
  ```json
  {
    "result": {
      "message": "item 9fe882ca-cc7c-4b3d-9083-c2f69e50ccd4 not found",
      "messages": {}
    },
    "status": "404"
  }
- **Фактический результат**: Статус ответа — `404 Not Found`, тело ответа:
  ```json
  {
  "result": {
    "message": "item 9fe882ca-cc7c-4b3d-9083-c2f69e50ccd4 not found",
    "messages": null
    },
    "status": "404"
  }
  ```

## 7. Статус ответа - 200 ОК при `sellerId` выходящим за диапозон
- **Эндпоинт**: GET /api/1/{sellerID}/item
- **Серьезность**: Незначительная
- **Шаги воспроизведения**:
  1. Отправить запрос, в котором `sellerID` равен 1000000 или 111110 (диапозон: 111111 - 999999):
- **Ожидаемый результат**: Статус ответа - 400 Bad Request
- **Фактический результат**: Статус ответ - 200 OK, в теле ответа пустой массив

## 8. Объявление создается при пустом названии объявления
- **Эндпоинт**: POST /api/1/item
- **Серьезность**: Значительная 
- **Шаги воспроизведения**:
  1. Отправить POST-запрос /api/1/item с телом, в котором поле `name` имеет значение "" (пустая строка), остальные поля корректные
- **Ожидаемый результат**: Статус ответа - 400 Bad Request
- **Фактический результат**: Статус ответ - 200 OK, объявление создано