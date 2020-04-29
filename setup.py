import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pimetrics",
    version="0.1.0",
    author='Christophe Lambin',
    author_email='christophe.lambin@gmail.com',
    description="Metrics to measure data from different sources and report to a monitoring system (e.g. Prometheus)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/clambin/pimetrics',
    packages=['pimetrics'], # setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7')
