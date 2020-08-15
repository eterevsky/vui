import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name='vui',
    version='0.0.4',
    author='Oleg Eterevsky',
    author_email='oleg@eterevsky.com',
    description='GUI framework written in pure Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eterevsky/vui',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha'
    ],
    python_requires='>=3.6',
    install_requires='pyglet>=1.5.6',
)