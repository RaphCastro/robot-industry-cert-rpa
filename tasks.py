from robocorp.tasks import task
from steps.extract import main

@task
def minimal_task():
    main()