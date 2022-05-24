""" our dev tasks """
import sys

from invoke import Collection, Program, task

from server import VERSION

PROJECT_NAME = 'server'


@task
def lint(ctx):
    """ run axblack and pylint """
    ctx.run(f'isort src/{PROJECT_NAME}', pty=True)
    ctx.run(f'black src/{PROJECT_NAME} src/tests', pty=True)
    ctx.run(f'pylint src/{PROJECT_NAME}', pty=True)


@task
def test(ctx):
    """ run our tests """
    ctx.run(
        f'py.test --cov {PROJECT_NAME} --cov-report term-missing src/tests',
        pty=True,
    )


@task
def run(ctx, debug=False):
    """ run dev server """
    ctx.run(
        f'python3 -m {PROJECT_NAME}.main {"--debug" if debug else ""}',
        pty=True,
    )


ns = Collection.from_module(sys.modules[__name__])
program = Program(namespace=ns, version=VERSION)
