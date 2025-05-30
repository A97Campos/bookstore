import json
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth.models import User  # Adicione esta importação

from order.factories import OrderFactory, UserFactory
from product.factories import CategoryFactory, ProductFactory
from order.models import Order

class TestOrderViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.category = CategoryFactory(title="technology")
        self.product = ProductFactory(
            title="mouse", 
            price=100, 
            category=[self.category]
        )
        self.order = OrderFactory(product=[self.product], user=self.user)

    def test_order(self):
        response = self.client.get(
            reverse("order-list", kwargs={"version": "v1"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order_data = json.loads(response.content)
        self.assertEqual(
            order_data["results"][0]["product"][0]["title"], self.product.title
        )
        self.assertEqual(
            order_data["results"][0]["product"][0]["price"], self.product.price
        )
        self.assertEqual(
            order_data["results"][0]["product"][0]["active"], self.product.active
        )
        self.assertEqual(
            order_data["results"][0]["product"][0]["category"][0]["title"],
            self.category.title,
        )

    def test_create_order(self):
        product = ProductFactory()
        data = json.dumps({
            "products_id": [product.id],
            "user": self.user.id
        })

        response = self.client.post(
            reverse("order-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        created_orders = Order.objects.filter(user=self.user)
        self.assertTrue(created_orders.exists())
        
        latest_order = created_orders.latest('id')
        self.assertEqual(latest_order.product.first().id, product.id)