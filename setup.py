"""aspire_dash — Aspire Academy shared Dash component & styling library."""
from setuptools import setup, find_packages

setup(
    name="aspire_dash",
    version="0.1.0",
    description="Aspire Academy shared Dash branding, components, and layouts",
    author="Kenny McMillan",
    packages=find_packages(),
    package_data={"aspire_dash": ["assets/*", "assets/**/*", "templates/*"]},
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "dash>=2.14",
        "dash-bootstrap-components>=1.5",
        "plotly>=5.18",
        "pyyaml>=6.0",
        "dash-svg>=0.0.12",
    ],
    entry_points={
        "console_scripts": [
            "aspire-dash=aspire_dash.__main__:main",
        ],
    },
)
