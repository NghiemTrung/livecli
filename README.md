# [Livecli][livecli-website]

[![TravisCI build status][travisci-build-status-badge]][travisci-build-status] [![AppVeyor][appveyor-badge]][appveyor] [![codecov.io][codecov-coverage-badge]][codecov-coverage] [![pypi.python.org][pypi-badge]][pypi]

Livecli is a CLI utility that pipes flash videos from online streaming services to a variety of video players such as VLC, or alternatively, a browser.

The main purpose of livecli is to convert CPU-heavy flash plugins to a less CPU-intensive format.

Livecli is a fork of the [Streamlink][streamlink] and [Livestreamer][livestreamer] project.

Please note that by using this application you're bypassing ads run by
sites such as Twitch.tv. Please consider donating or paying for subscription
services when they are available for the content you consume and enjoy.


# [Installation][livecli-installation]

#### Installation via Python pip

```bash
pip install livecli
```

#### Manual installation via Python

```bash
git clone https://github.com/livecli/livecli
cd livecli
pip install -U .
```

#### Windows, MacOS, Linux and BSD specific installation methods

- [Windows][livecli-installation-windows]
- [Windows portable version][livecli-installation-windows-portable]
- [MacOS][livecli-installation-others]
- [Linux and BSD][livecli-installation-linux]


# Features

Livecli is built via a plugin system which allows new services to be easily added.

Supported streaming services, among many others, are:

- [Dailymotion](https://www.dailymotion.com)
- [Livestream](https://livestream.com)
- [Twitch](https://www.twitch.tv)
- [UStream](http://www.ustream.tv)
- [YouTube Live](https://www.youtube.com)

A list of all supported plugins can be found on the [plugin page][livecli-plugins].


# Quickstart

After installing, simply use:

```
livecli STREAMURL best
```

Livecli will automatically open the stream in its default video player!
See [Livecli's detailed documentation][livecli-documentation] for all available configuration options, CLI parameters and usage examples.


# Contributing

All contributions are welcome.
Feel free to open a new thread on the issue tracker or submit a new pull request.
Please read [CONTRIBUTING.md][contributing] first. Thanks!


  [livecli-website]: https://livecli.github.io
  [livecli-plugins]: https://livecli.github.io/plugin_matrix.html
  [livecli-documentation]: https://livecli.github.io/cli.html
  [livecli-installation]: https://livecli.github.io/install.html
  [livecli-installation-windows]: https://livecli.github.io/install.html#windows-binaries
  [livecli-installation-windows-portable]: https://livecli.github.io/install.html#windows-portable-version
  [livecli-installation-linux]: https://livecli.github.io/install.html#linux-and-bsd-packages
  [livecli-installation-others]: https://livecli.github.io/install.html#other-platforms
  [streamlink]: https://github.com/streamlink/streamlink
  [livestreamer]: https://github.com/chrippa/livestreamer
  [contributing]: https://github.com/livecli/livecli/blob/master/CONTRIBUTING.md
  [changelog]: https://github.com/livecli/livecli/blob/master/CHANGELOG.rst
  [contributors]: https://github.com/livecli/livecli/graphs/contributors
  [travisci-build-status]: https://travis-ci.org/livecli/livecli
  [travisci-build-status-badge]: https://img.shields.io/travis/livecli/livecli/master.svg?style=flat-square
  [appveyor]: https://ci.appveyor.com/project/back-to/livecli
  [appveyor-badge]: https://img.shields.io/appveyor/ci/back-to/livecli/master.svg?style=flat-square
  [codecov-coverage]: https://codecov.io/github/livecli/livecli?branch=master
  [codecov-coverage-badge]: https://img.shields.io/codecov/c/github/livecli/livecli/master.svg?style=flat-square
  [pypi]: https://pypi.python.org/pypi/livecli
  [pypi-badge]: https://img.shields.io/pypi/v/livecli.svg?style=flat-square
