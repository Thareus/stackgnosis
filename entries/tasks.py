from bs4 import BeautifulSoup
import re
from celery import shared_task
from .models import Entry

import logging
logger = logging.getLogger("django")

@shared_task
def hyperlink_entry(entry_pk):
    logger.info(f"[hyperlink_entry] Starting for {entry_pk}")

    def replace_titles_with_links(entry_title, html_content, link_title, link_slug):
        html = BeautifulSoup(html_content, 'html.parser')

        text_nodes = []
        for element in html.find_all(text=True):
            if element.parent.name != 'a':  # Skip text inside <a> tags
                text_nodes.append(element)

        # Replace title in each text node
        for text_node in text_nodes:
            pattern = r'(?i)(?<!\w)(' + re.escape(link_title) + r')(?!\w)'
            replacement = f'<a href="/entries/{link_slug}">{re.escape(link_title)}</a>'
            new_text = re.sub(pattern, replacement, str(text_node))

            # Only replace if something changed
            if new_text != str(text_node):
                new_html = BeautifulSoup(new_text, 'html.parser')
                text_node.replace_with(new_html)
                logger.info(f"[hyperlink_entry] Added link to {link_title} to {entry_title}")
        return html

    try:

        entry = Entry.objects.get(pk=entry_pk)
        entries = Entry.objects.all()
        entry_titles = entries.values_list('title', 'slug')
        updated_entries = []
        # Update entry with links to other entries
        for title, slug in entry_titles:
            entry.description = replace_titles_with_links(entry.title, entry.description, title, slug)
        entry.save()

        # Update other entries with link to new entry
        for other_entry in entries:
            other_entry.description = replace_titles_with_links(other_entry.title, other_entry.description, entry.title, entry.slug)
            updated_entries.append(other_entry)        
        if updated_entries:
            Entry.objects.bulk_update(updated_entries, ['description'])        
        
    except Exception as e:
        logger.error(f"[hyperlink_entry] Error for entry_pk={entry_pk}: {e}")