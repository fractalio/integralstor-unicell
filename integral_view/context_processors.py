
from integralstor import config


def get_version(request):
    version = None
    try:
        version, err = config.get_version()
        if err:
            raise Exception('Error retrieving version number')
    except Exception, e:
        return {'version': 'Unspecified version'}
    else:
        return {'version': version}

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
