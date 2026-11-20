"""Group observed syntax for research; this is not a runtime condition registry."""
import argparse
import json
from pathlib import Path

FAMILIES = {
    'empire_identity': 'has_authority has_ethic has_origin has_civic has_valid_civic is_nomadic is_country_type is_primitive is_ai has_ai_personality',
    'species_population_traits': 'is_archetype has_trait is_sapient is_same_species is_pop_category count_owned_pop_amount',
    'ship_category_and_dna': 'uses_ship_category has_dna',
    'research': 'has_technology can_research_technology',
    'development': 'has_ascension_perk has_tradition num_ascension_perk_slots has_crisis_level has_menace_perk',
    'policies_and_rights': 'has_policy_flag has_citizenship_type has_slavery_type',
    'leaders_and_council': 'has_base_skill is_councilor is_councilor_type is_ruler',
    'colonies_and_systems': 'num_owned_planets is_planet_class uses_district_set is_inside_nebula',
    'infrastructure': 'has_district num_districts num_zones num_buildings has_starbase_size count_starbase_sizes has_megastructure disabled in_construction',
    'resources_and_economy': 'has_resource resource_expenses_compare has_deposit has_deposit_for',
    'country_history': 'has_country_flag has_modifier has_relic',
    'exploration': 'has_seen_any_bypass owns_any_bypass num_cosmic_storms_encountered is_astral_scar count_archaeological_site is_site_completed',
    'situations': 'is_situation_type',
    'federation': 'has_federation has_federation_law has_federation_perk',
    'subject_agreements': 'is_subject has_active_specialization',
    'contacts': 'has_communications num_communications perc_communications_with_playable',
    'galactic_community': 'is_galactic_community_member is_active_resolution',
    'external_conditions': 'host_has_dlc has_global_flag days_passed years_passed mid_game_years_passed',
    'context_and_collections': 'any_agreement any_country any_member any_neighbor_country any_owned_leader any_owned_nonprimary_starbase any_owned_planet any_owned_pop_group any_owned_species any_planet_within_border any_relation any_situation any_system_megastructure any_system_planet any_system_within_border federation founder_species owner owner_species prev solar_system space_owner? species this exists is_same_value',
    'structure_and_operands': 'add always amount base calc_true_if complex_trigger_modifier count country else factor hidden_trigger if limit mode modifier mult parameters resource ship_category starbase_size trigger trigger_scope type value',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Directory produced by inventory.py')
    output = parser.parse_args().output
    inventory = json.loads((output / 'inventory.json').read_text(encoding='utf-8'))
    observations = json.loads((output / 'observations.json').read_text(encoding='utf-8'))
    keys = {g['key'] for g in inventory['groups']}
    classified = [key for text in FAMILIES.values() for key in text.split()]
    assert len(classified) == len(set(classified)), 'Duplicate classification'
    assert keys == set(classified), (keys - set(classified), set(classified) - keys)
    results = []
    for family, text in FAMILIES.items():
        observed = [o for o in observations if o['key'] in text.split()]
        results.append({'family': family, 'keys': text.split(),
                        'technologies': len({o['technology'] for o in observed}),
                        'observations': len(observed),
                        'section_technologies': {
                            section: len({o['technology'] for o in observed if o['section'] == section})
                            for section in sorted({o['section'] for o in observed})}})
    references = [o for o in observations if isinstance(o['value'], str)
                  and o['value'].startswith(('trigger:', 'value:'))]
    result = {'snapshot_revision': inventory['snapshot_revision'], 'unique_assignment_keys': len(keys),
              'assignment_shapes': inventory['assignment_shapes'], 'observations': len(observations),
              'scope': 'Technology appearance fields and swap triggers; not AI selection or effect bodies.',
              'note': 'Syntactic grouping only. Traits may belong to leaders or species; scopes and logical trees remain required.',
              'families': results, 'dynamic_scalar_references': references}
    (output / 'classified_inventory.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('families', 'dynamic_scalar_references')}, indent=2))
    print('All observed keys classified exactly once; dynamic scalar references:', len(references))


if __name__ == '__main__':
    main()
