"""Collect selected source documents without domain projection or enrichment."""

from sttv.script.parser import parse_text
from sttv.script.serialization import serialize_document
from sttv.sources.files import read_source
from sttv.common.timing import measure


def read_document(settings, report, variables, expansion, path, encoding, before_serialization=None):
    relative = path.relative_to(settings.game).as_posix()
    try:
        with measure(report.data['performance']['timings'], 'parse_expand_serialize'):
            text = read_source(path, encoding, report, relative)
            parsed = parse_text(text, settings.syntax, relative, expansion=expansion)
            variables.apply(parsed)
            offsets = before_serialization() if before_serialization is not None else None
            document = serialize_document(parsed, offsets)
            report.data['counts']['parsed_files'] += 1
            return document
    except Exception as exc:
        if getattr(exc, 'code', None) == 'parallel_cancelled':
            raise
        report.data['counts']['failed_files'] += 1
        report.failure(exc, 'parsing', source='STELLARIS_ROOT', file=relative)
    finally:
        timings = report.data['performance']['timings']
        timings['parse_expand_serialize'] -= timings.get('id_order_wait', 0.0)
        report.data['counts']['inline_scripts'] = dict(expansion.counts)
        report.data['inline_sources'] = dict(sorted(expansion.templates.manifest.items()))
        report.data['counts']['parameters'] = dict(expansion.parameter_counts)
        report.data['counts']['max_call_depth'] = expansion.max_depth

