# setup.py
from setuptools import setup, find_packages

setup(
    name='snapforge',
    version='0.1.0',
    description='图像处理工具',
    author='Your Name',  # 请填写你的名字
    author_email='your_email@example.com',  # 请填写你的邮箱
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
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',  # 确保使用的是正确的 Python 版本
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Multimedia :: Graphics',
    ],
    python_requires='>=3.8',  # 请根据你的实际 Python 版本要求填写
)
