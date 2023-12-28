from setuptools import setup

setup(
    name='Periodical File Sender',
    version='1.0',
    packages=['periodical_file_sender'],
    url='https://github.com/Hamza5/Periodical-File-Sender',
    license='MIT',
    author='Hamza Abbad',
    description='A GUI based tool to send emails with attachment periodically using an SMTP server.',
    install_requires=['PyQt5'],
    package_data={
        'periodical_file_sender': ['icon.svg']
    },
    entry_points={
        'console_scripts': ['periodical_file_sender=periodical_file_sender.PES_GUI:main']
    },
    python_requires=">=3.6"
)
