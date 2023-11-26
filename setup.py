from setuptools import setup, find_packages

setup(
    author="Amir Motamedi",
    author_email="seyedamirhosein.motamedi@charite.de",
    name='oct-vol',
    version='0.2.0',
    description="A package to read, write, and crop OCT .vol files.",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/neurodial/oct-vol.git",
    packages=find_packages(),
    install_requires=['numpy'],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3'
    ]
)
