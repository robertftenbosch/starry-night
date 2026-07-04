from setuptools import setup, find_packages

setup(
    name="starry-night",
    version="0.1.0",
    author="Starry Night Developer",
    author_email="developer@example.com",
    description="A dome-like starry night visualization application for celestial objects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/starry-night",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pygame>=2.0.0",
        "requests>=2.25.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "starry-night=starry_night.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)