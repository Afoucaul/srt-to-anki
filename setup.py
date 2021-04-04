import setuptools


requirements = []
with open("./requirements.txt", "r") as fd:
    for requirement in fd:
        requirements.append(requirement.strip())


setuptools.setup(
    name="srt-to-anki",
    version="1.0.0",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["srt-to-anki=srt_to_anki.__main__:main"]},
)
