import setuptools

with open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()

setuptools.setup(
    name='wyscoutapi',
    description='An extremely basic wrapper for the Wyscout data API',
    version='0.0.2',
    author='Ben Torvaney',
    author_email='torvaney@protonmail.com',
    url='https://github.com/Torvaney/wyscoutapi',
    license='GPLv3+',
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    packages=setuptools.find_packages(where='src'),
    package_dir={
        '': 'src',
    },
    install_requires=[
        'requests>=2.21.0',
        'ratelimiter>=1.2.0',
    ]
)
