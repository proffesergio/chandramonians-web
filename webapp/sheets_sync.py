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
from datetime import datetime, date

from django.conf import settings

logger = logging.getLogger(__name__)


def _get_credentials():
    """Decode and return Google service account credentials from env var."""
    creds_b64 = settings.GOOGLE_CREDS_JSON
    if not creds_b64:
        raise ValueError("GOOGLE_CREDS_JSON environment variable is not set.")
    creds_json = base64.b64decode(creds_b64).decode('utf-8')
    return json.loads(creds_json)


def _parse_date(value: str):
    """Try to parse a date string in multiple common formats."""
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d.%m.%Y'):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def _normalize_header(header: str) -> str:
    """Normalize a column header to a consistent key."""
    return header.strip().lower().replace(' ', '_')


def sync_sheet_tab(sheet, member_type: str, worksheet_index: int) -> dict:
    """
    Sync one worksheet tab (Life Members or General Members).

    Args:
        sheet: gspread Spreadsheet object
        member_type: 'LIFE' or 'GENERAL'
        worksheet_index: 0 for first tab, 1 for second tab, etc.

    Returns:
        dict with 'added', 'updated', 'skipped', 'errors' counts
    """
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

    # Map normalized header names to MembershipPayment fields
    field_map = {
        'name': 'member_name',
        'member_name': 'member_name',
        'full_name': 'member_name',
        'payment_date': 'payment_date',
        'date': 'payment_date',
        'amount': 'amount',
        'fee': 'amount',
        'receipt_no': 'receipt_number',
        'receipt_number': 'receipt_number',
        'receipt': 'receipt_number',
        'batch': 'batch_year',
        'batch_year': 'batch_year',
        'passing_year': 'batch_year',
        'phone': 'phone',
        'mobile': 'phone',
        'status': 'status',
    }

    for row_idx, row in enumerate(all_rows[1:], start=2):
        try:
            if not any(cell.strip() for cell in row):
                continue

            row_data = dict(zip(headers, row))
            payment_fields = {'member_type': member_type, 'sheet_row_id': row_idx}

            for header_key, field_name in field_map.items():
                if header_key in row_data and row_data[header_key].strip():
                    value = row_data[header_key].strip()
                    if field_name == 'payment_date':
                        value = _parse_date(value)
                    elif field_name == 'amount':
                        try:
                            value = float(value.replace(',', '').replace('৳', '').replace('Tk', '').strip())
                        except ValueError:
                            value = None
                    elif field_name == 'status':
                        status_lower = value.lower()
                        if 'paid' in status_lower:
                            value = 'PAID'
                        elif 'pending' in status_lower:
                            value = 'PENDING'
                        elif 'partial' in status_lower:
                            value = 'PARTIAL'
                        else:
                            value = 'PAID'
                    payment_fields[field_name] = value

            if not payment_fields.get('member_name'):
                stats['skipped'] += 1
                continue

            obj, created = MembershipPayment.objects.update_or_create(
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
    """
    Main sync function. Reads both Life Members and General Members sheets
    and upserts into MembershipPayment.

    Returns:
        Summary dict with totals and timestamp.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        logger.error("gspread / google-auth not installed. Run: pip install gspread google-auth")
        return {'success': False, 'error': 'Required packages not installed.'}

    sheet_id = settings.GOOGLE_SHEET_ID
    if not sheet_id:
        return {'success': False, 'error': 'GOOGLE_SHEET_ID not configured.'}

    try:
        creds_dict = _get_credentials()
    except Exception as e:
        return {'success': False, 'error': f'Credentials error: {e}'}

    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]

    try:
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(sheet_id)
    except Exception as e:
        logger.error(f"Google Sheets connection error: {e}")
        return {'success': False, 'error': str(e)}

    # Tab 0 = Life Members, Tab 1 = General Members (adjust if your sheet differs)
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
