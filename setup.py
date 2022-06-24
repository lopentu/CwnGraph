from setuptools import setup, find_packages

setup(
    name='CwnGraph',
    version='0.5.0-dev1',
    packages=find_packages(),
    license='GPL GNUv3',
    author="NTUGIL LOPE Lab",   
    setup_requires=["wheel"],
    install_requires=["gdown>=4.4.0", "requests", "nltk"],
    description="A CWN Python binding with graph structure",
    long_description="A CWN Python binding with graph structure"
)
