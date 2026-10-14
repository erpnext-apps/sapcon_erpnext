from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in custom_sapcon/__init__.py
from custom_sapcon import __version__ as version

setup(
	name="sapcon_custom",
	version=version,
	description="Sapcon Custom",
	author="Frappe",
	author_email="krithi@erpnext.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
