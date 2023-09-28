# PyPi Notes

My notes, not for general consumption

	On Mac:
	
	conda activate pymovie-env
	pip3 install build	# if not already installed
	pip3 install twine	# if not already installed
	cd ~/Desktop/Astro
	python3 -m build --sdist ravf
	cd ravf
	twine upload dist/ravf-1.0.0.tar.gz
		username: __token__
		password: API Key 


References:

* [Snarky - Release Fixing](https://snarky.ca/what-to-do-when-you-botch-a-release-on-pypi/)