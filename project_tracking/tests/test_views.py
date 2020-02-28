import json
import time
from datetime import datetime
from mixer.backend.django import mixer
from project_tracking.models import Task, Project, User
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

    def test_list_user_tasks_without_tasks(self):
        self.set_api_authentication()
        task_response = self.client.get('/api/v1/tasks/')
        json_data = json.loads(task_response.content)
        self.assertEqual(200, task_response.status_code)
        self.assertEqual(len(json_data), 0)

    def test_list_user_tasks(self):
        self.set_api_authentication()
        task = mixer.blend(Task, project=self.project)
        task_response = self.client.get('/api/v1/tasks/')
        json_data = json.loads(task_response.content)
        self.assertEqual(200, task_response.status_code)
        self.assertEqual(len(json_data), 1)
        self.assertIn("id", json_data[0])
        self.assertIn("name", json_data[0])
        self.assertIn("started_at", json_data[0])
        self.assertIn("ended_at", json_data[0])
        self.assertIn("spend_time", json_data[0])
        self.assertIn("is_closed", json_data[0])
        self.assertEquals(json_data[0].get('is_closed'), False)

    def test_create_new_task(self):
        data = {
            "project_id": self.project.id,
            "name": "test new task"
        }
        self.set_api_authentication()
        response = self.client.post('/api/v1/tasks/', json.dumps(data), content_type='application/json')
        json_data = json.loads(response.content)
        self.assertEqual(201, response.status_code)

    def test_create_task_without_project_or_invalid_project(self):
        data = {
            "name": "test new task"
        }
        self.set_api_authentication()
        response = self.client.post('/api/v1/tasks/', json.dumps(data), content_type='application/json')
        json_data = json.loads(response.content)
        self.assertEqual(400, response.status_code)
        json_data = json.loads(response.content)
        self.assertIn("error", json_data)
        self.assertIn("You must provide a project", json_data.get('error'))
        data.update({"project_id": 11212})
        response2 = self.client.post('/api/v1/tasks/', json.dumps(data), content_type='application/json')
        self.assertEqual(400, response2.status_code)

    def test_create_new_task_when_other_task_is_running(self):
        data = {
            "project_id": self.project.id,
            "name": "test new task"
        }
        self.set_api_authentication()
        task = mixer.blend(Task, project=self.project)
        response = self.client.post('/api/v1/tasks/', json.dumps(data), content_type='application/json')
        json_data = json.loads(response.content)
        self.assertEqual(403, response.status_code)
        self.assertIn("error", json_data)
        self.assertIn("there are tasks running,", json_data.get('error'))

    def test_pause_resume_task(self):
        data_task = { "project_id": self.project.id, "name": "test new task" }
        self.set_api_authentication()
        response1 = self.client.post('/api/v1/tasks/', json.dumps(data_task), content_type='application/json')
        task_data = json.loads(response1.content)
        self.assertEqual(201, response1.status_code)
        time.sleep(3)
        new_task_id = task_data.get('id')
        response2 = self.client.put('/api/v1/tasks/pause_resume/{0}/'.format(new_task_id))
        updated_task_data = json.loads(response2.content)
        self.assertEquals(updated_task_data.get('is_paused'), True)
        response3 = self.client.put('/api/v1/tasks/pause_resume/{0}/'.format(new_task_id))
        updated_task_data2 = json.loads(response3.content)
        self.assertEquals(updated_task_data2.get('is_paused'), False)

    def test_close_task(self):
        data_task = { "project_id": self.project.id, "name": "test new task" }
        self.set_api_authentication()
        response1 = self.client.post('/api/v1/tasks/', json.dumps(data_task), content_type='application/json')
        task_data = json.loads(response1.content)
        self.assertEqual(201, response1.status_code)
        time.sleep(3)
        new_task_id = task_data.get('id')
        response2 = self.client.put('/api/v1/tasks/close/{0}/'.format(new_task_id))
        updated_task_data = json.loads(response2.content)
        self.assertEquals(updated_task_data.get('is_closed'), True)
        response3 = self.client.put('/api/v1/tasks/close/{0}/'.format(new_task_id))
        self.assertEqual(400, response3.status_code)
        updated_task_data2 = json.loads(response3.content)
        self.assertIn("error", updated_task_data2)
        self.assertEquals("Task already closed", updated_task_data2.get('error'))

    def test_restart_task(self):
        data_task = {"project_id": self.project.id, "name": "test new task"}
        self.set_api_authentication()
        response1 = self.client.post('/api/v1/tasks/', json.dumps(data_task), content_type='application/json')
        task_data = json.loads(response1.content)
        self.assertEqual(201, response1.status_code)
        time.sleep(3)
        new_task_id = task_data.get('id')
        first_started_at_datetime = datetime.strptime(task_data.get('started_at').split(".")[0], '%Y-%m-%dT%H:%M:%S')
        response2 = self.client.put('/api/v1/tasks/restart/{0}/'.format(new_task_id))
        updated_task_data = json.loads(response2.content)
        reset_started_at_datetime = datetime.strptime(updated_task_data.get('started_at').split(".")[0], '%Y-%m-%dT%H:%M:%S')
        self.assertGreater(reset_started_at_datetime, first_started_at_datetime)

    def test_restart_task_with_no_id_or_incorrect_id(self):
        self.set_api_authentication()
        response = self.client.put('/api/v1/tasks/restart/5555/')
        self.assertEqual(404, response.status_code)
        json_data = json.loads(response.content)
        self.assertIn("detail", json_data)

    def test_continue_task(self):
        data_task = {"project_id": self.project.id, "name": "test new task"}
        self.set_api_authentication()
        response1 = self.client.post('/api/v1/tasks/', json.dumps(data_task), content_type='application/json')
        task_data = json.loads(response1.content)
        self.assertEqual(201, response1.status_code)
        time.sleep(3)
        new_task_id = task_data.get('id')
        response2 = self.client.put('/api/v1/tasks/close/{0}/'.format(new_task_id))
        updated_task_data = json.loads(response2.content)
        self.assertEquals(updated_task_data.get('is_closed'), True)
        response3 = self.client.post('/api/v1/tasks/continue/', json.dumps({"id": new_task_id}),
                                     content_type='application/json')
        self.assertEqual(201, response3.status_code)
        task_continue_data = json.loads(response3.content)
        continue_task_id = task_continue_data.get('id')
        self.assertNotEqual(new_task_id, continue_task_id)

    def test_continue_task_with_no_id_or_incorrect_id(self):
        self.set_api_authentication()
        response = self.client.post('/api/v1/tasks/continue/', json.dumps({"id": 1121}),
                                     content_type='application/json')
        self.assertNotEqual(201, response.status_code)
        json_data = json.loads(response.content)
        self.assertIn("error", json_data)