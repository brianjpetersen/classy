# standard libraries
pass
# third party libraries
pass
# first party libraries
import devploy

if __name__ == '__main__':
    host = '52.1.51.153'
    certificate_filename = '/Users/brianjpetersen/Desktop/podimetrics/secret/secret/certificates/aws/development.pem'
    instance = devploy.deploy.Instance(host, 'ubuntu', certificate_filename)
    #instance.upgrade(reboot=True)
    #instance.install_packages(['git', 'wget'])
    #instance.install_python()
    #instance.rethinkdb_install()
    #instance.pip_install('rethinkdb')
    #instance.pip_install('delorean')
    #instance.pip_install('webob')
    #instance.pip_install('waitress')
    #instance.run('mkdir ~/podimetric')
    #instance.mount_drive('/dev/xvdh', 'ext4', '~/podimetrics')
    #instance.change_permissions('777', '~/podimetrics')
    instance.cd('~/podimetrics')
    #instance.git_clone('https://github.com/brianjpetersen/classy.git')
    #instance.git_clone('https://github.com/brianjpetersen/tiny_id.git')
    instance.cd('tiny_id')
    #instance.pip_install()
    instance.cd('../')
