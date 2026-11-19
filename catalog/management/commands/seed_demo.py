from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Category, Product


CATEGORIES = {
    "Technology": ("tech", "https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&w=700&q=80"),
    "Style": ("style", "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=700&q=80"),
    "Home & Living": ("home-living", "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=700&q=80"),
    "Books": ("books", "https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=700&q=80"),
    "Wellness": ("wellness", "https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=700&q=80"),
    "Outdoors": ("outdoors", "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=700&q=80"),
}

PRODUCTS = [
    ("Ceramic pour-over set", "Home & Living", "A quietly beautiful stoneware dripper and matching cup for slow, satisfying mornings.", "38.00", 24, True, "photo-1495474472287-4d71bcdd2085"),
    ("Everyday wireless headphones", "Technology", "Comfort-first over-ear headphones with warm sound, clear calls and a long-lasting battery.", "89.00", 18, True, "photo-1505740420928-5e560c06d30e"),
    ("Soft-knit weekend sweater", "Style", "A relaxed, breathable cotton blend with a soft hand and an easy, throw-on shape.", "64.00", 12, True, "photo-1576566588028-4147f3842f27"),
    ("The little book of slow living", "Books", "A thoughtful collection of small rituals and ideas for a more considered everyday.", "22.00", 31, False, "photo-1544947950-fa07a98d237f"),
    ("Citrus & cedar candle", "Home & Living", "Bright citrus opens into mellow cedarwood in a clean-burning, hand-poured soy candle.", "28.00", 5, True, "photo-1603006905003-be475563bc59"),
    ("Compact instant camera", "Technology", "A pocket-sized instant camera with automatic exposure for keeping the good bits tangible.", "74.00", 9, True, "photo-1516035069371-29a1b244cc32"),
    ("Canvas market tote", "Style", "A sturdy everyday carryall with reinforced handles and a roomy, unlined interior.", "26.00", 42, False, "photo-1590874103328-eac38a683ce7"),
    ("Ribbed glass water bottle", "Wellness", "A reusable borosilicate bottle with a grippy sleeve and an easy-clean wide mouth.", "24.00", 16, False, "photo-1602143407151-7111542de6e8"),
    ("Linen table runner", "Home & Living", "Washed natural linen brings an easy, lived-in feel to weeknight dinners and long lunches.", "42.00", 7, True, "photo-1600210492486-724fe5c67fb0"),
    ("Field notes journal set", "Books", "Three pocket-sized recycled-paper notebooks made for lists, sketches and stray ideas.", "18.00", 65, False, "photo-1455390582262-044cdead277a"),
    ("Foldable picnic blanket", "Outdoors", "A water-resistant base and soft woven top make this blanket an easy companion outdoors.", "48.00", 11, False, "photo-1524492412937-b28074a5d7da"),
    ("Everyday crossbody pouch", "Style", "A hands-free compact bag with a useful inner pocket and adjustable woven strap.", "39.00", 14, False, "photo-1548036328-c9fa89d128fa"),
    ("Mini bluetooth speaker", "Technology", "A small, splash-resistant speaker with balanced sound and up to twelve hours of play.", "52.00", 20, True, "photo-1608043152269-423dbba4e7e1"),
    ("Botanical hand cream duo", "Wellness", "Two pocket-friendly creams with shea butter and a light, fresh botanical scent.", "19.00", 33, False, "photo-1608248543803-ba4f8c70ae0b"),
    ("Sculptural stoneware vase", "Home & Living", "An artful, tactile silhouette in speckled stoneware, made for stems or a shelf of its own.", "46.00", 4, True, "photo-1578500494198-246f612d3b3d"),
    ("The curious cook cookbook", "Books", "Approachable recipes and kitchen notes for curious home cooks and happy improvisers.", "32.00", 22, False, "photo-1589998059171-988d887df646"),
    ("Soft sole house slides", "Style", "Cushioned, lightweight slides with a cotton terry lining for a comfortable home routine.", "34.00", 28, False, "photo-1543163521-1bf539c55dd2"),
    ("Stretch & restore yoga mat", "Wellness", "A supportive, grippy mat with comfortable cushioning and a simple carry strap.", "58.00", 13, True, "photo-1506629905607-d9f7d82c4f6e"),
    ("Pocket binoculars", "Outdoors", "Lightweight, compact binoculars bring birds, trails and far-off details a little closer.", "67.00", 8, False, "photo-1472396961693-142e6e269027"),
    ("Portable reading light", "Technology", "A rechargeable clip-on lamp with a soft amber setting for late chapters and early flights.", "29.00", 37, False, "photo-1507842217343-583bb7270b66"),
]


class Command(BaseCommand):
    help = "Create or refresh ShopEase sample categories and products."

    def handle(self, *args, **options):
        categories = {}
        for name, (slug, image_url) in CATEGORIES.items():
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "image_url": image_url, "description": f"Thoughtful finds for {name.lower()}."},
            )
            categories[name] = category
        for name, category_name, description, price, stock, featured, image_id in PRODUCTS:
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "category": categories[category_name],
                    "description": description,
                    "price": price,
                    "compare_at_price": None,
                    "stock": stock,
                    "is_featured": featured,
                    "image_url": f"https://images.unsplash.com/{image_id}?auto=format&fit=crop&w=900&q=85",
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(CATEGORIES)} categories and {len(PRODUCTS)} products."))