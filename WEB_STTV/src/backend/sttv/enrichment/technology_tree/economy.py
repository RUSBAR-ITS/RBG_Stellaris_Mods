"""Build reusable production/capacity evidence; evaluate only active own bonuses."""

from collections import defaultdict

from .ast import fields, scalar, references, prerequisite, number, numeric_items, unlocks, access


def production_index(catalog, config):
    modifiers, jobs, providers = {}, defaultdict(list), defaultdict(list)
    for category in catalog.rows('economic_categories'):
        for field, suffix in config['generation_fields'].items():
            if any('produces' in references(n) for n in fields(category['body'], field)):
                modifier = config['modifier_pattern'].format(category=category['id'], suffix=suffix)
                modifiers[modifier] = category
    job_ids = {}
    for job in catalog.rows('pop_jobs'):
        job_ids[config['job_modifier_pattern'].format(job=job['id'])] = job['id']
        for block in fields(job['body'], 'resources'):
            if fields(block, 'produces'):
                jobs[scalar(block, 'category')].append((job, block))
    for obj in catalog.rows(config['provider_kind']):
        for field in config['provider_blocks']:
            for block in fields(obj['body'], field):
                multiplier = number(scalar(block, 'multiplier'))
                if multiplier is not None and multiplier <= 0:
                    continue
                for modifier, value in numeric_items(block):
                    if modifier in job_ids and value > 0:
                        providers[job_ids[modifier]].append((obj, field, block))
    result = defaultdict(list)
    for modifier, category in modifiers.items():
        for job, resources in jobs[category['id']]:
            for obj, field, block in providers[job['id']]:
                owners = unlocks(obj)
                if owners:
                    catalog.resolve('economic_categories', category['id'])
                    catalog.resolve('pop_jobs', job['id'])
                    catalog.resolve(config['provider_kind'], obj['id'])
                    result[modifier].append({'owners': sorted(owners), 'category': category['source'],
                        'job': job['source'], 'resources': resources, 'provider': obj['source'],
                        'provider_field': field, 'provider_block': block, 'access': access(obj), 'conditional': True})
    return result


def capacity_index(catalog, config):
    result = defaultdict(list)
    for mapping in config['mappings']:
        for obj in catalog.rows(mapping['kind']):
            usage = number(scalar(obj['body'], mapping['usage_field']))
            if usage is None or usage <= 0:
                continue
            target_id = scalar(obj['body'], mapping['linked_field'])
            target = catalog.resolve(mapping['linked_kind'], target_id)
            if not target:
                continue
            catalog.resolve(mapping['kind'], obj['id'])
            owners = references(prerequisite(target['body']))
            result[mapping['modifier']].append({'owners': sorted(owners), 'object': obj['source'],
                'target': target['source'], 'mapping': mapping, 'usage': str(usage),
                'access': access(target), 'conditional': True})
    return result


def matches(technology, candidates, index):
    result = []
    for modifier, value in technology['bonuses'].items():
        if value <= 0:
            continue
        for witness in index.get(modifier, []):
            for parent in sorted(set(witness['owners']) & set(candidates)):
                result.append({**witness, 'parent': parent, 'modifier': modifier, 'value': str(value),
                               'technology': technology['source'], 'variant': technology['variant']})
    return result
