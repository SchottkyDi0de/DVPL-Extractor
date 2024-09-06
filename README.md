# License: MIT
Copyright 2024 [vladislawzero@gmail.com](mailto:vladislawzero@gmail.com) | discord: _zener_dioder | [https://github.com/SchottkyDi0de](https://github.com/SchottkyDi0de)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This license applies to all files in this project that contain Python source code unless otherwise specified!

# Releases:

pass

# Platforms:

Windows 10 or later

# Used libs

lz4 4.3.3

psutil 6.0.0

customtkinter 5.2.2

### Bulder

auto-py-to-exe 2.44.1

# Build

### Requirements:
Windows 10 or later

[Python 3.11](https://www.python.org/downloads/release/python-3110/) or later

### 1: Prepare
Download the repository

Create virtual environment
`python -m venv .env`

and activate
`.env/scripts/activate`

install dependencies
`pip install -r requirements.txt`

### 2: Start build

Run builder:
`auto-py-to-exe`

When the build program opens, select `main.py` as the script in the root of the project and select the `customtkinter` package folder in the dependencies (show location of package: `pip show customtkinter`). I also recommend to choose window mode to hide the console in the finished application. The finished application will be in the `output` folder in the root of the project

