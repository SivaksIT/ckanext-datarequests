import pytest
from sqlalchemy import inspect

from ckan import model

from ckanext.datarequests import db


@pytest.fixture
def datarequest_setup():
    db.init_db(model)
    engine = model.Session.get_bind()
    inspector = inspect(engine)
    print('::::::: fixture-start->', inspector.get_table_names())
    datarequests_table = Table('datarequests' ,model.meta)
    print(dir(db.DataRequest))
    
    yield 
    model.Session.close_all()
    model.meta.metadata.drop_all(bind=engine, tables=[datarequests_table,
                                db.comments_table, db.followers_table])
    print('::::::: fixture-end->',inspector.get_table_names())


    
    # if db.datarequests_table.exists():
    #     model.meta.metadata.drop_all(bind=engine,\
    #                  tables=[db.datarequests_table])
    # if db.comments_table.exists():
    #     model.meta.metadata.drop_all(bind=engine,\
    #                      tables=[db.comments_table])
    # if db.followers_table.exists():
    #     model.meta.metadata.drop_all(bind=engine,\
    #                      tables=[db.followers_table])