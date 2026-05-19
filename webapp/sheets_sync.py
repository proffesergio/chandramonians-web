"""
Google Sheets sync service for Chandramonians membership payment data.

Reads Life Members and General Members from the configured Google Sheet,
then upserts records into the MembershipPayment model.

Sheet ID: configured via GOOGLE_SHEET_ID env var
Sheet URL: https://docs.google.com/spreadsheets/d/1X4T058McT6GTnmUyu1OsmLua9BwKPEz03Rr-rbcMRvs

Setup (one-time):
1. Go to console.cloud.google.com → enable Google Sheets API + Google Drive API
2. Create a Service Account and download the JSON credentials file
3. Base64-encode the JSON: base64 credentials.json
4. Set GOOGLE_CREDS_JSON=<base64 string> in your .env file
5. Share the Google Sheet with the service account email (Viewer access)
"""

import base64
import json
import logging
import re
from datetime import datetime

from django.conf import settings

logger = logging.getLogger(__name__)

# Maps normalised column headers → MembershipPayment field names.
# Covers both the actual sheet headers and common CSV variants.
FIELD_MAP = {
    # Name — sheet uses "Member's Name"
    'name':            'member_name',
    'member_name':     'member_name',
    'member_s_name':   'member_name',   # "Member's Name" after normalisation
    'members_name':    'member_name',
    'full_name':       'member_name',
    # Payment date — sheet uses "Due date"
    'due_date':        'payment_date',
    'payment_date':    'payment_date',
    'date':            'payment_date',
    # Amount — sheet uses "Total Paid Amount" or "One Time Payment"
    'total_paid_amount': 'amount',
    'one_time_payment':  'amount',
    'amount':            'amount',
    'fee':               'amount',
    # Receipt (may not exist in the sheet)
    'receipt_no':      'receipt_number',
    'receipt_number':  'receipt_number',
    'receipt':         'receipt_number',
    # Batch — sheet uses "Batch"
    'batch':           'batch_year',
    'batch_year':      'batch_year',
    'passing_year':    'batch_year',
    # Phone — sheet uses "Mobile Number"
    'mobile_number':   'phone',
    'mobile':          'phone',
    'phone':           'phone',
    # Status — sheet uses "Payment Status"
    'payment_status':  'status',
    'status':          'status',
}


def _normalize_header(header: str) -> str:
    """Lowercase, strip/collapse non-alphanumeric chars to underscores.

    "Member's Name" → "member_s_name"
    "Mobile Number" → "mobile_number"
    "Payment Status" → "payment_status"
    """
    return re.sub(r'[^a-z0-9]+', '_', header.strip().lower()).strip('_')


def _parse_date(value: str):
    """Try common date formats; return a date object or None."""
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d.%m.%Y'):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def _parse_value(field_name: str, raw: str):
    """Convert a raw string to the appropriate Python type for field_name."""
    value = raw.strip()
    if not value or value.lower() in ('none', 'n/a', '-', '—', ''):
        return None
    if field_name == 'payment_date':
        return _parse_date(value)
    if field_name == 'amount':
        try:
            return float(value.replace(',', '').replace('৳', '').replace('Tk', '').strip())
        except ValueError:
            return None
    if field_name == 'status':
        sl = value.lower()
        if 'paid' in sl:
            return 'PAID'
        if 'pending' in sl:
            return 'PENDING'
        if 'partial' in sl:
            return 'PARTIAL'
        return 'PAID'
    return value


def parse_row_to_fields(row_data: dict) -> dict:
    """Map a {normalised_header: raw_value} dict to MembershipPayment field values.

    Shared by the Sheets sync, CSV upload, and Excel upload paths.
    Returns an empty dict when no member_name is found (row should be skipped).
    """
    result = {}
    seen_fields = set()
    for header_key, field_name in FIELD_MAP.items():
        if field_name in seen_fields:
            continue  # already filled from a higher-priority column
        raw = row_data.get(header_key, '')
        if not raw:
            continue
        parsed = _parse_value(field_name, str(raw))
        if parsed is not None:
            result[field_name] = parsed
            seen_fields.add(field_name)
    return result


def _get_credentials():
    """Decode and return Google service account credentials from env var."""
    creds_b64 = settings.GOOGLE_CREDS_JSON
    if not creds_b64:
        raise ValueError("GOOGLE_CREDS_JSON environment variable is not set.")
    creds_b64 = ''.join(creds_b64.split())
    creds_b64 += '=' * (-len(creds_b64) % 4)
    creds_json = base64.b64decode(creds_b64).decode('utf-8')
    return json.loads(creds_json)


def sync_sheet_tab(sheet, member_type: str, worksheet_index: int) -> dict:
    """Sync one worksheet tab (Life Members or General Members)."""
    from app.models import MembershipPayment

    try:
        ws = sheet.get_worksheet(worksheet_index)
    except Exception as e:
        logger.error(f"Cannot open worksheet {worksheet_index}: {e}")
        return {'added': 0, 'updated': 0, 'skipped': 0, 'errors': 1}

    all_rows = ws.get_all_values()
    if len(all_rows) < 2:
        logger.info(f"Worksheet {worksheet_index} has no data rows.")
        return {'added': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

    headers = [_normalize_header(h) for h in all_rows[0]]
    stats = {'added': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

    for row_idx, row in enumerate(all_rows[1:], start=2):
        try:
            if not any(cell.strip() for cell in row):
                continue

            row_data = dict(zip(headers, row))
            payment_fields = parse_row_to_fields(row_data)

            if not payment_fields.get('member_name'):
                stats['skipped'] += 1
                continue

            _, created = MembershipPayment.objects.update_or_create(
                member_type=member_type,
                sheet_row_id=row_idx,
                defaults=payment_fields,
            )
            if created:
                stats['added'] += 1
            else:
                stats['updated'] += 1

        except Exception as e:
            logger.error(f"Error processing row {row_idx}: {e}")
            stats['errors'] += 1

    return stats


def sync_all() -> dict:
    """Read both Life Members and General Members sheets and upsert into MembershipPayment."""
    try:
        import gspread
    except ImportError:
        logger.error("gspread not installed. Run: pip install gspread")
        return {'success': False, 'error': 'gspread package not installed.'}

    sheet_id = settings.GOOGLE_SHEET_ID
    if not sheet_id:
        return {'success': False, 'error': 'GOOGLE_SHEET_ID not configured.'}

    try:
        creds_dict = _get_credentials()
    except Exception as e:
        return {'success': False, 'error': f'Credentials error: {e}'}

    try:
        # gspread.service_account_from_dict() is the correct API for gspread >= 6
        client = gspread.service_account_from_dict(creds_dict)
        sheet = client.open_by_key(sheet_id)
    except Exception as e:
        logger.error(f"Google Sheets connection error: {e}")
        return {'success': False, 'error': str(e)}

    # Tab 0 = Life Members Data, Tab 1 = General Members
    life_stats = sync_sheet_tab(sheet, 'LIFE', worksheet_index=0)
    general_stats = sync_sheet_tab(sheet, 'GENERAL', worksheet_index=1)

    summary = {
        'success': True,
        'synced_at': datetime.now().isoformat(),
        'life_members': life_stats,
        'general_members': general_stats,
        'total_added': life_stats['added'] + general_stats['added'],
        'total_updated': life_stats['updated'] + general_stats['updated'],
        'total_errors': life_stats['errors'] + general_stats['errors'],
    }

    logger.info(f"Sheets sync complete: {summary}")
    return summary
