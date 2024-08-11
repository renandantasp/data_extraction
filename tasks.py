from robocorp.tasks import task
from taskmanager import TaskManager

@task
def execute_task():
  task_manager = TaskManager()
  task_manager.extract_news()
