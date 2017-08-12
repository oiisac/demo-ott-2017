from invoke import task, Collection
from app import PACKAGE_VERSION, APP_NAME

ns = Collection()

NETWORK = APP_NAME + '_network'
REDIS_CONT = APP_NAME + '_redis_db'
APP_IMG = '{app}_instance_{ver}'.format(app=APP_NAME, ver=PACKAGE_VERSION)


@task
def list(ctx):
    ctx.run('invoke --list')
ns.add_task(list)


@task
def buildApp(ctx):
    ctx.run('docker build -t {img} .'.format(img=APP_IMG))
ns.add_task(buildApp)


@task
def redis(ctx):
    ctx.run('docker run --name {redis} -d redis:alpine'.format(redis=REDIS_CONT))
    networkConnect(ctx, REDIS_CONT)
ns.add_task(redis)


@task
def networkConnect(ctx, container):
    try:
        ctx.run('docker network create {net}'.format(net=NETWORK))
    except:
        pass
    else:
        ctx.run('docker network connect {net} {container}'.format(net=NETWORK, container=container))
ns.add_task(networkConnect)
