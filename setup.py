import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smt-cal-demo",
    version="1.0.1",
    author="Michael Scheidt",
    author_email="mail@scheidt-mt.com",
    description="Calibration Management Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scheidt/py3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy>=1.19",
        "pyserial>=3.4",
        "python_dateutil>=2.8",
        "pyzmq>=19.0",
        "reportlab>=3.5",
        "scipy>=1.5",
        "simplejson>=3.17",
        "SQLAlchemy>=1.3",
        "Pillow>=7.2",
        "PyQt5>=5.15"
    ],
    entry_points = {
        'console_scripts': [
            'com = smt_cal_demo.calibration.devices.serial_devices_manager_v01:main',
            'gui = smt_cal_demo.calibration.guis.main_ui.main_calibration_v01:main',
            'cert = smt_cal_demo.calibration.reporting.certifcates.create_certificate.py',
        ],
    },

    package_data={
        # If any package contains *.png, include them:
        "": ["*.png","*.sqlite","*.ui"],
    }

)