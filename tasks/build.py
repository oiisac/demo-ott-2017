from invoke import task, Collection

from service.C import PACKAGE_VERSION, APP_NAME, REDIS_HOST, NETWORK, REDIS_CONT, APP_IMG, LOG_VOLUME


build_collection = Collection('build')


@task
def app(ctx):
    ctx.run('find . -name \'*.pyc\' -delete')
    ctx.run('docker build -t {img}:{ver} .'.format(img=APP_IMG, ver=PACKAGE_VERSION))
    ctx.run('docker tag {img}:{ver} {img}:latest'.format(img=APP_IMG, ver=PACKAGE_VERSION))
build_collection.add_task(app)


@task
def network(ctx, container):
    try:
        ctx.run('docker network create {net}'.format(net=NETWORK))
    except:
        pass
    ctx.run('docker network connect {net} {container}'.format(net=NETWORK, container=container))
build_collection.add_task(network)


@task
def redis(ctx):
    redis_docker_host = 'redis_db' if REDIS_CONT == 'localhost' else REDIS_CONT
    try:
        ctx.run('docker rm -fv {redis}'.format(redis=redis_docker_host))
    except:
        pass
    ctx.run('docker run -p 6379:6379 --name {redis} -d redis:alpine'.format(redis=redis_docker_host))
    network(ctx, redis_docker_host)
build_collection.add_task(redis)
