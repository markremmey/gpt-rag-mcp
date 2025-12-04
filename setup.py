from setuptools import setup, find_packages

setup(
    name='gpt-rag-mcp',
    version='0.2.0',
    author='Microsoft Corporation',
    author_email='markremmey@microsoft.com',
    description='GPT RAG MCP (Model Context Protocol) library',
    packages=find_packages(
        exclude=['tools.custom*', 'agents.custom.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9'    
)