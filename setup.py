from setuptools import setup, find_packages

setup(
    name='CwnGraph',
    version='0.1.3',
    packages=find_packages(),
    license='GPL GNUv3',
    author="NTUGIL LOPE Lab",   
    setup_requires=["wheel"],
    install_requires=["gdown"],
    description="A CWN Python binding with graph structure",
    long_description="A CWN Python binding with graph structure"
)
