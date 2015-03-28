# standard libraries
pass
# third party libraries
pass
# first party libraries
import devploy
import secrets

if __name__ == '__main__':

    host = '52.4.65.216'
    certificate_filename = secrets.certificate_filenames.aws.development
    instance = devploy.deploy.Instance(host, 'ubuntu', certificate_filename, verbose=True)
    print
    print instance
    print
    print 20*'='
    instance.upgrade(reboot=True)
    instance.apt_get('wget')
    instance.install_anaconda_python()
    """
    instance.python_path = '/anaconda/bin'
    instance.pip_path = '/anaconda/bin'
    """
    instance.rethinkdb_install()
    instance.pip_install('rethinkdb')
    instance.pip_install('delorean')
    instance.pip_install('webob')
    instance.pip_install('waitress')
    instance.run('mkdir ~/podimetrics')
    instance.set_permissions('~/podimetrics')
    # xvdb for m3, xvdh for t2
    instance.mount_drive('/dev/xvdh', 'ext4', '~/podimetrics')
    instance.cd('~/podimetrics')
    instance.apt_get('git')
    instance.git_clone('https://github.com/brianjpetersen/classy.git')
    instance.git_clone('https://github.com/brianjpetersen/tiny_id.git')
    instance.cd('tiny_id')
    instance.pip_install()
    instance.cd('../')
    instance.cd('classy')
    instance.pip_install()
    instance.cd('tests')
    instance.run('mkdir data')
    instance.cd('data')
    log_file = '~/podimetrics/classy/tests/data/rethinkdb_data/rethinkdb.log'
    instance.spawn('rethinkdb --bind all --http-port 8081 --log-file {}'.format(log_file))
    instance.cd('../')
    instance.spawn_python('test_device_layer.py')