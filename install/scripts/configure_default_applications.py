#!/usr/bin/python

import shutil, os
from datetime import datetime
from integralstor import config

def configure_default_applications(reconfigure=False):
    try:
        integralstor_root, err = config.get_platform_root()
        if err:
            raise Exception(err)
        app_json_file, err = config.get_applications_config_file_path()
        if err:
            raise Exception(err)
        if reconfigure and os.path.exists(app_json_file):
            d = datetime.now()
            shutil.move(app_json_file, "%s_%s" % (app_json_file,
                                                  d.strftime("%d%m%y%H%M")))
        if not os.path.exists(app_json_file):
            shutil.copy("%s/install/conf-files/others/applications.json" % integralstor_root,
                        app_json_file)
    except Exception, e:
        return None, "Error configuring default applications %s" % e
    else:
        return True

if __name__ == '__main__':
    print configure_default_applications(reconfigure=True)
