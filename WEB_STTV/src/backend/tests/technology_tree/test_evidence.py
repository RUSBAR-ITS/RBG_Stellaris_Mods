"""Independent examples for functional evidence and its explicit boundaries."""

from copy import deepcopy
import unittest

from sttv.common.errors import BuildError
from sttv.common.json_io import read_json
from sttv.common.paths import PRODUCT_ROOT
from sttv.enrichment.technology_tree import economy, relations, groups
from sttv.enrichment.technology_tree.ast import unlocks
from sttv.enrichment.technology_tree.inputs import Catalog, record_for
from sttv.enrichment.technology_tree.conditions import availability
from sttv.enrichment.technology_tree.representations import prepare
from .support import assignment as a, block as b, value as v, logical, tech, catalog, rules


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.registry=read_json(PRODUCT_ROOT/'config/datasets.json')['datasets']
        self.config={r['id']:r['parameters'] for r in rules()['rules']}
        self.techs=prepare(catalog([tech('a'),tech('b'),tech('c',['a','b'])]),{})

    def objects(self, **definitions):
        data={k:[] for k in self.registry}
        for kind, rows in definitions.items():
            data[kind]=[record_for(kind,'a'*64,f'/items/{i}',row) for i,row in enumerate(rows)]
        return Catalog(data)

    def test_direct_upgrade_shared_requirements_and_or_exclusion(self):
        source=a('old',b(a('prerequisites',b(v('a'),v('shared'))),a('upgrades',b(v('new')))))
        target=a('new',b(a('prerequisites',b(v('c'),v('shared')))))
        objects=self.objects(buildings=[source,target])
        result=relations.upgrades(objects,self.techs,self.config['direct_upgrades'])
        self.assertEqual(result['c'][0]['parent'],'a')
        target['value']['items'][0]['value']=logical('OR',v('c'),v('shared'))
        self.assertFalse(relations.upgrades(self.objects(buildings=[source,target]),self.techs,self.config['direct_upgrades']))

    def test_positive_relations_keep_conditions_and_exclude_negative_and_ai(self):
        provider=a('module',b(a('potential',b(a('has_technology','a')))))
        building=a('detector',b(a('prerequisites',b(v('c'))),a('possible',b(
            a('custom_tooltip',b(a('text','module'),logical('OR',a('has_starbase_module','module'),
                a('starbase_buildable_is_in_queue_before',b(a('first','module'))))))))))
        objects=self.objects(starbase_modules=[provider],starbase_buildings=[building])
        result=relations.direct(objects,self.techs,self.config['direct_relations'])
        self.assertEqual({w['parent'] for w in result['c']},{'a'})
        self.assertTrue(all(w['conditional'] for w in result['c']))
        building['value']['items'][1]=a('possible',b(logical('NOT',a('has_starbase_module','module'))))
        building['value']['items'].append(a('ai_weight',b(a('has_starbase_module','module'))))
        self.assertFalse(relations.direct(self.objects(starbase_modules=[provider],starbase_buildings=[building]),self.techs,self.config['direct_relations']))

    def test_component_effect_sign_and_depth_use_original_prerequisites(self):
        self.techs=prepare(catalog([tech('a'),tech('b',['a']),tech('d'),tech('c',['b','d'])]),{})
        def component(key,owner,amount):
            return a('utility_component_template',b(a('key',key),a('prerequisites',b(v(owner))),a('ship_modifier',b(a('hardening',amount)))))
        old,new=component('old','a',0.01),component('new','c',0.15)
        result=relations.indirect(self.objects(components=[old,new]),self.techs,self.config['indirect_affinity'])
        self.assertEqual(result['c'][0]['parent'],'b')
        self.assertEqual(result['c'][0]['path'],['b','a'])
        new['value']['items'][-1]=a('ship_modifier',b(a('hardening',-0.15)))
        self.assertFalse(relations.indirect(self.objects(components=[old,new]),self.techs,self.config['indirect_affinity']))

    def test_production_bonus_category_job_and_provider(self):
        objects=self.objects(economic_categories=[a('workers',b(a('generate_mult_modifiers',b(v('produces')))))],
            pop_jobs=[a('worker',b(a('resources',b(a('category','workers'),a('produces',b(a('alloys',1)))))))],
            buildings=[a('factory',b(a('prerequisites',b(v('a'))),a('triggered_planet_modifier',b(
                a('potential',b(a('is_nomadic','no'))),a('job_worker_add',1)))))])
        index=economy.production_index(objects,self.config['production_affinity'])
        from decimal import Decimal
        current={**self.techs['c'],'bonuses':{'workers_produces_mult':Decimal('.05')}}
        matches=economy.matches(current,['a','b'],index)
        self.assertEqual(matches[0]['parent'],'a')
        self.assertTrue(matches[0]['conditional'])

    def test_capacity_requires_positive_usage_and_linked_hull(self):
        objects=self.objects(starbase_levels=[a('station',b(a('starbase_capacity_used',1),a('ship_size','hull')))],
            ship_sizes=[a('hull',b(a('prerequisites',b(v('a')))))])
        index=economy.capacity_index(objects,self.config['capacity_affinity'])
        self.assertEqual(index['country_starbase_capacity_add'][0]['owners'],['a'])

    def test_weapon_routes_and_damage_ignore_tooltips_and_conditions(self):
        objects=self.objects(megastructures=[a('gun',b(a('prerequisites',b(v('c'))),a('scripted_action','fire')))],
            scripted_actions=[a('fire',b(a('on_completed','completed')))],
            on_actions=[a('completed',b(a('events',b(v('event.1')))))],
            events=[a('country_event',b(a('id','event.1'),a('immediate',b(a('if',b(
                a('limit',b(a('always','yes'))),a('damage_ship',b(a('amount',3)))))))))])
        cfg=self.config['functional_groups']
        routes=groups.routes(objects,self.techs,cfg['weapon'])
        result=groups.collect(objects,self.techs,cfg,routes)
        self.assertEqual(result['c'][0]['group'],'anti_ship_weaponry')
        effects=b(a('limit',b(a('damage_ship',3))),a('custom_tooltip','damage_ship'))
        self.assertEqual(list(groups.damage(effects,cfg['weapon'])),[])

    def test_unknown_profile_facts_stay_unknown_and_scopes_do_not_leak(self):
        facts={'country':{'is_nomadic':{'yes':False}}}
        self.assertIs(availability({**self.techs['a'],'potential':[b(a('is_nomadic','yes'))]},facts)['value'],False)
        self.assertIsNone(availability({**self.techs['a'],'potential':[b(a('owner',b(a('is_nomadic','yes'))))]},facts)['value'])

    def test_duplicate_used_object_reference_fails(self):
        objects=self.objects(buildings=[a('old',b(a('upgrades',b(v('target'))))),a('target',b()),a('target',b())])
        with self.assertRaises(BuildError):
            relations.upgrades(objects,self.techs,self.config['direct_upgrades'])
