from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")


setup(
	name="tianjy_organization",
	version='0.0.1',
	description="天玑组织 Tianjy Organization",
	author="天玑 Tinajy",
	author_email="天玑 Tinajy",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
