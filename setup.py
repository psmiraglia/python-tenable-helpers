from setuptools import find_packages, setup

from tenable_helpers import version


def get_requirements():
    requirements = []
    with open('requirements.txt', 'r') as fp:
        requirements = [line.strip() for line in fp.readlines()]
        fp.close()

    if not requirements:
        emsg = 'Unable to obtain requirements list'
        raise Exception(emsg)

    return requirements


def long_description():
    with open('README.md', 'r') as fp:
        lines = fp.readlines()
        fp.close()
    return ''.join(lines)


setup(
    name='tenable_helpers',
    version=version,
    python_requires='>=3.6',

    author='Paolo Smiraglia',
    author_email='paolo.smiraglia@gmail.com',
    description='Tenable.io CLI helpers',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/psmiraglia/python-tenable-helpers',

    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'po2tag = tenable_helpers.scripts.po2tag:po2tag',
            'group2tag = tenable_helpers.scripts.group2tag:group2tag',
        ],
    }
)
