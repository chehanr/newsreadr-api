"""Routes for API Version 2."""

from flasgger import swag_from
from flask import Blueprint, jsonify, redirect, request, url_for

from .newsreadr import (fetch_archives, fetch_archives_list, fetch_articles,
                        fetch_link_lists)

from .constants import BASE_URL

API = Blueprint('routes_v2', __name__)


@API.route('/')
def api_v2_root():
    """Redirect back to api information."""
    return redirect(url_for('api_root'), code=303)


@API.route('/articles', methods=['GET'])
@swag_from('docs/get_articles.yml')
def get_articles():
    """Get a list of the articles."""

    page = request.args.get('page', default=1, type=int)
    page_url, remote_status_code, available_pages, articles = fetch_articles(
        BASE_URL, page)

    results = {
        'request-type': 'get-articles',
        'page-url': page_url,
        'remote-status-code': remote_status_code,
        'page': page,
        'available-pages': available_pages,
        'articles': articles
    }

    return jsonify(results)


@API.route('/archives/find', methods=['GET'])
@swag_from('docs/get_archives.yml')
def get_archives():
    """Get list of the archived articles."""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=str)
    page = request.args.get('page', default=1, type=int)
    page_url, remote_status_code, available_pages, archives = fetch_archives(
        year, month, page)

    results = {
        'request-type': 'get-archives',
        'page-url': page_url,
        'remote-status-code': remote_status_code,
        'year': year,
        'month': month,
        'page': page,
        'available-pages': available_pages,
        'articles': archives
    }

    return jsonify(results)


@API.route('/archives', methods=['GET'])
@swag_from('docs/get_archives_list.yml')
def get_archives_list():
    """Get a list of the archive index."""
    page_url, remote_status_code, archives_list = fetch_archives_list()

    results = {
        'request-type': 'get-archives-list',
        'page-url': page_url,
        'remote-status-code': remote_status_code,
        'archives-list': archives_list
    }

    return jsonify(results)


@API.route('/links', methods=['GET'])
@swag_from('docs/get_links_list.yml')
def get_links_list():
    """Get a list of the link index."""
    list_type = request.args.get('list-type', type=str)
    page_url, remote_status_code, link_list = fetch_link_lists(
        list_type)

    results = {
        'request-type': 'get-link-list',
        'list-type': list_type,
        'page-url': page_url,
        'remote-status-code': remote_status_code,
        'link-list': link_list
    }

    return jsonify(results)
