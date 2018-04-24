from functools import partial

import click
from apscheduler.schedulers.background import BackgroundScheduler

from konsent import make_app, db, update_phases


@click.command()
@click.argument('action', type=click.Choice(['runserver', 'createdb']))
@click.option('-d', '--database-name', default='konsent',
              help='Database name')
@click.option('-H', '--database-host', default='127.0.0.1',
              help='Database host')
@click.option('-u', '--database-user', default='root',
              help='Database username')
@click.option('-p', '--database-password', default='',
              help='Database password')
def main(action,
         database_name,
         database_host,
         database_user,
         database_password):

    db_uri = 'mysql://{username}{sep}{password}@{host}/{database}'.format(
        host=database_host,
        username=database_user,
        sep=':' if len(database_password) else '',
        password=database_password,
        database=database_name
    )

    app = make_app(db_uri=db_uri)

    if action == 'runserver':
        # start the scheduler
        apsched = BackgroundScheduler()
        apsched.add_job(partial(update_phases, app), 'interval', seconds=30)
        apsched.start()
        # start the app
        app.run(debug=True)
    elif action == 'createdb':
        app.app_context().push()
        db.create_all()
