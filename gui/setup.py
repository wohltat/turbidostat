from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
includes = [
  'matplotlib.legend_handler', 
  'matplotlib.style', 
  'matplotlib.backends.backend_tkagg', 
  'tkinter.filedialog',
  'wx.xml',
  # 'numpy',
  # 'scipy',
  # 'wx',
  # 'encodings',
  ]
excludes = [
  'PySide2', 
  'PyQt4', 
  'PyQt5',
  'apt',
  'apport',
  'attr',
  'asyncio',
  'audioop',
  'bs4',
  'bz2',
  'cairo',
  'chardet',
  'cryptography',
  'curses',
  'colorama',
  'cffi',
  'concurrent',
  'gi',
  'html',
  'html5lib',
  'ipykernel',
  'IPython',
  'jedi',
  'jupyter_client',
  'jinja2',
  'keyring',
  'lib2to3',
  'lxml',
  'mmap',
  'mpl_toolkits',
  'multiprocessing',
  'pkg_resources',
  'psutil',
  'reportlab',
  'tornado',
  'pip',
  'mock',
  'OpenSSL',
  'pytz',
  'pydoc_data',
  'pandas',
  'PIL',
  'qtpy',
  'readline',
  'ssl',
  'setuptools',
  'xml',
  'zmq','*'
  'scipy.spatial'
  # 'ctypes',
  # 'collections',
  # 'dateutil',
  # 'json',
  # 'email',
  # 'http',
  # 'tkinter',
  # 'unittest',
  # 'urllib',
  ]
buildOptions = dict(
          packages = includes, 
          excludes = excludes, 
          includes= includes,
          zip_include_packages = [
            'ctypes', 'collections', 'encodings', 'distutils', 'email', 'unittest', 'serial', 'dateutil', 'importlib', 
            'urllib', 'tkinter', 'json', 'http', 'wx', 'scipy', 'test', 'matplotlib', 'logging',
            # 'numpy',
            ], 
          # zip_exclude_packages = "numpy"
          # zip_exclude_packages = ""
          )

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('turbidostat.py', base=base)
]

setup(name='TurbidostatGUI',
      version = '0.405',
      description = 'Turbidostat GUI',
      options = dict(build_exe = buildOptions),
      executables = executables)
