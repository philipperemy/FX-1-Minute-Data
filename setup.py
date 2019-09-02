from setuptools import setup

setup(
    name='histdata',
    version='1.0',
    description='Download FX/commodities data (M1, Tick) from histdata.com.',
    author='Philippe Remy',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    packages=['histdata'],
    install_requires=['requests', 'beautifulsoup4']
)
