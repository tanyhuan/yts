from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_urlparse
from ..utils import (
    parse_duration,
    parse_iso8601,
    str_to_int,
)


class FourTubeBaseIE(InfoExtractor):
    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        kind, video_id, display_id = mobj.group('kind', 'id', 'display_id')

        if kind == 'm' or not display_id:
            url = self._URL_TEMPLATE % video_id

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_meta('name', webpage)
        timestamp = parse_iso8601(self._html_search_meta(
            'uploadDate', webpage))
        thumbnail = self._html_search_meta('thumbnailUrl', webpage)
        uploader_id = self._html_search_regex(
            r'<a class="item-to-subscribe" href="[^"]+/(?:channel|user)s?/([^/"]+)" title="Go to [^"]+ page">',
            webpage, 'uploader id', fatal=False)
        uploader = self._html_search_regex(
            r'<a class="item-to-subscribe" href="[^"]+/(?:channel|user)s?/[^/"]+" title="Go to ([^"]+) page">',
            webpage, 'uploader', fatal=False)

        categories_html = self._search_regex(
            r'(?s)><i class="icon icon-tag"></i>\s*Categories / Tags\s*.*?<ul class="[^"]*?list[^"]*?">(.*?)</ul>',
            webpage, 'categories', fatal=False)
        categories = None
        if categories_html:
            categories = [
                c.strip() for c in re.findall(
                    r'(?s)<li><a.*?>(.*?)</a>', categories_html)]

        view_count = str_to_int(self._search_regex(
            r'<meta[^>]+itemprop="interactionCount"[^>]+content="UserPlays:([0-9,]+)">',
            webpage, 'view count', default=None))
        like_count = str_to_int(self._search_regex(
            r'<meta[^>]+itemprop="interactionCount"[^>]+content="UserLikes:([0-9,]+)">',
            webpage, 'like count', default=None))
        duration = parse_duration(self._html_search_meta('duration', webpage))

        media_id = self._search_regex(
            r'<button[^>]+data-id=(["\'])(?P<id>\d+)\1[^>]+data-quality=', webpage,
            'media id', default=None, group='id')
        sources = [
            quality
            for _, quality in re.findall(r'<button[^>]+data-quality=(["\'])(.+?)\1', webpage)]
        if not (media_id and sources):
            player_js = self._download_webpage(
                self._search_regex(
                    r'<script[^>]id=(["\'])playerembed\1[^>]+src=(["\'])(?P<url>.+?)\2',
                    webpage, 'player JS', group='url'),
                video_id, 'Downloading player JS')
            params_js = self._search_regex(
                r'\$\.ajax\(url,\ opts\);\s*\}\s*\}\)\(([0-9,\[\] ]+)\)',
                player_js, 'initialization parameters')
            params = self._parse_json('[%s]' % params_js, video_id)
            media_id = params[0]
            sources = ['%s' % p for p in params[2]]

        token_url = 'https://tkn.kodicdn.com/{0}/desktop/{1}'.format(
            media_id, '+'.join(sources))

        parsed_url = compat_urlparse.urlparse(url)
        tokens = self._download_json(token_url, video_id, data=b'', headers={
            'Origin': '%s://%s' % (parsed_url.scheme, parsed_url.hostname),
            'Referer': url,
        })
        formats = [{
            'url': tokens[format]['token'],
            'format_id': format + 'p',
            'resolution': format + 'p',
            'quality': int(format),
        } for format in sources]
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'categories': categories,
            'thumbnail': thumbnail,
            'uploader': uploader,
            'uploader_id': uploader_id,
            'timestamp': timestamp,
            'like_count': like_count,
            'view_count': view_count,
            'duration': duration,
            'age_limit': 18,
        }


