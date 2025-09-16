from django.core.management.base import BaseCommand

# from django.contrib.auth.models import User # Import the User model built in Django user model
from tenant_db.models import User, Product, Order, OrderItem


class Command(BaseCommand):
    help = "Populate the database with initial data"

    def handle(self, *args, **kwargs):

        user = User.objects.filter(username="admin").exists()
        # Create a superuser
        if not user:
            User.objects.create_superuser(
                username="admin", email="etsayhaben@gmial.com", password="admin123"
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created superuser 'admin'")
            )
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists"))
        self.stdout.write("🚀 Starting product creation...")
        # Create sample products
        products = [
            {
                "name": "Laptop",
                "description": "A high-performance laptop",
                "price": 999.99,
                "stock": 10,
            },
            {
                "name": "Smartphone",
                "description": "A latest model smartphone",
                "price": 699.99,
                "stock": 25,
            },
            {
                "name": "Headphones",
                "description": "Noise-cancelling headphones",
                "price": 199.99,
                "stock": 15,
            },
        ]
        for prod in products:
            product, created = Product.objects.get_or_create(
                name=prod["name"], defaults=prod
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created product: {product.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Product already exists: {product.name}")
                )
        # Create a sample order for the superuser
        admin_user = User.objects.get(username="admin")
        if not Order.objects.filter(user=admin_user).exists():
            order = Order.objects.create(
                user=admin_user, status=Order.OrderStatus.PENDING
            )
            # Add products to the order
            for product in Product.objects.all():
                OrderItem.objects.create(order=order, product=product, quantity=1)
            self.stdout.write(
                self.style.SUCCESS(f"Created order {order.order_id} for user 'admin'")
            )
        else:
            self.stdout.write(
                self.style.WARNING("Order for user 'admin' already exists")
            )
