import os

from fabric.api import env, run

DEPLOYMENTS = {
    'prod': {
        'host_string': 'ubuntu@f2dhis2.ona.io',
        'key_filename': os.path.expanduser('~/.ssh/ona.pem'),
        'project_env': '/home/ubuntu/.virtualenvs/f2dhis2',
        'cwd': '/home/ubuntu/src/f2dhis2'
    },
}


def run_in_virtualenv(command):
    d = {
        'activate': os.path.join(env.project_env, 'bin', 'activate'),
        'command': command,
    }
    run('source %(activate)s && %(command)s' % d)


def deploy(deployment='prod', branch='master'):
    env.update(DEPLOYMENTS[deployment])
    run("git fetch origin")
    run("git checkout origin/%s" % branch)
    run_in_virtualenv("pip install -r requirements.pip")
    run_in_virtualenv("python manage.py syncdb")
    run_in_virtualenv("python manage.py migrate")
    run_in_virtualenv("python manage.py collectstatic --noinput")
    run("sudo /etc/init.d/celeryd-f2dhis2 restart")
    run("sudo uwsgi --reload /var/run/f2dhis2.pid")
