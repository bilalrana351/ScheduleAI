from setuptools import setup, find_packages

setup(
    name="src",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'torch',
        'numpy',
        'tqdm',
        'scikit-learn',
        'wget',
        'num2words',
        'word2number',
        'flask',
        'pytest',
        'requests',
        'flask-cors'
    ]
)