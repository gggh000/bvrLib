echo "Current version is: "
cat setup.py  | grep version
echo "Make sure to increment the version before uploading."
python setup.py sdist bdist_wheel
twine upload dist/*
