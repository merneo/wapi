"""
Setup configuration for WAPI CLI package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as fh:
        requirements = [
            line.strip()
            for line in fh
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="wapi-cli",
    version="0.9.0",
    author="WAPI CLI Team",
    author_email="",  # Add contact email if available
    description="Command-line interface for WEDOS WAPI - Manage domains, DNS, and NSSETs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merneo/wapi",
    project_urls={
        "Bug Reports": "https://github.com/merneo/wapi/issues",
        "Source": "https://github.com/merneo/wapi",
        "Documentation": "https://github.com/merneo/wapi/blob/master/WIKI.md",
        "Changelog": "https://github.com/merneo/wapi/blob/master/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dns": ["dnspython>=2.0.0,<3.0.0"],
        "dev": [
            "black>=23.0.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "flake8>=6.0.0,<8.0.0",
            "mypy>=1.0.0,<2.0.0",
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "pre-commit>=3.0.0,<4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wapi=wapi.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="wedos, wapi, domain, dns, nameserver, nsset, cli, command-line",
    license="MIT",
    platforms=["any"],
)
