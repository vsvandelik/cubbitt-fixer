import setuptools

setuptools.setup(
    name="cubbitt-fix-vsvandelik",
    version="0.1.1",
    author="Vojtech Svandelik",
    author_email="vojtech.svandelik@gmail.com",
    description="CUBBITT fixer for numbers, units and possible names problems.",
    url="https://github.com/vsvandelik/cubbitt-fixer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "conllu",
        "requests",
        "tabulate",
        "word2number",
        "pyyaml",
        "ufal.udpipe"
    ]
)
