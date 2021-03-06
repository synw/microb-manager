Microb manager
==============

Admin interface for [Microb](https://github.com/synw/microb): edit pages in Django and mirror them into Rethinkdb to be
served with Microb. 

Install
-------

  ```bash
pip install django
django-admin startproject sites && cd sites
  ```

[Install and configure Django R](https://github.com/synw/django-R#install)

  ```bash
git clone https://github.com/synw/microb-manager.git
mv microb-manager/microb/ .
rm -rf microb-manager/
pip install pytz django-codemirror2 django-ckeditor django-reversion django-mptt Pillow jsonfield
  ```

Add to INSTALLED_APPS in Django settings.py:

  ```python
"mptt",
"reversion",
"ckeditor",
"ckeditor_uploader",
"codemirror2",
"microb",
  ```
Add the Ckeditor config to settings:

  ```python
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_JQUERY_URL = '/static/js/jquery-2.1.4.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar':  [
                    ["Format", "Styles", "Bold", "Italic", "Underline", '-', 'RemoveFormat'],
                    ['NumberedList', 'BulletedList', "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter','JustifyRight', 'JustifyBlock'],
                    ["Image", "Table", "Link", "Unlink", "Anchor", "SectionLink", "Subscript", "Superscript"], ['Undo', 'Redo'],
                    ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],["Source", "Maximize"],
                    ],
        "removePlugins": "stylesheetparser",
        'width': '1150px',
        'height': '450px',
    },
}
  ```
Microb settings:

  ```python
MICROB_CODE_MODE = True # to enable codemirror editor (otherwise it will be ckeditor)
  ```
Migrate:

  ```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
  ```

Go to `/admin/` and add a machine and a http server. 
Then you can create pages. Go to `/r/` to view the page data from Rethinkdb.

Note: you can synchronize the local database from the main db:

  ```bash
python manage.py microb_syncdb domain_name
  ```

Replace `domain_name` by the name of the server, corresponding to the name of the Rethinkdb database you want to sync

[Configure Microb](https://github.com/synw/microb#configuration):

  ```bash
mv microb/servers .
cd servers/localhost
vim microb_config.json # same values than in settings.py
# symlink to the images folder
cd static
ln -s ../../media/localhost/img/ img
  ```

Run the server: `./microb`


