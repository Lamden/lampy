from setuptools import setup, find_packages

requirements = [
    'requests',
    'PyNaCl'
]

setup(
    name='lamdenpy',
    version='0.1.2',
    url='https://github.com/Lamden/lampy',
    license='Creative Commons Non-Commercial',
    author='Lamden',
    author_email='team@lamden.io',
    description='Python driver for the Lamden blockchain. Everything you need to integrate smart contracts with standard applications.',
    packages=find_packages(),
    install_requires=requirements,
)
