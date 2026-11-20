"""Apply narrowly configured import corrections without modifying source files."""

from dataclasses import asdict

from document_package.errors import BuildError
from .nodes import Source


class CorrectedSource(Source):
    def __init__(self, text, source):
        super().__init__(text, source.file, source.root, source.call_id)
        self.original, self.environment = source, source.environment

    def origin(self, start, end):
        return dict(self.original.origin(start, min(end, len(self.original.text))), synthetic=True,
                    generated_span=asdict(self.span(start, end)))

    def environment_at(self, start, end):
        return self.original.environment_at(start, min(end, len(self.original.text)))


class SourceExceptions:
    def __init__(self, options, report, config_file, inline_directory='common/inline_scripts', config_root='PARSER_CONFIG'):
        self.rules, self.report, self.config_file = options['rules'], report, config_file
        self.inline_directory, self.config_root = inline_directory, config_root
        ids = [rule['id'] for rule in self.rules]
        if len(set(ids)) != len(ids):
            raise BuildError('source_exception_configuration', 'Repeated source exception ID')
        self.counts = {key: 0 for key in ids}
        if report is not None:
            report.data['counts']['source_exceptions'] = self.counts

    def candidates(self, context, kind):
        root = context.root_source['file'].casefold()
        return [rule for rule in self.rules if rule['kind'] == kind
                and root in [path.casefold() for path in rule['match']['root_files']]]

    def choose(self, rules):
        if len(rules) > 1:
            raise BuildError('source_exception_conflict', 'Conflicting rules: ' + ', '.join(r['id'] for r in rules))
        return rules[0] if rules else None

    def log(self, context, rule, source, offset, before, after, value_source):
        if context.preparing:
            return
        self.counts[rule['id']] += 1
        site = source.origin(offset, offset)
        row = dict(rule_id=rule['id'], root_source=context.root_source, provenance=site,
                   call_chain=[{k: v for k, v in item.items() if k != 'identity'} for item in context.stack],
                   before=before, after=after, value_source=value_source)
        if self.report is not None:
            self.report.data['source_exceptions'].append(row)
            self.report.add('warning', 'source_exception_applied', 'expansion', rule['id'],
                            source=site['root'], file=site['file'], line=site['span']['line'])

    def reference(self, context, payload):
        rules = [rule for rule in self.candidates(context, 'script_value_reference')
                 if rule['match']['file'].casefold() == payload.origin(0, 0)['file'].casefold()
                 and rule['match']['scalar'] == payload.text]
        rule = self.choose(rules)
        if rule is None:
            return payload
        replacement = rule['action']['replace_scalar']
        self.log(context, rule, payload, 0, payload.text, replacement, self.config_file)
        return CorrectedSource(replacement, payload)

    def missing(self, context, record, options):
        def resolve(parameter, token, source, bindings):
            normalize = (lambda name: name) if options['parameter_case_sensitive'] else str.casefold
            rules = []
            target_file = record['target']['file']
            if record['kind'] == 'inline_script':
                target_file = self.inline_directory + '/' + target_file
            for rule in self.candidates(context, 'missing_parameter'):
                match = rule['match']
                if (match['call_kind'] != record['kind']
                        or match['definition_file'].casefold() != target_file.casefold()
                        or match.get('call_name', record['target'].get('name')) != record['target'].get('name')
                        or normalize(match['missing_parameter']) != normalize(parameter.name)
                        or token.raw != match['reference']
                        or not all(normalize(key) in bindings for key in match['required_parameters'])):
                    continue
                rules.append(rule)
            rule = self.choose(rules)
            if rule is None:
                return None
            action, used = rule['action'], set()
            if 'parameter_from_object' in action:
                from .object_arguments import derive
                argument, value_source = derive(context, action, self.config_file, record['id'], normalize(parameter.name))
            elif 'parameter_from' in action:
                key = normalize(action['parameter_from'])
                argument = bindings[key]
                used.add(key)
                value_source = action['parameter_from']
            else:
                argument = Source(action['parameter_literal'], self.config_file, self.config_root, record['id'])
                value_source = self.config_file
            self.log(context, rule, source, parameter.span.start, None, argument.text, value_source)
            return argument, used
        return resolve
