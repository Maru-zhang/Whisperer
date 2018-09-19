from setuptools import setup

setup(
    name='Whisperer',
    version='0.1.0',
    author='zhangbinhui',
    py_modules=['whisperer'], 
    install_requires=['Click', 'markdown2'],
    entry_points='''
        [console_scripts]
        wsp=whisperer:cli
    '''
)