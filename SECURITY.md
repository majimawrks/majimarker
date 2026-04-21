# Security Notes

Pillow is pinned to an exact version (`pillow==10.4.0`) to prevent unintended upgrades that may introduce CVEs or breaking parser changes. To upgrade, review the [Pillow changelog](https://pillow.readthedocs.io/en/stable/releasenotes/index.html) and any active advisories, update the pin in `requirements.txt`, and rebuild + smoke-test before shipping. Refresh at least quarterly or immediately on any security advisory.
