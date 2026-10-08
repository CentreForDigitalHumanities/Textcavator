from datetime import datetime

MIN_DATE = datetime(year=1800, month=1, day=1)
MAX_DATE = datetime(year=2025, month=12, day=31)


def document_context(context_fields = ['debate_id'], sort_field = 'sequence', sort_direction = 'asc', context_display_name = 'debate'):
    return {
        'context_fields': context_fields,
        'sort_field': sort_field,
        'sort_direction': sort_direction,
        'context_display_name': context_display_name
    }
