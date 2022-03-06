from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class TestUserViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users_url = reverse('users-list')
        cls.token_url = reverse('token_obtain_pair')
        cls.token_refresh_url = reverse('token_refresh')

        cls.existing_user = User.objects.create_user(
            username='existing',
            email='existing@user.com',
            password='existing_password')

        baker.make('account.User',
                   username='darkLord',
                   email='darkLord@voldy.com')

    def test_user_registration_with_all_valid_data(self):
        data = {
            "username": "testUser",
            "email": "testUser@google.yahoo",
            "password": "SuperSecrete",
            "first_name": "First",
            "last_name": "Last",
            "phone": "01777333777",
        }

        response = self.client.post(self.users_url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response_json.get('id'))
        self.assertEqual(response_json.get('username'), data['username'])
        self.assertEqual(response_json.get('email'), data['email'])
        self.assertEqual(response_json.get('phone'), data['phone'])

    def test_user_registration_with_existing_username(self):
        data = {
            "username": self.existing_user.username,
            "email": "new@user.com",
            "password": "SuperSecrete",
        }

        response = self.client.post(self.users_url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json['username'][0], 'A user with that username already exists.')

    def test_user_obtain_access_token(self):
        data = {
            "username": "existing",
            "password": "existing_password"}

        response = self.client.post(self.token_url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response_json.get('access'))
        self.assertTrue(response_json.get('refresh'))

    def test_password_change(self):
        url = self.users_url + str(self.existing_user.id) + '/'
        response = self.client.patch(url, {'password': 'halum'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(self.existing_user)
        response = self.client.patch(url, {'password': 'halum'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_users_with_token_authentication(self):
        data = {"username": "existing", "password": "existing_password"}
        response = self.client.post(self.token_url, data)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.json()['access'])
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_users(self):
        self.client.force_login(self.existing_user)
        response = self.client.get(self.users_url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['count'], 2)

    def test_search_users(self):
        self.client.force_login(self.existing_user)
        response = self.client.get(self.users_url + "?search=existing")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['count'], 1)
        self.assertEqual(response_json['results'][0]['username'], self.existing_user.username)
