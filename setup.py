from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in tianjy_organization/__init__.py
from tianjy_organization import __version__ as version

setup(
	name="tianjy_organization",
	version=version,
	description="天玑组织 Tianjy Organization",
	author="天玑 Tinajy",
	author_email="天玑 Tinajy",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
