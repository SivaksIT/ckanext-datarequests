import factory

from ckan import model
from ckan.tests import helpers

from ckanext.datarequests import db
from ckanext.datarequests import constants


class Datarequests(factory.Factory):
    class Meta:
        model = db.DataRequest
        abstract = False

    
    title  = factory.Sequence(lambda n: 'Test Datarequest [{n}]'.format(n=n))
    description = 'Some description'

    @classmethod
    def _build(cls, target_class, *args, **kwargs):
        raise NotImplementedError(".build() isn't supported in CKAN")

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        if args:
            assert False, "Positional args aren't supported, use keyword args."
    
        
        # datarequests is so badly behaved I'm doing this for now
        data_dict = dict(**kwargs)
        user = model.User.get(data_dict['user']['id'])
        context = {}
        context['auth_user_obj'] = user
        print(';;;;;;;------------>', data_dict['user']['id'])
        print('::::----> data_dict', data_dict)
        data_dict.pop('user', None)
        print(data_dict)

        

        datarequest = helpers.call_action(constants.CREATE_DATAREQUEST,
                                         context=context,
                                         **data_dict)
        return datarequest