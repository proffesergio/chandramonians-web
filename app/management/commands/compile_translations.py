from django.core.management.base import BaseCommand
from pathlib import Path
import polib


class Command(BaseCommand):
    help = 'Compile .po translation files to .mo (no system gettext required — uses polib)'

    def handle(self, *args, **options):
        locale_dir = Path(__file__).resolve().parents[3] / 'locale'
        po_files = list(locale_dir.rglob('*.po'))
        if not po_files:
            self.stdout.write(self.style.WARNING(f'No .po files found in {locale_dir}'))
            return
        for po_path in po_files:
            mo_path = po_path.with_suffix('.mo')
            po = polib.pofile(str(po_path), encoding='utf-8')
            po.save_as_mofile(str(mo_path))
            count = len([e for e in po if e.msgstr])
            self.stdout.write(
                self.style.SUCCESS(f'Compiled {po_path.name} -> {mo_path.name}  ({count} strings)')
            )
