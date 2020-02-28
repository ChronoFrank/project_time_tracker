import time
from django.test import TestCase
from mixer.backend.django import mixer
from project_tracking.models import Task, Project, User


class ProjectTestCase(TestCase):

    def setUp(self) -> None:
        self.user = mixer.blend(User, username='test')
        self.project = mixer.blend(Project, user=self.user)

    def test_str_function(self):
        self.assertEqual(str(self.project), self.project.name)

    def test_project_tasks_property_when_there_is_no_tasks(self):
        self.assertEqual([], self.project.project_tasks)

    def test_project_tasks_property_when_project_has_tasks(self):
        task = mixer.blend(Task, project=self.project, )
        self.assertNotEqual([], self.project.project_tasks)
        self.assertEqual(len(self.project.project_tasks), 1)
        self.assertIn('spend_time', str(self.project.project_tasks))
        self.assertIn('name', str(self.project.project_tasks))

    def test_project_total_spend_time_property_when_there_is_no_tasks(self):
        self.assertEqual('0 hrs 0 mins 0 secs', self.project.total_spend_time)

    def test_project_total_spend_time_property_when_project_has_tasks(self):
        task = mixer.blend(Task, project=self.project)
        self.assertNotEqual('0 hrs 0 mins 0 secs', self.project.total_spend_time)


class TaskTestCase(TestCase):
    def setUp(self) -> None:
        self.user = mixer.blend(User, username='test')
        self.project = mixer.blend(Project, user=self.user)
        self.task = mixer.blend(Task, project=self.project)

    def test_str_function(self):
        self.assertEqual(str(self.task), '{0}-{1}'.format(self.task.name, self.task.project))

    def test_task_spend_time_property_when_task_started(self):
        self.assertNotEqual('0 hrs 0 mins 0 secs', self.task.spend_time)

    def test_tasks_get_total_task_seconds_method(self):
        self.assertIsInstance(self.task.get_total_task_seconds(), int)
        self.assertGreater(self.task.get_total_task_seconds(), 0)

    def test_tasks_is_paused_property(self):
        self.task.pause()
        self.assertEqual(self.task.is_paused, True)

    def test_task_toggle_paused_method(self):
        self.task.toggle_paused()
        self.assertEqual(self.task.is_paused, True)
        self.task.toggle_paused()
        self.assertEqual(self.task.is_paused, False)

    def test_task_unpause_method(self):
        self.task.pause()
        time.sleep(2)
        self.assertIsNotNone(self.task.paused_at)
        self.task.unpause()
        self.assertEqual(self.task.is_paused, False)
        self.assertGreater(self.task.seconds_paused, 0)

    def test_task_close_method(self):
        self.task.close()
        self.assertIsNone(self.task.paused_at)
        self.assertIsNotNone(self.task.ended_at)

    def test_task_restart_method(self):
        self.task.restart()
        self.assertIsNone(self.task.ended_at)
        self.assertIsNone(self.task.paused_at)
        self.assertEqual(self.task.seconds_paused, 0)
        self.assertIsNotNone(self.task.started_at)
