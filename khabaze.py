import os
import sys
import shutil
import getopt
EXCLUDE = [ 'khabaze.py', 'Auto_fill.py','clean_osm.py','apps', '__pycache__', '.git' ]
DONT_COMPILE = [ 'anastacia', 'api', 'manage.py', 'resource_deamon.py' ]
errors = ''

def generate_folder (path, name):
    i=1
    while os.path.exists(path + name):
        if i > 1: name = name[:-1]
        name+=str(i)
        i=i+1
    else:
        EXCLUDE.append(name)
        return name

def ila_makhbaza(source_root, path, compiled_root, file_py, makhbaza_root):

    def get_v3_output ():

        for x in os.listdir('./'):
            if x.startswith(file_py[:-3]) and x.endswith('.so'):
                return x

    shutil.copyfile(source_root + path + file_py,source_root + makhbaza_root + file_py)
    cwd = os.getcwd()
    os.chdir(source_root + makhbaza_root)

    v = '3'
    if sys.version_info[0] < 3:
        v = '2'
    cmd = 'python{} khabze.py '.format(v) + file_py[:-3]+' build_ext --inplace'

    try:
        os.system(cmd)
        output = file_py[:-3] + '.so' if v  == '2' else get_v3_output()
        os.chdir(cwd)
        os.rename(source_root + makhbaza_root + output, compiled_root + path + file_py[:-3] + '.so')
    except Exception as e:
        #errors += 'error in ' + path + file_py + '\n'
        print ('Compilation Error {} '.format(e))
        os.chdir(cwd)
        os.rename(source_root + makhbaza_root + file_py,compiled_root + path + file_py)

def khabaze(source_root,path, compiled_root, makhbaza_root):


    for x in os.listdir(source_root + path):
        if x in EXCLUDE:
            print(str(x) + ' is excluded')
            continue
        if x in DONT_COMPILE:
            print(str(x) + ' kept in python source')
            if os.path.isdir(path + x): shutil.copytree(source_root + path + x, compiled_root + path + x)
            elif os.path.splitext(x)[1] == '.py': shutil.copyfile(source_root + path + x ,compiled_root + path + x)
            continue
        if os.path.isdir(source_root + path + x):
            os.mkdir(compiled_root + path + x)
            print(str(path) + str(x) + '/')
            khabaze( source_root, path + x + '/', compiled_root, makhbaza_root)
        elif x == '__init__.py' :shutil.copyfile(source_root +  path + x ,compiled_root + path + x)
        elif os.path.splitext(x)[1] == '.pyc': continue
        elif os.path.splitext(x)[1] == '.py': ila_makhbaza(source_root, path, compiled_root, x, makhbaza_root)
        else: shutil.copyfile(source_root + path + x ,compiled_root + path + x)

if __name__ == '__main__':

    args, _ = getopt.getopt(sys.argv[1:],'hs:m:c:e:d:',['help','source_root=','main=', 'compiled_root=','exclude=','dont_compile='])
    source_root = './'
    name = 'anastacia'
    for flag, arg in args:
        if flag in ('-h', '--help'): 
            print ('khabaze.py -s <source_root> -m <main_script> -c <compiled_root> -e <exclude> -d <dont_compile>')
            sys.exit()
        if flag in ('-s', '--source_root'): 
            if os.path.isdir(arg.split(',')[0]):
                source_root = arg.split(',')[0]
            else: raise Exception ('Invalid source root')
        if flag in ('-m', '--main'):
            if os.path.splitext(arg.split(',')[0])[1] == '.py':
                main= arg.split(',')[0]
            else: raise Exception ('Invalid main script file')
            DONT_COMPILE.append(main)
            name = os.path.splitext(name)[0]
        if flag in ('-c', '--compiled_root'):
            if os.path.isdir(arg.split(',')[0]):
                compiled_rootf = arg.split(',')[0]
        if flag in ('-e', '--exclude'): EXCLUDE += arg.split(',')
        if flag in ('-d', '--dont_compile'): DONT_COMPILE += arg.split(',')

    source_root += '/' if source_root[:-1] != '/' else ''
    """ Building makhbaza """
    makhbaza_root = generate_folder(source_root,'makhbaza')
    os.mkdir(source_root + makhbaza_root)
    with open(source_root + makhbaza_root + '/khabze.py', 'w') as f:
        data = """import sys
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules =[Extension(sys.argv[1], [sys.argv[1] + '.py']),]
sys.argv.remove(sys.argv[1])
setup(
    name ='""" + name + """',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)"""
        f.write(data)

    compiled_root = generate_folder(source_root,'compiled')
    os.mkdir(source_root + compiled_root)
    khabaze(source_root, '', source_root + compiled_root + '/', makhbaza_root + '/')
    shutil.rmtree(source_root + makhbaza_root)
    shutil.move(source_root+ compiled_root, os.path.abspath(compiled_rootf))

    print ('--------------- Report ---------------')
    print(errors)
