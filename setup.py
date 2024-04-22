"""Setup for the ScholarQuest package."""
from setuptools import setup

setup(
    name='ScholarQuest',
    version='0.0.1',
    description="""Package to get top institutions and\
    top professors/authors in the world or a specified country.""",
    maintainer='Ann John',
    maintainer_email='amjohn@andrew.cmu.edu',
    license='MIT',
    packages=['ScholarQuest'],
    install_requires=['requests'],
    scripts=[],
    entry_points={
        'console_scripts':
        [
            'sq = ScholarQuest.main:main'
        ]
    },
    long_description="""\
        This package is pip installable and allows users to input a\
        topic of their interest and a country (optional - if not\
        provided, it will default to the world) to get the top 10\
        institutions and top professors/authors.
    """
)
