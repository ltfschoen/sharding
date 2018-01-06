# Sharding

[![Build Status](https://travis-ci.org/ethereum/sharding.svg?branch=develop)](https://travis-ci.org/ethereum/sharding)

This repository contains the basic sharding utils.

See the "docs" directory for documentation and EIPs, and the "sharding" directory for code.

## Installation
### Environment

Please refer to [pyethereum - Developer-Notes](https://github.com/ethereum/pyethereum/wiki/Developer-Notes)

##### macOS

  1. [Fork](https://help.github.com/articles/fork-a-repo/#fork-an-example-repository) this Sharding Github repository

  2. [Setup Git Version Control](https://help.github.com/articles/fork-a-repo/#step-1-set-up-git)

  3. [Clone](https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork) your fork of this repository. Replace `<YOUR_GITHUB_USERNAME>` below with your Github username.
    ```shell
    git clone https://github.com/<YOUR_GITHUB_USERNAME>/sharding/;
    cd sharding;
    ```

  4. Show list of available Python versions.
  [Install Homebrew](https://brew.sh/). Install PyEnv.
  Switch to latest version of Python (i.e. using [virtualenv](https://github.com/pypa/virtualenv) or [pyenv](https://github.com/pyenv/pyenv)).
  Verify the version of Python being used.

    ```shell
    brew update; brew install pyenv;
    pyenv install --list;
    pyenv install 3.6.4rc1; pyenv global 3.6.4rc1;
    pyenv versions; python --version
    ```

    * Note: Supports the following versions of Python
      * Latest Stable version of Python 3.6 (i.e. Python `3.6.4rc1`), which is recommended since Viper requires python3.6, and Pyethereum supports python3.6
      * Note: Python 3.7 Alpha has been release but may not be currently supported. What's new in Python 3.7 https://docs.python.org/3.7/whatsnew/3.7.html

  5. Install dependencies specific to operating system

    ```shell
    brew install pkg-config libffi autoconf automake libtool openssl
    ```

  6. Show existing versions of Ethereum from PyPI and Viper that are installed - https://pip.pypa.io/en/stable/reference/pip_list/
    ```shell
    pip install --upgrade pip;
    pip freeze | grep -i -E "ethereum|viper|setuptools"
    ```

  7. Uninstall previously installed versions of Ethereum from PyPI and Viper. Uninstall PyTest Catchlog to avoid warnings when running Unit Tests. See #5 in Troubleshooting section.
    * WARNING: Do not install/reinstall Ethereum from PyPI manually. See #4 in Troubleshooting section below.

    ```shell
    python -m pip uninstall setuptools -y;
    python -m pip uninstall pytest-catchlog -y
    python -m pip uninstall ethereum -y;
    python -m pip uninstall viper -y;
    ```

  8. Install dependencies for Unit Testing, and Pyethereum and Viper from a specific branch and commit hash by setting the `USE_PYETHEREUM_DEVELOP` flag
    ```
    python -m pip install setuptools==37;
    USE_PYETHEREUM_DEVELOP=1 python setup.py develop;
    python -m pip install -r dev_requirements.txt;
    ```

  9. Run Unit Tests

    ```shell
    pytest sharding/tests/
    ```

  10. Contributing

    i) Configure an remote called Upstream. Show remote configurations (your Fork of the Upstream repository is called Origin)
  
      ```
      git remote add upstream https://github.com/ethereum/sharding;
      git remote -v;
      ```

    ii) Stay up-to-date with the develop branch of this Upstream repository https://github.com/ethereum/sharding by regularly pulling its latest changes to your local machine that has a clone of your fork using a [fetch and rebase](https://stackoverflow.com/a/44982185/3208553).

      ```
      git pull --rebase upstream develop
      ```

    iii) Create and check out a branch (feature `feat/<DESCRIPTION>`, fix `fix/<DESCRIPTION>`, docs `docs/<DESCRIPTION>`, or tests `tests/<DESCRIPTION>`) using this [Udemy Git Commit Style Guide](http://udacity.github.io/git-styleguide/)

      ```
      git checkout -b feat/my-feature-name;
      ```

    iv) Save changes and provide a meaningful commit message using using this [Udemy Git Commit Style Guide](http://udacity.github.io/git-styleguide/) and push the changes to your remote Fork

      ```
      git add . && git commit -m "feat: Add my feature" && git push origin feat/my-feature-name;
      ```

    v) Create a Pull Request from the remote branch "feat/my-feature-name" in your Fork (that you just pushed) to the "develop" branch in the Upstream repository

### Troubleshooting

##### macOS

1. OpenSSL dependency error on macOS

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

2. OpenSSL symlinks broken

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

3. Latest Ethereum PyPI dependency not supported by Viper on macOS

  * Problem: Error occurs when trying to install dependencies with `python setup.py install` such as `error: ethereum 2.3.0 is installed but ethereum==2.1.0 is required by {'viper'}` complaining that the version installed of [Ethereum from Python Package Index (PyPI)](https://pypi.python.org/pypi/ethereum/2.3.0) is not supported by Viper after upgrading to the latest version Python (i.e. Python 3.6 or 3.7)

  * Solution: Uninstall old version and reinstall new version before running `python setup.py install` again

    ```
    python -m pip uninstall ethereum==2.3.0;
    python -m pip install ethereum==2.1.0
    ```

4. Unit Test not passing due to Ethereum PyPI dependency failing

 * Problem: Unit Test not passing due to error `E  KeyError: b'GENESIS_NUMBER'` in test file `sharding/tests/test_main_chain.py`
   * References:
     * https://github.com/ethereum/sharding/pull/51#issuecomment-355720781
     * https://github.com/ethereum/sharding/pull/53

* Solution: Do not install/reinstall Ethereum from Python Package Index (PyPI) or Viper manually (i.e. do not install with `python -m pip install ethereum==2.1.0`), as doing so does not install the dependency correctly. Instead install them using `USE_PYETHEREUM_DEVELOP=1 python setup.py develop`

 * Example: If you incorrectly try to install Ethereum from PyPI manually with `python -m pip install ethereum==2.1.0`, then when you run `pip show ethereum` it shows the following:

   ```shell
   $ pip show ethereum
   Name: ethereum
   Version: 2.1.0
   Summary: Next generation cryptocurrency network
   Home-page: https://github.com/ethereum/pyethereum/
   Author: UNKNOWN
   Author-email: UNKNOWN
   License: UNKNOWN
   Location: /Users/Ls/.pyenv/versions/3.6.4rc1/lib/python3.6/site-packages
   Requires: scrypt, pyethash, py-ecc, coincurve, PyYAML, rlp, pbkdf2, pycryptodome, repoze.lru, pysha3
   ```

 * Whereas when you correctly install Ethereum from PyPI using `USE_PYETHEREUM_DEVELOP=1 python setup.py develop` then when you run `pip show ethereum` you will notice that the value for its Location is provided, hence the reason why this approach works.

   ```shell
   $ pip show ethereum
   Name: ethereum
   Version: 2.1.0
   Summary: Next generation cryptocurrency network
   Home-page: https://github.com/ethereum/pyethereum/
   Author: UNKNOWN
   Author-email: UNKNOWN
   License: UNKNOWN
   Location: /Users/Ls/.pyenv/versions/3.6.4rc1/lib/python3.6/site-packages/ethereum-2.1.0-py3.6.egg
   Requires: py-ecc, scrypt, pyethash, future, pbkdf2, repoze.lru, pysha3, coincurve, pycryptodome, PyYAML, rlp
   ```
