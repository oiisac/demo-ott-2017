from invoke import task, Collection

from service.C import PACKAGE_VERSION, APP_NAME, REDIS_HOST, NETWORK, REDIS_CONT, APP_IMG, LOG_VOLUME, INST_NUMBER


service_collection = Collection('service')


@task
def start(ctx):
    """ Run service as multiple containers with names like app name"""
    try:
        ctx.run('docker volume create {name}'.format(name=LOG_VOLUME))
    except:
        pass
    for i in range(0, INST_NUMBER):
        ctx.run('''docker run -d --net={net} -v logs:/tmp/{app}/ \
                   --name={app}_{ver}_{i} \
                   {img}:latest \
                   sh -c "python service/main.py"'''.format(net=NETWORK, img=APP_IMG, app=APP_NAME,
                                                            ver=PACKAGE_VERSION, i=i))
service_collection.add_task(start)


@task
def stop(ctx):
    """ Stop and remove all containers with name like app name"""
    ctx.run("docker ps -a | grep {app} | tr -s ' ' | cut -d ' ' -f 1 | xargs docker rm -fv".format(app=APP_NAME))
service_collection.add_task(stop)


@task
def errors(ctx):
    """ Print all errors from DB"""
    ctx.run('''docker run --rm --net={net} -v logs:/tmp/{app}/\
               -e GET_ERRORS=True \
               {img}:latest \
               sh -c "python service/main.py"'''.format(net=NETWORK, img=APP_IMG))
service_collection.add_task(errors)


@task
def clean(ctx):
    """ Clean DB"""
    ctx.run('''docker run --rm --net={net} -v logs:/tmp/{app}/\
               -e CLEAN_DB=True \
               {img}:latest \
               sh -c "python service/main.py"'''.format(app=APP_NAME, net=NETWORK, img=APP_IMG))
service_collection.add_task(clean)


@task
def logs(ctx):
    """ Get all logs"""
    ctx.run('''docker run --rm -v logs:/tmp/{app}/\
               {img}:latest \
               sh -c "tail /tmp/{app}/*.log"'''.format(app=APP_NAME, img=APP_IMG))
service_collection.add_task(logs)
