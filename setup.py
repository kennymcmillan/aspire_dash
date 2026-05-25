"""aspire_dash — Aspire Academy shared Dash component & styling library."""
from setuptools import setup, find_packages

setup(
    name="aspire_dash",
    version="0.37.0",
    description="Aspire Academy shared Dash branding, components, layouts, observability, timeseries, athlete + budget + time + export + tables + forms modules",
    author="Kenny McMillan",
    packages=find_packages(),
    package_data={"aspire_dash": ["assets/*", "assets/**/*", "templates/*", "brand.yml"]},
    include_package_data=True,
    python_requires=">=3.10",
    # Lower bounds set what we tested against; upper bounds prevent a
    # silent break when a downstream app pip-installs after Dash 5 / Plotly 7
    # release. Loosen these when we've actually tested the new majors.
    install_requires=[
        "dash>=2.14,<5",
        "dash-bootstrap-components>=1.5,<3",
        "plotly>=5.18,<7",
        "pyyaml>=6.0,<7",
        "dash-svg>=0.0.12,<1",
    ],
    extras_require={
        "test": ["pytest>=7", "numpy>=1.24"],
    },
    entry_points={
        "console_scripts": [
            "aspire-dash=aspire_dash.__main__:main",
        ],
    },
)
