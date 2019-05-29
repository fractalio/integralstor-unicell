import os, json, shutil, sqlite3
from datetime import datetime
from integralstor import config

def configure_storage_insights(recreate_db=False):
    try:
        istor_root = "/opt/integralstor/integralstor"
        app_dir = "%s/integral_view/applications" % istor_root
        site_dir = "%s/site-packages/integralstor/applications" % istor_root
        db_dir = "%s/storage_insights/db" % app_dir
        storage_insights_dict = { "name": "Storage Insights",
                           "use_launch_url_prefix": False,
                            "use_default_launch_url_path": True,
                            "provider_url": "https://fractalio.com",
                            "provider_name": "Fractalio Data" }
        app_json_file, err = config.get_applications_config_file_path()
        if err:
            raise Exception(err)

        with open(app_json_file) as f:
            app_data = json.load(f)

        app_data["storage_insights"] = storage_insights_dict

        with open(app_json_file, 'w') as f:
            json.dump(app_data, f, indent = 4)

        if not os.path.exists("%s/storage_insights" % site_dir):
            os.symlink("%s/storage_insights/site-packages/storage_insights" % app_dir,
                       "%s/storage_insights" % site_dir)

        if recreate_db and os.path.exists("%s/storage_insights.db" % db_dir):
            d = datetime.now()
            shutil.move("%s/storage_insights.db" % db_dir,
                        "%s/storage_insights.db_%s" % (db_dir, d.strftime("%d%m%y%H%M")))

        if not os.path.exists("%s/storage_insights.db" % db_dir):
                db_connection = sqlite3.connect("%s/storage_insights.db" % db_dir)
                cursor = db_connection.cursor()
                with open("%s/storage_insights.schema" % db_dir, 'r') as f:
                    cursor.executescript(f.read())

    except Exception, e:
        return None, "Error while configuring storage insights: %s" % e
    else:
        return True

if __name__ == '__main__':
    print configure_storage_insights(recreate_db=True)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
