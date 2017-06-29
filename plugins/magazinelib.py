from __future__ import unicode_literals, division, absolute_import
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin

import logging
import re

from flexget import plugin
from flexget.event import event
from flexget.plugins.internal.urlrewriting import UrlRewritingError
from flexget.utils.soup import get_soup

log = logging.getLogger('magazinelib')


class UrlRewriteMagazineLib(object):
    """DeadFrog urlrewriter."""

    # urlrewriter API
    def url_rewritable(self, task, entry):
        url = entry['url']
        if url.startswith('http://www.magazinelib.com/') or url.startswith('http://magazinelib.com/'):
            return True
        return False

    # urlrewriter API
    def url_rewrite(self, task, entry):
        entry['url'] = self.parse_download_page(entry['url'], task.requests)

    @plugin.internet(log)
    def parse_download_page(self, url, requests):
        txheaders = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        page = requests.get(url, headers=txheaders)
        try:
            soup = get_soup(page.text)
        except Exception as e:
            raise UrlRewritingError(e)
        vk_soup = soup.find('a', attrs={'href': re.compile(r'https:.*vk.com.*no_preview=1')})
        if not vk_soup:
            raise UrlRewritingError('Unable to locate download link from url %s' % url)
        vk_link = vk_soup.get('href')
        #txheaders = {'Accept': 'text/html'}
        page = requests.get(vk_link)
        if page.status_code != 200:
            raise UrlRewritingError('File does not exist in VK')
        return page.url


@event('plugin.register')
def register_plugin():
    plugin.register(UrlRewriteMagazineLib, 'magazinelib', interfaces=['urlrewriter'], api_ver=2)