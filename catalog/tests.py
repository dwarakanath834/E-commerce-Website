from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from cartapp.models import Cart, CartItem
from catalog.models import Category, Product
from orders.models import Order, OrderItem
from reviews.models import Review

User = get_user_model()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ShopFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Home & Living")
        self.product = Product.objects.create(
            name="Ceramic cup", category=self.category, description="A handmade cup.", price="24.00", stock=8
        )
        self.customer = User.objects.create_user(username="sam", password="A-strong-test-pass-934", email="sam@example.com")
        self.other_customer = User.objects.create_user(username="lee", password="A-strong-test-pass-934")

    def test_registration_login_logout_and_profile(self):
        response = self.client.post(reverse("register"), {
            "username": "new-shopper", "first_name": "New", "last_name": "Shopper",
            "email": "new@example.com", "password1": "A-strong-test-pass-734", "password2": "A-strong-test-pass-734",
        })
        self.assertRedirects(response, reverse("home"))
        created = User.objects.get(username="new-shopper")
        self.assertTrue(created.check_password("A-strong-test-pass-734"))
        self.assertTrue(created.profile)
        self.assertEqual(self.client.get(reverse("profile")).status_code, 200)
        self.client.post(reverse("logout"))
        self.assertRedirects(self.client.get(reverse("cart_detail")), f"{reverse('login')}?next={reverse('cart_detail')}")
        self.assertTrue(self.client.login(username="sam", password="A-strong-test-pass-934"))

    def test_product_search_category_and_price_sort(self):
        second = Product.objects.create(name="Woven basket", category=self.category, description="Natural fibre.", price="18.00", stock=4)
        response = self.client.get(reverse("product_list"), {"q": "woven", "category": self.category.slug, "sort": "price-low"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, second.name)
        self.assertNotContains(response, self.product.name)

    def test_password_reset_page_uses_shopease_account_flow(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Let's get you")

    def test_cart_rejects_quantity_above_stock_and_updates_quantity(self):
        self.client.force_login(self.customer)
        add_url = reverse("add_to_cart", args=[self.product.pk])
        self.client.post(add_url, {"quantity": 3})
        item = CartItem.objects.get(cart__user=self.customer, product=self.product)
        self.assertEqual(item.quantity, 3)
        self.client.post(add_url, {"quantity": 6})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)
        self.client.post(reverse("update_cart_item", args=[item.pk]), {"quantity": 5})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_guest_add_to_cart_resumes_after_sign_in(self):
        response = self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"quantity": 2})
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('resume_pending_cart')}")
        response = self.client.post(reverse("login"), {
            "username": "sam", "password": "A-strong-test-pass-934", "next": reverse("resume_pending_cart"),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("resume_pending_cart"))
        response = self.client.get(response["Location"])
        self.assertRedirects(response, reverse("cart_detail"))
        self.assertEqual(CartItem.objects.get(cart__user=self.customer, product=self.product).quantity, 2)

    def test_checkout_decrements_stock_and_creates_private_order(self):
        self.client.force_login(self.customer)
        cart, _ = Cart.objects.get_or_create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        response = self.client.post(reverse("checkout"), {
            "full_name": "Sam Shopper", "email": "sam@example.com", "phone": "555-0101",
            "street": "12 Market Street", "city": "Portland", "state": "Oregon", "postal_code": "97201",
            "payment_method": "demo_card", "save_address": "on",
        })
        order = Order.objects.get(user=self.customer)
        self.assertRedirects(response, reverse("order_detail", args=[order.number]))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 6)
        self.assertEqual(order.total, self.product.price * 2)
        self.assertFalse(cart.items.exists())
        self.assertEqual(self.client.get(reverse("order_detail", args=[order.number])).status_code, 200)
        self.client.force_login(self.other_customer)
        self.assertEqual(self.client.get(reverse("order_detail", args=[order.number])).status_code, 404)

    def test_customer_can_cancel_pending_order_and_stock_is_restored(self):
        order = self.make_order()
        self.client.force_login(self.customer)
        self.client.post(reverse("cancel_order", args=[order.number]))
        order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.product.stock, 8)

    def test_only_verified_buyers_can_review_and_duplicate_reviews_are_blocked(self):
        self.client.force_login(self.customer)
        review_url = reverse("create_review", args=[self.product.pk])
        payload = {"rating": "5", "title": "A daily favourite", "body": "Feels wonderful and looks lovely."}
        self.client.post(review_url, payload)
        self.assertFalse(Review.objects.exists())
        order = self.make_order(status=Order.Status.DELIVERED)
        self.client.post(review_url, payload)
        self.client.post(review_url, payload)
        self.assertEqual(Review.objects.filter(product=self.product, user=self.customer).count(), 1)

    def test_staff_can_update_status_but_customers_cannot_open_dashboard(self):
        order = self.make_order()
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)
        staff = User.objects.create_user(username="manager", password="A-strong-test-pass-824", is_staff=True)
        self.client.force_login(staff)
        response = self.client.post(reverse("update_order_status", args=[order.number]), {"status": Order.Status.CONFIRMED})
        self.assertRedirects(response, reverse("dashboard"))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)

    def make_order(self, status=Order.Status.PENDING):
        order = Order.objects.create(
            user=self.customer, number=f"SETEST{Order.objects.count() + 1}", status=status,
            payment_method=Order.PaymentMethod.DEMO_CARD, full_name="Sam Shopper", email="sam@example.com",
            phone="555-0101", street="12 Market Street", city="Portland", state="Oregon", postal_code="97201",
            subtotal="48.00", shipping="0.00", total="48.00",
        )
        OrderItem.objects.create(order=order, product=self.product, product_name=self.product.name, unit_price="24.00", quantity=2)
        self.product.stock = 6
        self.product.save(update_fields=["stock"])
        return order