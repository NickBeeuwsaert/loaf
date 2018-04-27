from setuptools import setup, find_packages


setup(
    name='loaf',
    version='0.1',
    author='Nick Beeuwsaert',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(
        where='lib'
    ),
    package_dir={
        '': 'lib'
    },
    install_requires=[
        'urwid',
        'aiohttp'
    ],
    extras_require={
        'test': [],
        'dev': [
            'pycodestyle',
            'mypy'
        ]
    },
    entry_points={
        'console_scripts': [
            'loaf = loaf:main'
        ]
    }
)
