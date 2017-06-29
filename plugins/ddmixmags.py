from __future__ import unicode_literals, division, absolute_import
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin

import logging
import re
import base64
import string

from flexget import plugin
from flexget.event import event
from flexget.plugins.internal.urlrewriting import UrlRewritingError

log = logging.getLogger('ddmixmags')

class UrlRewriteDDmixMags(object):

    # urlrewriter API
    def url_rewritable(self, task, entry):
        url = entry['url']
        if url.startswith('https://ddmix.net/') or url.startswith('https://www.ddmix.net/'):
            return True
        return False

    # urlrewriter API
    def url_rewrite(self, task, entry):
        entry['url'] = self.parse_download_page(entry['url'], task.requests)

    @plugin.internet(log)
    def parse_download_page(self, url, requests):
        txheaders = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        page = requests.get(url, headers=txheaders)

        match = re.findall('mirror[0-9]_openload\',\'(.*?)\'\)',page.text)
        if len(match) == 0:
            raise UrlRewritingError('Unable to locate Openload hash from url %s' % url)
        urlhash = match[0]
        data = base64.b64decode(urlhash)
        data = data.split("-")
        down_link = ""
        for char in data:
            down_link += str(unichr(int(char)))
        if not down_link:
            raise UrlRewritingError('Unable to locate download link from url %s' % url)
        return down_link

@event('plugin.register')
def register_plugin():
    plugin.register(UrlRewriteDDmixMags, 'ddmixmags', interfaces=['urlrewriter'], api_ver=2)