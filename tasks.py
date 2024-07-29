from robocorp.tasks import task
from steps.extract import RobotOrderAutomation

@task
def minimal_task():
    robot = RobotOrderAutomation()
    robot.execute()