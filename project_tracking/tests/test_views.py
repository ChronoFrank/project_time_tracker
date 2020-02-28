import json
import time
from unittest.mock import patch
from mixer.backend.django import mixer
from project_tracking.models import Task, Project, User
from django.test import TestCase
from rest_framework.test import APITestCase


class JWTAuthViewsTesCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user("test", "test@mailinator.com", "super_secret")

    def test_invalid_login(self):
        response = self.client.post('/api/v1/access_token/', {"username": "test", "password": "super"})
        json_data = json.loads(response.content)
        self.assertEqual(400, response.status_code)
        self.assertEqual(json_data.get('non_field_errors')[0], u'No active account found with the given credentials')

    def test_generate_access_token(self):
        response = self.client.post('/api/v1/access_token/', {"username": "test", "password": "super_secret"})
        json_data = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertIn('access', json_data.keys())
        self.assertIn('refresh', json_data.keys())

    def test_refresh_access_token(self):
        response1 = self.client.post('/api/v1/access_token/', {"username": "test", "password": "super_secret"})
        json_data1 = json.loads(response1.content)
        response2 = self.client.post('/api/v1/refresh_token/', {"refresh": json_data1.get('refresh')})
        json_data2 = json.loads(response2.content)
        self.assertEqual(200, response2.status_code)
        self.assertIn('access', json_data2.keys())
        self.assertNotIn('refresh', json_data2.keys())


class UserReviewViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@mailinator.com", "super_secret")
        response = self.client.post('/api/v1/access_token/', {"username": "test", "password": "super_secret"})
        json_data = json.loads(response.content)
        self.access_token = json_data.get('access')
        self.project = mixer.blend(Project, user=self.user)

    def set_api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_user_method_not_allowed(self):
        """
        test try to do a request with a method not allowed to get and 405 error
        """
        self.set_api_authentication()
        response = self.client.delete('/api/v1/users/'.format(self.user.id), {"email": self.user.email})
        self.assertEqual(405, response.status_code)

    def test_get_single_user(self):
        """
        test to retrive a single user by id
        """
        task = mixer.blend(Task, project=self.project)
        self.set_api_authentication()
        response = self.client.get('/api/v1/users/{}/'.format(self.user.id))
        json_data = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, '"id":{}'.format(self.user.id))
        self.assertContains(response, '"username":"{}"'.format(self.user.username))
        self.assertEqual(self.user.username, json_data.get('username'))
        self.assertFalse('"password:"' in json_data)
        self.assertNotEqual([], json_data.get('project_set'))

    def test_get_all_users(self):
        """
        test to retrive all users
        """
        user_1 = User.objects.create_user("test1", "test1@earth.com", "super_secret")
        user_2 = User.objects.create_user("test2", "test2@earth.com", "super_secret")
        self.set_api_authentication()
        response = self.client.get('/api/v1/users/')
        json_data = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(json_data), 3)

    def test_get_user_projetcs_tasks_information(self):
        task1 = mixer.blend(Task, project=self.project)
        task1.close()
        task2 = mixer.blend(Task, project=self.project)
        task2.pause()
        self.set_api_authentication()
        response = self.client.get('/api/v1/users/{}/'.format(self.user.id))
        json_data = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertGreater(len(json_data.get('project_set')), 0)
        self.assertContains(response, "{0}".format(task1.name))
        self.assertContains(response, "{0}".format(task2.name))
        self.assertContains(response, "total_spend_time")


class ProjectViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user("test1", "test@mailinator.com", "super_secret")
        response = self.client.post('/api/v1/access_token/', {"username": "test1", "password": "super_secret"})
        json_data = json.loads(response.content)
        self.access_token = json_data.get('access')

    def set_api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_project_methods_not_allowed(self):
        self.set_api_authentication()
        response = self.client.delete('/api/v1/projects/')
        self.assertEqual(405, response.status_code)
        response = self.client.options('/api/v1/projects/')
        self.assertEqual(405, response.status_code)

    def test_create_project_without_user_auth(self):
        data = {
            "name": "test project"
        }
        response = self.client.post('/api/v1/projects/', json.dumps(data), content_type='application/json')
        self.assertEqual(401, response.status_code)

    def test_create_project_without_name(self):
        data = {}
        self.set_api_authentication()
        response = self.client.post('/api/v1/projects/', json.dumps(data), content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_create_project_with_user(self):
        data = {
            "name": "test project"
        }
        self.set_api_authentication()
        response = self.client.post('/api/v1/projects/', json.dumps(data), content_type='application/json')
        json_data = json.loads(response.content)
        self.assertEqual(201, response.status_code)

    def test_list_projects_for_user(self):
        project1 = mixer.blend(Project, user=self.user)
        self.set_api_authentication()
        response = self.client.get('/api/v1/projects/')
        json_data = json.loads(response.content)
        self.assertEqual(len(json_data), 1)
        self.assertIn("id", json_data[0])
        self.assertIn("name", json_data[0])
        self.assertIn("project_tasks", json_data[0])
        self.assertIn("total_spend_time", json_data[0])
        self.assertEqual(json_data[0].get('name'), project1.name)
        self.assertEqual(json_data[0].get('project_tasks'), [])


class TaskViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user("test2", "test@mailinator.com", "super_secret")
        response = self.client.post('/api/v1/access_token/', {"username": "test2", "password": "super_secret"})
        json_data = json.loads(response.content)
        self.access_token = json_data.get('access')
        self.project = mixer.blend(Project, user=self.user)

    def set_api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_task_method_not_allowed(self):
        self.set_api_authentication()
        response = self.client.delete('/api/v1/tasks/'.format(self.user.id), {"email": self.user.email})
        self.assertEqual(405, response.status_code)
