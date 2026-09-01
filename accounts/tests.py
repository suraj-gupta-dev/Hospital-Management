from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User



class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')
    
    def test_user_registration_success(self):
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
    
    def test_user_registration_password_mismatch(self):
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class ChangePasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.urls = reverse("change-password")
        self.user = User.objects.create_user(
            email="test@gmail.com",
            first_name="test",
            last_name="user",
            password="oldpass@123"
        )

    def test_change_password_success(self):
        """Test successful password change"""
        self.client.force_authenticate(user=self.user)

        data = {
            "old_password": "oldpass@123",
            "new_password": "newpass@123",
            "confirm_new_password": "newpass@123"
        }

        response = self.client.post(self.urls, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")

        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass@123"))

    def test_change_password_unauthenticated(self):
        """Test without authenticated"""
        self.client.force_authenticate(user=None)

        data = {
            "old_password": "oldpass@123",
            "new_password": "newpass@123",
            "confirm_new_password": "newpass@123"
        }

        response = self.client.post(self.urls, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
