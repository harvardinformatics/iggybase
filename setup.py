from distutils.core import setup

setup(
    name='iggybase',
    version='',
    packages=['iggybase', 'iggybase.mod_auth', 'iggybase.mod_murray_lab', 'iggybase_env.lib.python3.4.site-packages.bn',
              'iggybase_env.lib.python3.4.site-packages.pbr', 'iggybase_env.lib.python3.4.site-packages.pbr.cmd',
              'iggybase_env.lib.python3.4.site-packages.pbr.hooks',
              'iggybase_env.lib.python3.4.site-packages.pbr.tests',
              'iggybase_env.lib.python3.4.site-packages.pbr.tests.testpackage.pbr_testpackage',
              'iggybase_env.lib.python3.4.site-packages.pip', 'iggybase_env.lib.python3.4.site-packages.pip.vcs',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.distlib',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.distlib._backport',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.colorama',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib.trie',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib.filters',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib.serializer',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib.treewalkers',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib.treeadapters',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.html5lib.treebuilders',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages.chardet',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages.urllib3',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages.urllib3.util',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages.urllib3.contrib',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages.urllib3.packages',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor.requests.packages.urllib3.packages.ssl_match_hostname',
              'iggybase_env.lib.python3.4.site-packages.pip._vendor._markerlib',
              'iggybase_env.lib.python3.4.site-packages.pip.commands',
              'iggybase_env.lib.python3.4.site-packages.pip.backwardcompat',
              'iggybase_env.lib.python3.4.site-packages.flask', 'iggybase_env.lib.python3.4.site-packages.flask.ext',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.lib.python2.5.site-packages.site_package',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.path.installed_package',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.flaskext',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.flaskext.oldext_package',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.moduleapp',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.moduleapp.apps',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.moduleapp.apps.admin',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.moduleapp.apps.frontend',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.blueprintapp',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.blueprintapp.apps',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.blueprintapp.apps.admin',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.blueprintapp.apps.frontend',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.flask_broken',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.config_package_app',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.subdomaintestmodule',
              'iggybase_env.lib.python3.4.site-packages.flask.testsuite.test_apps.flask_newext_package',
              'iggybase_env.lib.python3.4.site-packages.mysql',
              'iggybase_env.lib.python3.4.site-packages.mysql.connector',
              'iggybase_env.lib.python3.4.site-packages.mysql.connector.django',
              'iggybase_env.lib.python3.4.site-packages.mysql.connector.fabric',
              'iggybase_env.lib.python3.4.site-packages.mysql.connector.locales',
              'iggybase_env.lib.python3.4.site-packages.mysql.connector.locales.eng',
              'iggybase_env.lib.python3.4.site-packages.jinja2',
              'iggybase_env.lib.python3.4.site-packages.jinja2.testsuite',
              'iggybase_env.lib.python3.4.site-packages.jinja2.testsuite.res',
              'iggybase_env.lib.python3.4.site-packages.blinker', 'iggybase_env.lib.python3.4.site-packages.wtforms',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.csrf',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.i18n',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.django',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.django.templatetags',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.dateutil',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.appengine',
              'iggybase_env.lib.python3.4.site-packages.wtforms.ext.sqlalchemy',
              'iggybase_env.lib.python3.4.site-packages.wtforms.csrf',
              'iggybase_env.lib.python3.4.site-packages.wtforms.fields',
              'iggybase_env.lib.python3.4.site-packages.wtforms.widgets',
              'iggybase_env.lib.python3.4.site-packages.dominate', 'iggybase_env.lib.python3.4.site-packages.mod_wsgi',
              'iggybase_env.lib.python3.4.site-packages.mod_wsgi.docs',
              'iggybase_env.lib.python3.4.site-packages.mod_wsgi.images',
              'iggybase_env.lib.python3.4.site-packages.mod_wsgi.server',
              'iggybase_env.lib.python3.4.site-packages.mod_wsgi.server.management',
              'iggybase_env.lib.python3.4.site-packages.mod_wsgi.server.management.commands',
              'iggybase_env.lib.python3.4.site-packages.werkzeug',
              'iggybase_env.lib.python3.4.site-packages.werkzeug.debug',
              'iggybase_env.lib.python3.4.site-packages.werkzeug.contrib',
              'iggybase_env.lib.python3.4.site-packages.flask_wtf',
              'iggybase_env.lib.python3.4.site-packages.flask_wtf.recaptcha',
              'iggybase_env.lib.python3.4.site-packages.stevedore',
              'iggybase_env.lib.python3.4.site-packages.stevedore.tests',
              'iggybase_env.lib.python3.4.site-packages.stevedore.example',
              'iggybase_env.lib.python3.4.site-packages._markerlib',
              'iggybase_env.lib.python3.4.site-packages.markupsafe',
              'iggybase_env.lib.python3.4.site-packages.setuptools',
              'iggybase_env.lib.python3.4.site-packages.setuptools.tests',
              'iggybase_env.lib.python3.4.site-packages.setuptools.command',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.ext',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.ext.declarative',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.orm',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.sql',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.util',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.event',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.engine',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.testing',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.testing.suite',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.testing.plugin',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.mssql',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.mysql',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.oracle',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.sqlite',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.sybase',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.firebird',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.dialects.postgresql',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.databases',
              'iggybase_env.lib.python3.4.site-packages.sqlalchemy.connectors',
              'iggybase_env.lib.python3.4.site-packages.flask_bootstrap',
              'iggybase_env.lib.python3.4.site-packages.flask_sqlalchemy',
              'iggybase_env.lib.python3.4.site-packages.virtualenv_support'],
    url='',
    license='',
    author='Marc Breneiser',
    author_email='mbreneiser@g.harvard.edu',
    description=''
)
