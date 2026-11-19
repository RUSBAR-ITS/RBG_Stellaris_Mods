"""Closed parameter contracts for each supported relationship handler."""

from .helpers import BOOL, TEXT, array, obj, mapping, union
from sttv.common.datasets import KINDS

KIND = {'enum': list(KINDS)}
STRINGS = array(TEXT, uniqueItems=True)


def parameters():
    return {
        **{key: obj({}) for key in ('normalized_id', 'same_area', 'same_category', 'mandatory',
                                   'same_potential', 'standard_empire', 'highest_tier')},
        'direct_upgrades': obj({'mappings': array(obj({'kind': KIND, 'field': TEXT,
                                                     'direction': {'enum': ['forward', 'reverse']}}), minItems=1)}),
        'direct_relations': obj({'kinds': array(KIND, uniqueItems=True), 'sections': STRINGS,
            'relations': mapping(KIND), 'operators': STRINGS,
            'queue': obj({'command': TEXT, 'field': TEXT, 'kinds': array(KIND, uniqueItems=True)})}),
        'indirect_affinity': obj({'depth': {'type': 'integer', 'minimum': 1}, 'kind': KIND,
                                  'modifier_block': TEXT}),
        'production_affinity': obj({'generation_fields': mapping(TEXT), 'modifier_pattern': TEXT,
            'job_modifier_pattern': TEXT, 'provider_kind': KIND, 'provider_blocks': STRINGS}),
        'capacity_affinity': obj({'mappings': array(obj({'modifier': TEXT, 'kind': KIND,
            'usage_field': TEXT, 'linked_field': TEXT, 'linked_kind': KIND}), minItems=1)}),
        'functional_groups': obj({
            'ship': obj({'group': TEXT, 'kind': KIND, 'speed_field': TEXT, 'roles_field': TEXT, 'roles': STRINGS}),
            'terraform': obj({'group': TEXT, 'kind': KIND, 'type': TEXT, 'from_field': TEXT,
                              'to_field': TEXT, 'condition_field': TEXT, 'predicate': TEXT}),
            'weapon': obj({'group': TEXT, 'kinds': array(KIND, uniqueItems=True), 'component_kind': KIND,
                'component_type': TEXT, 'action_field': TEXT, 'action_kind': KIND, 'completion_field': TEXT,
                'hook_kind': KIND, 'events_field': TEXT, 'event_kind': KIND,
                'effect_field': TEXT, 'damage_command': TEXT, 'excluded_effect_sections': STRINGS})}),
    }


def schema():
    declarations = parameters()
    reference = obj({'definition_ref': TEXT})
    entry = union(*(obj({'id': {'const': key}, 'enabled': BOOL, 'parameters': union(spec, reference)})
                    for key, spec in declarations.items()))
    return obj({'format': {'const': 'sttv.technology_tree_rules'}, 'format_version': {'const': 1},
                'rules': array(entry, minItems=1), 'definitions': mapping(union(*declarations.values()))})
