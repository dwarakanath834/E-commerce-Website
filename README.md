# ShopEase

ShopEase is a responsive Django storefront with customer accounts, a searchable product catalog, stock-aware shopping carts, demo checkout, order tracking, verified-buyer reviews, and a staff dashboard. Django templates and the ORM power the application; there is no separate JavaScript framework.

## Requirements

- Python 3.12 or newer
- MySQL 8+ for a MySQL deployment, or SQLite for local development
- Internet access for the bundled Bootstrap/font CDN and sample product photography

## Local setup (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. SQLite is the default and needs no separate service. Create a staff user with `createsuperuser` to use `/dashboard/` and Django's full product/category/customer/review management at `/admin/`.

## MySQL configuration

Create a database and application user in MySQL, then set the values in `.env`:

```dotenv
DJANGO_SECRET_KEY=use-a-long-random-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=shop.example.com
DB_ENGINE=mysql
MYSQL_DATABASE=shopease
MYSQL_USER=shopease_user
MYSQL_PASSWORD=your-local-database-password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

`PyMySQL` provides the MySQL adapter, so a separate native compiler or `mysqlclient` wheel is not needed. The connection uses `utf8mb4`. Never commit `.env`; production deployments should provide a unique secret and configure HTTPS, secure cookies, email delivery, media storage and backups.

## Customer journeys

- Register, sign in/out, edit account details, change a password, or request a reset link. Reset mail is written to the development console by default.
- Browse categories, search product names/descriptions, sort by price or newest, and view availability and reviews.
- Add, update or remove cart items. Quantities are validated against stock on every write.
- Place a demo-card or cash-on-delivery order. The checkout transaction locks stock rows, snapshots product names/prices and deducts inventory. No payment is processed.
- View only your own orders, track the current status, and cancel a pending order. Cancellation restores inventory.
- Submit one review per product after a non-cancelled purchase.
- Staff use `/dashboard/` for sales/order overview and order status updates; `/admin/` provides full catalog, account, inventory and review CRUD.

## Database and sample catalog

The domain models are split across `accounts`, `catalog`, `cartapp`, `orders` and `reviews`. Django's built-in `User` model is used with a one-to-one profile; addresses, categories, products, carts, orders and reviews are stored through Django ORM relationships and database constraints. Product/profile image uploads use Pillow-backed `ImageField`s. Demo catalog images use remote Unsplash image URLs; staff can upload local product images in Django admin.

`python manage.py seed_demo` creates six sample categories and 20 products and is safe to rerun.

## Tests and checks

```powershell
python manage.py check
python manage.py test catalog.tests
```

The test suite covers registration/password hashing, login-required access, catalog filtering, cart stock limits, checkout and stock deduction, customer-specific order access, cancellation/restocking, review eligibility and staff authorization/status changes. For a live MySQL check, configure `.env`, ensure the MySQL service is running, and rerun the same commands.

## Notes

- Django's CSRF middleware protects POST forms; customer-facing order and cart views scope records to the signed-in user.
- The sample password reset backend prints email contents to the terminal. Configure SMTP for a deployed site.
- The payment choices are demonstrations only and deliberately do not collect card details or contact a payment gateway.