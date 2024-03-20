About the test app
------------------
To launch the test app, you need to make sure the following repos are
adjacent to the tk-multi-publish2 repo.

- tk-core (for bootstrapping)
- tk-frameworks-qtwidgets
- tk-frameworks-shotgunutils

You also need a connection to the internet as the shell engine and the core will
be pulled from the Toolkit AppStore and the app requires a connection to a
Flow Production Tracking site. You can use any site.

The app itself has a few plugins that pretend to operate on items found in a
scene.

Install tk-toolchain and use pytest to run the tests
