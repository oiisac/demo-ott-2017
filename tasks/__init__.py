from invoke import task, Collection

from tasks.build import build_collection
from tasks.service import service_collection


ns = Collection()
ns.add_collection(build_collection)
ns.add_collection(service_collection)


@task
def list(ctx):
    ctx.run('invoke --list')
ns.add_task(list)
