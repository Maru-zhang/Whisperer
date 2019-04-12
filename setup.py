from setuptools import setup

setup(
    name='Whisperer',
    version='0.2.0',
    author='zhangbinhui',
    py_modules=['whisperer'], 
    install_requires=['Click', 'markdown2', 'python-gitlab'],
    entry_points='''
        [console_scripts]
        wsp=whisperer:cli
    '''
)