class FourTubeIE(FourTubeBaseIE):
    IE_NAME = '4tube'
    _VALID_URL = r'https?://(?:(?P<kind>www|m)\.)?4tube\.com/(?:videos|embed)/(?P<id>\d+)(?:/(?P<display_id>[^/?#&]+))?'
    _URL_TEMPLATE = 'https://www.4tube.com/videos/%s/video'
    _TESTS = [{
        'url': 'http://www.4tube.com/videos/209733/hot-babe-holly-michaels-gets-her-ass-stuffed-by-black',
        'md5': '6516c8ac63b03de06bc8eac14362db4f',
        'info_dict': {
            'id': '209733',
            'ext': 'mp4',
            'title': 'Hot Babe Holly Michaels gets her ass stuffed by black',
            'uploader': 'WCP Club',
            'uploader_id': 'wcp-club',
            'upload_date': '20131031',
            'timestamp': 1383263892,
            'duration': 583,
            'view_count': int,
            'like_count': int,
            'categories': list,
            'age_limit': 18,
        },
    }, {
        'url': 'http://www.4tube.com/embed/209733',
        'only_matching': True,
    }, {
        'url': 'http://m.4tube.com/videos/209733/hot-babe-holly-michaels-gets-her-ass-stuffed-by-black',
        'only_matching': True,
    }]


class FuxIE(FourTubeBaseIE):
    _VALID_URL = r'https?://(?:(?P<kind>www|m)\.)?fux\.com/(?:video|embed)/(?P<id>\d+)(?:/(?P<display_id>[^/?#&]+))?'
    _URL_TEMPLATE = 'https://www.fux.com/video/%s/video'
    _TESTS = [{
        'url': 'https://www.fux.com/video/195359/awesome-fucking-kitchen-ends-cum-swallow',
        'info_dict': {
            'id': '195359',
            'ext': 'mp4',
            'title': 'Awesome fucking in the kitchen ends with cum swallow',
            'uploader': 'alenci2342',
            'uploader_id': 'alenci2342',
            'upload_date': '20131230',
            'timestamp': 1388361660,
            'duration': 289,
            'view_count': int,
            'like_count': int,
            'categories': list,
            'age_limit': 18,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'https://www.fux.com/embed/195359',
        'only_matching': True,
    }, {
        'url': 'https://www.fux.com/video/195359/awesome-fucking-kitchen-ends-cum-swallow',
        'only_matching': True,
    }]


class PornTubeIE(FourTubeBaseIE):
    _VALID_URL = r'https?://(?:(?P<kind>www|m)\.)?porntube\.com/(?:videos/(?P<display_id>[^/]+)_|embed/)(?P<id>\d+)'
    _URL_TEMPLATE = 'https://www.porntube.com/videos/video_%s'
    _TESTS = [{
        'url': 'https://www.porntube.com/videos/teen-couple-doing-anal_7089759',
        'info_dict': {
            'id': '7089759',
            'ext': 'mp4',
            'title': 'Teen couple doing anal',
            'uploader': 'Alexy',
            'uploader_id': 'Alexy',
            'upload_date': '20150606',
            'timestamp': 1433595647,
            'duration': 5052,
            'view_count': int,
            'like_count': int,
            'categories': list,
            'age_limit': 18,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'https://www.porntube.com/embed/7089759',
        'only_matching': True,
    }, {
        'url': 'https://m.porntube.com/videos/teen-couple-doing-anal_7089759',
        'only_matching': True,
    }]


class PornerBrosIE(FourTubeBaseIE):
    _VALID_URL = r'https?://(?:(?P<kind>www|m)\.)?pornerbros\.com/(?:videos/(?P<display_id>[^/]+)_|embed/)(?P<id>\d+)'
    _URL_TEMPLATE = 'https://www.pornerbros.com/videos/video_%s'
    _TESTS = [{
        'url': 'https://www.pornerbros.com/videos/skinny-brunette-takes-big-cock-down-her-anal-hole_181369',
        'md5': '6516c8ac63b03de06bc8eac14362db4f',
        'info_dict': {
            'id': '181369',
            'ext': 'mp4',
            'title': 'Skinny brunette takes big cock down her anal hole',
            'uploader': 'PornerBros HD',
            'uploader_id': 'pornerbros-hd',
            'upload_date': '20130130',
            'timestamp': 1359527401,
            'duration': 1224,
            'view_count': int,
            'categories': list,
            'age_limit': 18,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'https://www.pornerbros.com/embed/181369',
        'only_matching': True,
    }, {
        'url': 'https://m.pornerbros.com/videos/skinny-brunette-takes-big-cock-down-her-anal-hole_181369',
        'only_matching': True,
    }]
