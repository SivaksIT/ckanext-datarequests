import click
from ckan import model

def get_commands():
    @click.group()
    def datarequests():
        """Generates datarequest commands"""
        pass

    @datarequests.command()
    def initdb():
        from ckanext.datarequests.db import init_db
        init_db(model)

    return [datarequests]