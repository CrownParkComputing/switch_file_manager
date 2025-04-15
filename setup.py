import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='nsz',
	version='4.6.1',
	script="nsz.py",
	author="Jon Whittingham (Original creator: Nico Bosshard)",
	author_email="jon@crownparkcomputing.com",
	maintainer="Jon Whittingham",
	maintainer_email="jon@crownparkcomputing.com",
	description="NSZ - Homebrew compatible NSP/XCI compressor/decompressor",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/jonwhittingham/switch-file-manager",
	packages=['nsz', 'nsz.Fs', 'nsz.nut', 'nsz.gui_qt'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires=[
		'pycryptodome',
		'zstandard',
		'enlighten',
		'PySide6>=6.0.0',
		'qt-material>=2.14',
	],
	entry_points = {
		'console_scripts': ['nsz = nsz:main'],
		'gui_scripts': ['nsz-qt = nsz.gui_qt.main_qt:main']
	},
	keywords = ['nsz', 'xcz', 'ncz', 'nsp', 'xci', 'nca', 'Switch', 'file-manager'],
	python_requires='>=3.6',
	zip_safe=False,
	include_package_data=True,
 )
