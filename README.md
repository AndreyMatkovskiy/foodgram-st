# 🍽️ FoodGram
## 🧾 Описание проекта
**FoodGram** — это веб-приложение для публикации и поиска кулинарных рецептов.  
Пользователи могут:
- 👤 Регистрироваться и входить в систему (JWT, Djoser)
- 📋 Просматривать рецепты с фильтрацией по тегам, авторам и ингредиентам
- ⭐ Добавлять рецепты в избранное
- 🛒 Формировать список покупок по выбранным рецептам
- 📥 Скачать список покупок в формате PDF
- 👥 Подписываться на любимых авторов рецептов
- 🖼️ Загружать изображения рецептов

---

## 🚀Шаги по запуску проекта

1. **Клонируйте репозиторий**  
```bash
git clone https://github.com/AndreyMatkovskiy/foodgram-st.git
cd foodgram-st
```
2. **Создайте виртуальное окружение**
```bash
python -m venv venv
source venv/Scripts/activate
```
  3. **Установите зависимости**
```bash
cd infra
pip install -r requirements.txt
```
4. **Запустите Docker Desktop**
5. **Соберите фротенд**
```bash
# Находясь в infra:
docker run --rm \
  -v /d/Dev/foodgram-st/foodgram-st/frontend:/app \
  -w /app \
  node:16-alpine \
  sh -c "npm install && npm run build"
```
5. **Настройте окружение**
```bash
cp .env.example .env
# Отредактируйте .env: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, SECRET_KEY, ALLOWED_HOSTS, BASE_URL
```
6. **Поднимите контейнеры**
```bash
docker-compose up -d --build
```
7. **Создайте суперпользователя**
```bash
docker-compose exec backend python manage.py createsuperuser
```
8. **Загрузите фикстуры тегов и ингредиентов**
``` bash
docker-compose exec backend python manage.py loaddata backend/fixtures/ingredients_fixture.json # <- Фикстура ингредиентов
docker-compose exec backend python manage.py loaddata backend/fixtures/tags_fixture.json # <- Фикстура тегов
```
✅Готово! Теперь у вас рабочий сайт!
❓Проверить работу:
- https://localhost:8000/ - основная страница сайта
- https://localhost:8000/admin/ - админ-панель сайта
## ⚙️ Основной функционал

| Сервис       | Описание                                                               |
| ------------ | ---------------------------------------------------------------------- |
| Регистрация  | Логин/пароль, соцсети (OAuth2 через social-auth-app-django)            |
| Рецепты      | CRUD операций, фильтрация, пагинация                                   |
| Избранное    | Добавление/удаление рецептов в личное «Избранное»                      |
| Корзина      | Формирование списка ингредиентов, скачивание списка покупок            |
| Подписки     | Подписка/отписка на авторов, просмотр ленты новых рецептов подписанных |
| Админ-панель | Управление пользователями, рецептами, ингредиентами, тегами            |

👨‍💻 Автор: *Матковский Андрей*