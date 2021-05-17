from setuptools import setup

VERSION = '1.0.1'

setup(
    name='tableau_accessibility_fixer',
    version=VERSION,
    py_modules=['tabfix'],
    url='https://github.com/scottbw/tableau-accessibility',
    download_url='https://github.com/scottbw/tableau-accessibility/tarball/{}'.format(VERSION),
    license='MIT',
    author='Scott Wilson',
    author_email='scott.bradley.wilson@gmail.com',
    description='A command-line tool for improving Tableau accessibility',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['lxml==4.6.2', 'pyyaml==5.4.1'],
    entry_points={
        'console_scripts': ['tabfix=tabfix:main'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7'
    ]
)
