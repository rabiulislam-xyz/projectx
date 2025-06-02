from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from projectx.utils import phone_regex # For phone validation test

User = get_user_model()


class TestUserViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users_list_url = reverse('users-list') # Renamed for clarity
        cls.token_url = reverse('token_obtain_pair')
        cls.token_refresh_url = reverse('token_refresh')

        cls.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )

        cls.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1password',
            phone='01777111111' # Added phone for update tests
        )

        cls.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2password'
        )
        # cls.existing_user can be replaced by user1 or user2 if its specific data isn't crucial for old tests.
        # For now, we have 3 users: admin, user1, user2.
        # The original baker.make user is also created, so total 4 users initially.

        # URL for detail view
        cls.user1_detail_url = reverse('users-detail', kwargs={'pk': cls.user1.id})
        cls.user2_detail_url = reverse('users-detail', kwargs={'pk': cls.user2.id})
        cls.me_url = reverse('users-me')


    def test_user_registration_with_all_valid_data(self):
        data = {
            "username": "testUser",
            "email": "testUser@google.yahoo",
            "password": "SuperSecrete",
            "first_name": "First",
            "last_name": "Last",
            "phone": "01777333777", # Valid phone based on regex
        }

        response = self.client.post(self.users_list_url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response_json.get('id'))
        self.assertEqual(response_json.get('username'), data['username'])
        self.assertEqual(response_json.get('email'), data['email'])
        self.assertEqual(response_json.get('phone'), data['phone'])

    def test_user_registration_with_existing_username(self):
        data = {
            "username": self.user1.username, # Using user1 for existing username
            "email": "new@user.com",
            "password": "SuperSecrete",
        }

        response = self.client.post(self.users_list_url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json['username'][0], 'A user with that username already exists.')

    # New tests for registration edge cases
    def test_user_registration_missing_username(self):
        data = {"email": "missingusername@example.com", "password": "password"}
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.json())

    def test_user_registration_missing_password(self):
        data = {"username": "missingpassword", "email": "missingpassword@example.com"}
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.json())

    def test_user_registration_missing_email(self):
        data = {"username": "missingemail", "password": "password"}
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())

    def test_user_registration_invalid_email(self):
        data = {"username": "invalidemailuser", "password": "password", "email": "invalid-email"}
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())

    def test_user_registration_existing_email(self):
        data = {
            "username": "anotheruser",
            "password": "password",
            "email": self.user1.email # Existing email
        }
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())
        self.assertEqual(response.json()['email'][0], 'user with this email address already exists.')


    def test_user_registration_invalid_phone(self):
        data = {
            "username": "invalidphoneuser",
            "password": "password",
            "email": "phone@example.com",
            "phone": "12345" # Invalid phone
        }
        response = self.client.post(self.users_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.json())
        # Assuming phone_regex validation error message is standard
        # self.assertEqual(response.json()['phone'][0], phone_regex.message) # This might be too specific

    def test_user_obtain_access_token(self):
        data = {
            "username": self.user1.username,
            "password": "user1password"} # Using user1 credentials

        response = self.client.post(self.token_url, data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response_json.get('access'))
        self.assertTrue(response_json.get('refresh'))

    def test_password_change(self): # This test updates password, which is part of user update
        # Original test seems to be testing if a user can change their own password
        # This is typically part of the "update own details" scenario
        # For unauthenticated:
        response = self.client.patch(self.user1_detail_url, {'password': 'newpassword'})
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # For authenticated:
        self.client.force_login(self.user1)
        response = self.client.patch(self.user1_detail_url, {'password': 'newpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify password change by trying to log in with the new password
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.check_password('newpassword'))

    # Tests for /users/me/ endpoint
    def test_get_own_details_me_endpoint(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)
        self.assertEqual(response.data['email'], self.user1.email)

    def test_get_own_details_me_endpoint_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    # Tests for Updating User Details (PATCH to /users/{id}/)
    def test_update_own_details(self):
        self.client.force_login(self.user1)
        update_data = {"first_name": "UpdatedFirst", "last_name": "UpdatedLast", "phone": "01999888777"}
        response = self.client.patch(self.user1_detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, update_data['first_name'])
        self.assertEqual(self.user1.last_name, update_data['last_name'])
        self.assertEqual(self.user1.phone, update_data['phone'])

    def test_update_other_user_details_forbidden(self):
        self.client.force_login(self.user1) # user1 logged in
        update_data = {"first_name": "AttemptUpdate"}
        response = self.client.patch(self.user2_detail_url, update_data) # attempts to update user2
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_other_user_details(self):
        self.client.force_login(self.admin_user) # admin logged in
        update_data = {"first_name": "AdminUpdatedFirst"}
        response = self.client.patch(self.user1_detail_url, update_data) # admin updates user1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, update_data['first_name'])

    # Test New Permission Handling
    # 5.1. List Users (GET to /users/)
    def test_list_users_as_non_admin_forbidden(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_as_admin_success(self): # Modified from test_get_all_users
        self.client.force_login(self.admin_user)
        response = self.client.get(self.users_list_url)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Count should be admin, user1, user2, and the baker.make one from original setUpTestData
        # If baker.make('account.User', ...) is still active and not removed.
        # User.objects.count() would be more robust here if initial setup is complex.
        self.assertEqual(response_json['count'], User.objects.count())


    def test_list_users_unauthenticated_forbidden(self):
        response = self.client.get(self.users_list_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    # Modifying test_access_users_with_token_authentication
    def test_list_users_as_admin_with_token_authentication(self): # Renamed and modified
        # Obtain token for admin user
        token_data = {"username": self.admin_user.username, "password": "adminpassword"}
        token_response = self.client.post(self.token_url, token_data)
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.json()['access']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], User.objects.count())


    # 5.2. Retrieve User (GET to /users/{id}/)
    def test_retrieve_own_details_success(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.user1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)

    def test_retrieve_other_user_details_as_non_admin_forbidden(self):
        self.client.force_login(self.user1) # user1 logged in
        response = self.client.get(self.user2_detail_url) # attempts to retrieve user2
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_other_user_details_as_admin_success(self):
        self.client.force_login(self.admin_user) # admin logged in
        response = self.client.get(self.user1_detail_url) # admin retrieves user1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)

    def test_retrieve_user_unauthenticated_forbidden(self):
        response = self.client.get(self.user1_detail_url) # Attempt to retrieve user1
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


    # Kept existing search test, ensure it uses an appropriate user
    # If search is admin-only, it should use admin_user. If available to all, user1 is fine.
    # Based on new permissions, listing (and thus search by extension) is admin-only.
    def test_search_users_as_admin(self): # Renamed and modified
        self.client.force_login(self.admin_user)
        # Assuming user1 has username 'user1'
        response = self.client.get(self.users_list_url + "?search=user1")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['count'], 1)
        self.assertEqual(response_json['results'][0]['username'], self.user1.username)

    def test_search_users_as_non_admin_forbidden(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.users_list_url + "?search=user2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
