# setup.py
from setuptools import setup, find_packages

setup(
    name='snapforge',
    version='0.1.0',
    description='图像处理工具',
    author='Your Name',
    author_email='your_email@example.com',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'opencv-python',
        'PyQt5',
        'pyyaml',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'snapforge = snapforge.__main__:main',
        ],
    },
)