from taskmanager import TaskManager
from robocorp.tasks import task

@task
def execute_task():
  task_manager = TaskManager()
  task_manager.extract_news()
