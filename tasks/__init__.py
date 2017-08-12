from invoke import task, Collection


ns = Collection()


@task
def list(ctx):
    ctx.run('invoke --list')
ns.add_task(list)


@task
def buildApp(ctx):
    ctx.run('docker build -t redis_app_instance .')
ns.add_task(buildApp)
