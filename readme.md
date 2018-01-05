# Sharding

[![Build Status](https://travis-ci.org/ethereum/sharding.svg?branch=develop)](https://travis-ci.org/ethereum/sharding)

This repository contains the basic sharding utils.

See the "docs" directory for documentation and EIPs, and the "sharding" directory for code.

## Installation
### Environment

Please refer to [pyethereum - Developer-Notes](https://github.com/ethereum/pyethereum/wiki/Developer-Notes)

##### macOS

  1. Show list of available Python versions. Switch to latest version of Python (i.e. using [virtualenv](https://github.com/pypa/virtualenv) or [pyenv](https://github.com/pyenv/pyenv)). Verify the version of Python being used.

    ```shell
    pyenv install --list;
    pyenv install 3.6.4rc1; pyenv global 3.6.4rc1;
    pyenv versions; python --version
    ```

    * Note: Supports the following versions of Python
      * Latest Stable version of Python 3.6 (i.e. Python `3.6.4rc1`), which is recommended since Viper requires python3.6, and Pyethereum supports python3.6
      * Note: Python 3.7 Alpha has been release but may not be currently supported. What's new in Python 3.7 https://docs.python.org/3.7/whatsnew/3.7.html

  2. Install dependencies specific to operating system

    ```shell
    brew install pkg-config libffi autoconf automake libtool openssl
    ```

### Install
```shell
git clone https://github.com/ethereum/sharding/
cd sharding
python setup.py install
```
 
### Install with specific pyethereum branch and commit hash
1. Update `setup.py`
2. Set flag
```shell
USE_PYETHEREUM_DEVELOP=1 python setup.py develop
```

### Install development tool
```shell
pip install --upgrade pip;
pip install -r dev_requirements.txt
```

### Troubleshooting

##### macOS

* OpenSSL dependency error on macOS

  * Problem: Error occurs when running `USE_PYETHEREUM_DEVELOP=1 python setup.py develop`

    ```
    scrypt-1.2.0/libcperciva/crypto/crypto_aes.c:6:10: fatal error: 'openssl/aes.h' file not found
    #include <openssl/aes.h>
             ^~~~~~~~~~~~~~~
    1 error generated.
    error: Setup script exited with error: command 'clang' failed with exit status 1
    ```

  * Solution: Set SSL flags to valid directories. Use `which openssl` to verify where the OpenSSL binary executable is installed. If it is installed in `/usr/local/opt/openssl/bin` then OpenSSL is installed in `/usr/local/opt/openssl/`. Check that `/usr/local/opt/openssl/` contains the `lib` and `include` subdirectories with `ls -lha /usr/local/opt/openssl/`

    ```
    brew update; brew upgrade openssl; which openssl;
    export LDFLAGS="-L/usr/local/opt/openssl/lib";
    export CPPFLAGS="-I/usr/local/opt/openssl/include"
    ```

* OpenSSL symlinks broken

  * Problem: Error occurred after first switching to a different Python version (i.e. 3.6.4rc1), installing dependencies with `python setup.py install`, and then trying to run Unit Tests with `pytest sharding/tests/`

    ```
    E   OSError: dlopen(/Users/Ls/.pyenv/versions/3.6.4rc1/lib/python3.6/site-packages/_scrypt.cpython-36m-darwin.so, 6): Library not loaded: @rpath/libcrypto.1.0.0.dylib
    E     Referenced from: /Users/Ls/.pyenv/versions/3.6.4rc1/lib/python3.6/site-packages/_scrypt.cpython-36m-darwin.so
    E     Reason: image not found
    ```

  * Solution: Run the following commands to fix symlinks. Reference: https://github.com/tihmstar/futurerestore/issues/25. Use `which openssl` to verify where the OpenSSL binary executable is installed to determine the OpenSSL root directory (i.e. /usr/local/opt/openssl/).

    ```
    ln -s /usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib /usr/local/lib/
    ln -s /usr/local/opt/openssl/lib/libssl.1.0.0.dylib /usr/local/lib/
    ```

* Latest Ethereum PyPI dependency not supported by Viper on macOS

  * Problem: Error occurs when trying to install dependencies with `python setup.py install` such as `error: ethereum 2.3.0 is installed but ethereum==2.1.0 is required by {'viper'}` complaining that the version installed of [Ethereum from Python Package Index (PyPI)](https://pypi.python.org/pypi/ethereum/2.3.0) is not supported by Viper after upgrading to the latest version Python (i.e. Python 3.6 or 3.7)

  * Solution: Uninstall old version and reinstall new version before running `python setup.py install` again

    ```
    python -m pip uninstall ethereum==2.3.0;
    python -m pip install ethereum==2.1.0
    ```
