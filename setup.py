from setuptools import setup
import os
from simplewebdavclient.simplewebdavclient import __version__

base_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

packages = [
    'simplewebdavclient'
]

install_requires = [
    'requests == 2.23.0',
]

tests_require = [
    'pytest',
]

setup(
    name='simplewebdavclient',
    version=__version__,
    python_requires='~=3.3',
    description='This is a library used to make WebDav Client Connections simple.',
    long_description=long_description,
    long_description_content_type='text/restructuredtext',
    keywords='webdav simple',
    url='https://simplewebdavclient.readthedocs.io',
    project_urls={
        'Documentation': 'https://simplewebdavclient.readthedocs.io/en/latest/',
        'Source': 'https://github.com/btr1975/simplewebdavclient',
        'Tracker': 'https://github.com/btr1975/simplewebdavclient/issues',
    },
    author='Benjamin P. Trachtenberg',
    author_email='e_ben_75-python@yahoo.com',
    license='MIT',
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    test_suite='pytest',
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
