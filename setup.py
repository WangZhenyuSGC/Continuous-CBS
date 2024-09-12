from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
from Cython.Build import cythonize


class BuildCCBSExt(_build_ext):
    """Builds CCBS before our module."""

    def run(self):
        # Build CCBS
        import os
        import os.path
        import subprocess

        build_dir = os.path.abspath('build/CCBS')
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
            subprocess.check_call(['cmake', '../..'],
                                    cwd=build_dir)
        subprocess.check_call(['cmake', '--build', '../..'], cwd=build_dir)

        _build_ext.run(self)


extensions = [
    Extension('CCBS', ['*.pyx'],
                include_dirs=['../'],
                libraries=['CCBS'],
                library_dirs=['lib'])
]

setup(
    name="pyCCBS",
    ext_modules=cythonize(extensions),
    cmdclass={'build_ext': BuildCCBSExt},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Cython',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Sofstware Development :: Libraries :: Python Modules',
    ],
)