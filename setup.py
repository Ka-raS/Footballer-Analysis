import setuptools

setuptools.setup(
    name='premierstats',
    version='0.1.0',
    description='A Python program to collect football players statistical data in the 2024-2025 English Premier League season.',
    author='Ka-raS',
    url='',
    packages=setuptools.find_packages(),
    python_requires='>=3.8.10',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'premierstats = source.__main__:main'
        ]
    }
)