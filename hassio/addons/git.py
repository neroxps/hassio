"""Init file for HassIO addons git."""
import asyncio
import logging
import os
import shutil
import tempfile

import git

from ..const import URL_HASSIO_ADDONS

_LOGGER = logging.getLogger(__name__)


class AddonsRepo(object):
    """Manage addons git repo."""

    def __init__(self, config, loop, path, url):
        """Initialize git base wrapper."""
        self.config = config
        self.loop = loop
        self.repo = None
        self.path = path
        self.url = url
        self._lock = asyncio.Lock(loop=loop)

    async def load(self):
        """Init git addon repo."""
        if not os.path.isdir(self.path):
            return await self.clone()

        async with self._lock:
            try:
                _LOGGER.info("Load addons repository")
                self.repo = await self.loop.run_in_executor(
                    None, git.Repo, self.path)

            except (git.InvalidGitRepositoryError, git.NoSuchPathError) as err:
                _LOGGER.error("Can't load %s repo: %s.", self.path, err)
                return False

            return True

    async def clone(self):
        """Clone git addon repo."""
        async with self._lock:
            try:
                _LOGGER.info("Clone addons repository")
                self.repo = await self.loop.run_in_executor(
                    None, git.Repo.clone_from, self.url, self.path)

            except (git.InvalidGitRepositoryError, git.NoSuchPathError) as err:
                _LOGGER.error("Can't clone %s repo: %s.", self.url, err)
                return False

            return True

    async def pull(self):
        """Pull git addon repo."""
        if self._lock.locked():
            _LOGGER.warning("It is already a task in progress.")
            return False

        async with self._lock:
            try:
                _LOGGER.info("Pull addons repository")
                await self.loop.run_in_executor(
                    None, self.repo.remotes.origin.pull)

            except (git.InvalidGitRepositoryError, git.NoSuchPathError) as err:
                _LOGGER.error("Can't pull %s repo: %s.", self.url, err)
                return False

            return True


class AddonsRepoHassIO(AddonsRepo):
    """HassIO addons repository."""

    def __init__(self, config, loop):
        """Initialize git hassio addon repository."""
        super()__init__(
            config, loop, config.path_addons_repo, URL_HASSIO_ADDONS)


class AddonsRepoCustom(AddonsRepo)
    """Custom addons repository."""

    def __init__(self, config, loop, url, slug=None):
        """Initialize git hassio addon repository."""
        if slug is None:
            _LOGGER("Init new custom addon repository %s", url)
            with tempfile.TemporaryDirectory(dir=config.path_addons_custom) \
                    temp_dir:
                slug = temp_dir.name

            config.add_addons_repository(url, slug)

        path = os.path.join(config.path_addons_custom, slug)
        super()__init__(config, loop, path, url)

    def remove(self):
        """Remove a custom addon."""
        if os.path.isdir(self.path):
            _LOGGER.info("Remove custom addon repository %s", self.url)

            def log_err(funct, path, _):
                """Log error."""
                _LOGGER.warning("Can't remove %s", path)

            shutil.rmtree(self.path, onerror=log_err)

        self.config.drop_addons_repository(self.url)
