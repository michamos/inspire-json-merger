# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
"""
This test check the correctness of the merger rules on all the schema's keys.
Important: in order to check the schema's coverage, please add the `cover`
decorator to each test, referring to the schema's key under test.
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import decorator
import pytest
from inspire_schemas.api import load_schema, validate

from inspire_json_merger.inspire_json_merger import inspire_json_merge
from inspire_json_merger.utils.utils import sort_conflicts

# list of all the schema's keys tested
COVERED_SCHEMA_KEYS = []


def cover(key):
    # collect the schema's key verified by a test
    def tag(func):
        def wrapper(func, *args, **kwargs):
            COVERED_SCHEMA_KEYS.append(key)
            return func(*args, **kwargs)
        return decorator.decorator(wrapper, func)
    return tag


def add_arxiv_source(*json_obj):
    # This function add a source object to the given json file list
    for obj in json_obj:
        source = {
            'acquisition_source': {
                'source': 'arxiv'
            }
        }
        obj.update(source)
    return json_obj if len(json_obj) > 1 else json_obj[0]


def validate_subschema(obj):
    if len(obj.keys()) > 1:
        del obj['acquisition_source']
    schema = load_schema('hep')
    key = list(obj.keys())[0]  # python 3 compatibility
    sub_schema = schema['properties'].get(key)
    assert validate(obj.get(key), sub_schema) is None


@cover('$schema')
def test_merging_schema_field():
    root = {'$schema': 'http://inspire-nightly.cern.ch/schemas/records/hep.json'}  # record_id: 1308464
    head = {'$schema': 'http://qa.inspirehep.net/schemas/records/hep.json'}
    update = {'$schema': 'http://inspirehep.net/schemas/records/hep.json'}

    expected_merged = {'$schema': 'http://qa.inspirehep.net/schemas/records/hep.json'}
    expected_conflict = [['SET_FIELD', ['$schema'], 'http://inspirehep.net/schemas/records/hep.json']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('_collections')
def test_merging_collections_field():
    root = {'_collections': ['BABAR Analysis Documents']}
    head = {'_collections': ['BABAR Analysis Documents', 'CDF Internal Notes']}
    update = {'_collections': ['BABAR Analysis Documents', 'CDF Notes']}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('_desy_bookkeeping')
def test_merging_desy_bookkeeping_field():
    root = {
        '_desy_bookkeeping': [
            {
                'date': '2014-07-31',
                'expert': 'B',
                'status': 'abs'
            }, {
                'date': '2014-08-06',
                'expert': 'B',
                'status': 'printed'
            }, {
                'date': '2015-01-02',
                'status': 'final'
            }
        ]
    }
    # record_id: 1308464
    head = {
        '_desy_bookkeeping': [
            {
                'date': '2014-07-31',
                'expert': 'B',
                'status': 'printed2'
            }, {
                'date': '2014-08-06',
                'expert': 'B',
                'status': 'printed'
            }, {
                'date': '2015-01-02',
                'expert': 'B',
                'status': 'final'
            }
        ]
    }
    update = {
        '_desy_bookkeeping': [
            {
                'date': '2014-07-31',
                'status': 'abs'
            }, {
                'date': '2014-08-06',
                'expert': 'B',
                'status': 'printed'
            }, {
                'date': '2015-01-03',
                'status': 'final'
            }
        ]
    }

    expected_merged = {
        '_desy_bookkeeping': [
            {
                'date': '2014-07-31',
                'status': 'printed2'
            }, {
                'date': '2014-08-06',
                'expert': 'B',
                'status': 'printed'
            }, {
                'date': '2015-01-02',
                'expert': 'B',
                'status': 'final'
            }

        ]
    }
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('_export_to')
def test_merging_export_to_field():
    root = {
        '_export_to': {
            'CDS': False,
            'HAL': False
        }
    }
    # record_id: 432169 & 717606
    head = {
        '_export_to': {
            'CDS': True,
            'HAL': False
        }
    }
    update = {
        '_export_to': {
            'CDS': False,
            'HAL': False
        }
    }

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('_fft')
def test_merging_fft_field():
    root = {
        '_fft': [
            {
                'creation_datetime': '2014-07-28T23:15:16',
                'description': 'Fulltext',
                'filename': 'fermilab-thesis-2014-17',
                'format': '.pdf',
                'path': '/opt/cds-invenio/var/data/files/g95/1902084/content.pdf;1',
                'type': 'Main',
                'version': 1
            }
        ]
    }
    # record_id: 1308464
    head = {
        '_fft': [
            {
                'creation_datetime': '2014-07-28T23:15:16',
                'description': 'Fulltext',
                'filename': 'fermilab-thesis-2014-18',
                'format': '.pdf',
                'path': '/opt/cds-invenio/var/data/files/g95/1902084/content.pdf;1',
                'type': 'Main',
                'version': 1
            }
        ]
    }
    update = {
        '_fft': [
            {
                'creation_datetime': '2014-07-28T23:15:16',
                'description': 'Fulltext',
                'filename': 'fermilab-thesis-2014-19',
                'format': '.pdf',
                'path': '/opt/cds-invenio/var/data/files/g95/1902084/content.pdf;1',
                'type': 'Main',
                'version': 1
            }
        ]
    }

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['_fft', 0, 'filename'], 'fermilab-thesis-2014-19']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('_files')
def test_merging_files_field():
    root = {
        '_files': [
            {
                'bucket': 'foo',
                'checksum': 'bar',
                'key': 'baz',
                'previewer': 'spam',
                'size': 1,
                'type': 'eggs',
                'version_id': 'version'
            }
        ]
    }
    # record_id: not found 9/05/2017
    head = {
        '_files': [
            {
                'bucket': 'foo1',
                'checksum': 'bar',
                'key': 'baz',
                'previewer': 'spam',
                'size': 1,
                'type': 'eggs',
                'version_id': 'version'
            }
        ]
    }
    update = {
        '_files': [
            {
                'bucket': 'foo2',
                'checksum': 'bar',
                'key': 'baz',
                'previewer': 'spam',
                'size': 1,
                'type': 'eggs',
                'version_id': 'version'
            }, {
                'bucket': 'foo2',
                'checksum': 'bar',
                'key': 'baz',
                'previewer': 'spam',
                'size': 1,
                'type': 'eggs',
                'version_id': 'second version'
            }
        ]
    }

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['_files', 0, 'bucket'], 'foo1']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('_private_notes')
def test_merging_private_notes_field():
    root = {
        '_private_notes': [
            {
                'source': 'SPIRES-HIDDEN',
                'value': 'Update from APS OAI Harvest'
            }
        ]
    }
    # record_id: 905854
    head = {
        '_private_notes': [
            {
                'source': 'SPIRES-HIDDEN',
                'value': 'Update from APS OAI Harvest foo'
            }
        ]
    }
    update = {
        '_private_notes': [
            {
                'source': 'SPIRES-HIDDEN',
                'value': 'Update from APS OAI Harvest bar'
            }, {
                'source': 'SPIRES',
                'value': 'Added by ..HEP.ADD.TO.HEP from APS OAI Harvest'
            }
        ]
    }

    expected_merged = {
        '_private_notes': [
            {
                'source': 'SPIRES-HIDDEN',
                'value': 'Update from APS OAI Harvest foo'
            }
        ]
    }
    expected_conflict = [['SET_FIELD', ['_private_notes', 0, 'value'], 'Update from APS OAI Harvest bar']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('abstracts')
def test_merging_abstracts_field():
    root = {
        'abstracts': [
            {
                'value': 'We investigate the structure of a proto-neutron star with '
                         'trapped neutrinos by us ing quantum hadrodynamics.',
                'source': 'arxiv'
            }
        ]
    }
    # record_id: 905854
    head = {
        'abstracts': [
            {
                'value': 'We investigate the structure of a proto-neutron star with '
                         'trapped neutrinos by us ing quantum hadrodynamics. bar',
                'source': 'arxiv'
            }
        ]
    }
    update = {
        'abstracts': [
            {
                'value': 'We investigate the structure of a proto-neutron star with '
                         'trapped neutrinos by us ing quantum hadrodynamics. foo',
                'source': 'arxiv'
            }
        ]
    }

    expected_merged = update
    expected_conflict = [
        [
            'SET_FIELD',
            ['abstracts', 0, 'value'],
            'We investigate the structure of a proto-neutron star with '
            'trapped neutrinos by us ing quantum hadrodynamics. bar'
        ]
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('accelerator_experiments')
def test_merging_accelerator_experiments_field():
    root = {
        'accelerator_experiments': [
            {
                'curated_relation': True,
                'experiment': 'FNAL-E-0830',
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/experiments/1110316'
                }
            }
        ],
    }
    # record_id: 982117
    head = {
        'accelerator_experiments': [
            {
                'curated_relation': True,
                'experiment': 'FNAL-E-08302',
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/experiments/1110316'
                }
            }, {
                'curated_relation': True,
                'experiment': 'FNAL-E-08301',
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/experiments/1110317'
                }
            }
        ],
    }
    update = {
        'accelerator_experiments': [
            {
                'curated_relation': True,
                'experiment': 'FNAL-E-08301',
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/experiments/1110316'
                }
            }
        ],
    }

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('acquisition_source')
def test_merging_acquisition_source_field():
    root = {
        'acquisition_source': {
            'method': 'batchuploade',
            'source': 'ejl'
        }
    }
    # record_id: 1517095
    head = {
        'acquisition_source': {
            'method': 'batchuploadeR',
            'source': 'ejl'
        }
    }
    update = {
        'acquisition_source': {
            'method': 'batchuploader',
            'source': 'ejl'
        }
    }

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    assert merged is not {}

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('arxiv_eprints')
def test_merging_arxiv_eprints_field():
    root = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math.CA',
                ],
                'value': '1703.04817'
            }
        ]
    }
    # record id: There are not examples of this kind of
    # field in Inspire. We created some examples with
    # the real date inside inspire.
    head = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math.CA',
                ],
                'value': '1703.04817'
            }
        ]
    }
    update = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math.CA',
                ],
                'value': '1703.04818'
            }
        ]
    }

    expected_merged = {
        'arxiv_eprints': [
            {
                'categories': [
                    'math.CA',
                ],
                'value': '1703.04817'
            }, {
                'categories': [
                    'math.CA',
                ],
                'value': '1703.04818'
            }
        ]
    }
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_authors_field():
    root = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756b',
                'full_name': 'Cox, Brian F.'
            }
        ]
    }
    head = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',
                'full_name': 'Cox, Brian'
            }
        ]
    }
    update = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756d',
                'full_name': 'Cox, Brian E.'
            }
        ]
    }

    expected_merged = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756d',
                'full_name': 'Cox, Brian'
            }
        ]
    }
    expected_conflict = [
        ['SET_FIELD', ['authors', 0, 'uuid'], '160b80bf-7553-47f0-b40b-327e28e7756c'],
        ['SET_FIELD', ['authors', 0, 'full_name'], 'Cox, Brian E.']
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_affiliations_field_per_ref():
    root = {}
    head = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756d',
                'full_name': u'ႷႷႷႷႷႷႷႷ',
                'affiliations': [
                    {
                        'value': 'Illinois Urbana',
                        'record': {
                            '$ref': 'http://newlabs.inspirehep.net/api/institutions/902867'
                        }
                    }
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',  # last digit changed
                'full_name': u'ႷႷႷႷႷႷႷႷ',
                'affiliations': [
                    {
                        'value': 'Illinois U., Urbana',
                        'record': {
                            '$ref': 'http://newlabs.inspirehep.net/api/institutions/902867'
                        }
                    }
                ]
            }
        ]
    }

    expected_merged = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',  # update uuid
                'full_name': u'ႷႷႷႷႷႷႷႷ',
                'affiliations': [
                    {
                        'value': 'Illinois Urbana',
                        'record': {
                            '$ref': 'http://newlabs.inspirehep.net/api/institutions/902867'
                        }
                    }
                ]
            }
        ]
    }
    expected_conflict = [
        ['SET_FIELD', ['authors', 0, 'uuid'], '160b80bf-7553-47f0-b40b-327e28e7756d'],
        ['SET_FIELD', ['authors', 0, 'affiliations', 0, 'value'], 'Illinois U., Urbana'],
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_affiliations_field_per_value():
    root = {}
    head = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756d',
                'full_name': 'Cox, Brian',
                'affiliations': [
                    {
                        'value': 'Illinois Urbana',
                        'record': {
                            '$ref': 'http://newlabs.inspirehep.net/api/institutions/902867'
                        }
                    }
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',  # last digit changed
                'full_name': 'Cox, Brian E.',
                'affiliations': [
                    {
                        'value': 'Illinois Urbana',
                        'record': {
                            '$ref': 'http://newlabs.inspirehep.net/api/institutions/902866'
                        }
                    }
                ]
            }
        ]
    }

    expected_merged = {
        'authors': [
            {
                'uuid': '160b80bf-7553-47f0-b40b-327e28e7756c',  # update uuid
                'full_name': 'Cox, Brian',
                'affiliations': [
                    {
                        'value': 'Illinois Urbana',
                        'record': {
                            '$ref': 'http://newlabs.inspirehep.net/api/institutions/902867'
                        }
                    }
                ]
            }
        ]
    }
    expected_conflict = [
        ['SET_FIELD', ['authors', 0, 'uuid'], '160b80bf-7553-47f0-b40b-327e28e7756d'],
        ['SET_FIELD', ['authors', 0, 'full_name'], 'Cox, Brian E.'],
        [
            'SET_FIELD',
            ['authors', 0, 'affiliations', 0, 'record', '$ref'],
            'http://newlabs.inspirehep.net/api/institutions/902866'
        ]
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_alternative_names_field():
    root = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'alternative_names': [
                    'K Pitts',
                    'K T Pitts',
                    'Pitts Kevin',
                    'Pitts Kevin T',
                    'Pitts T',
                    'Pitts, K',
                    'Pitts, K T',
                    'Pitts, Kevin',
                    'Pitts, Kevin T',
                    'Pitts, T',
                ]
            }
        ]
    }
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'alternative_names': [
                    'K Pitts',
                    'K T Pitts',
                    'Kevin Pitts',
                    'Kevin T Pitts',
                    'Pitts',
                    'Pitts K',
                    'Pitts K T',
                    'Pitts Kevin',
                    'Pitts Kevin T',
                    'Pitts T',
                    'Pitts, K',
                    'Pitts, K T',
                    'Pitts, Kevin',
                    'Pitts, Kevin T',
                    'Pitts, T'
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'alternative_names': [
                    'K Pitts',
                    'K T Pitts',
                    'Kevin Pitts',
                    'Pitts',
                    'Pitts K',
                    'Pitts K T',
                    'Pitts Kevin',
                    'Pitts Kevin T',
                    'Pitts T',
                    'Pitts, K',
                    'Pitts, K T',
                    'Pitts, Kevin',
                    'Pitts, Kevin T',
                    'Pitts, T',
                    'T Pitts'
                ]
            }
        ]
    }

    expected_merged = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'alternative_names': [
                    'K Pitts',
                    'K T Pitts',
                    'Kevin Pitts',
                    'Kevin T Pitts',
                    'Pitts',
                    'Pitts K',
                    'Pitts K T',
                    'Pitts Kevin',
                    'Pitts Kevin T',
                    'Pitts T',
                    'Pitts, K',
                    'Pitts, K T',
                    'Pitts, Kevin',
                    'Pitts, Kevin T',
                    'Pitts, T',
                    'T Pitts'
                ]
            }
        ]
    }
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_credit_roles_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'credit_roles': [
                    'Conceptualization',
                    'Data curation',
                    'Formal analysis',
                    'Funding acquisition',
                    'Investigation',
                    'Methodology',
                    'Project administration',
                ]
            }
        ]
    }

    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'credit_roles': [
                    'Resources',
                    'Software',
                    'Supervision',
                    'Validation',
                    'Visualization',
                    'Writing - original draft',
                    'Writing - review & editing'
                ]
            }
        ]
    }

    expected_merged = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'credit_roles': [
                    'Conceptualization',
                    'Data curation',
                    'Formal analysis',
                    'Funding acquisition',
                    'Investigation',
                    'Methodology',
                    'Project administration',
                    'Resources',
                    'Software',
                    'Supervision',
                    'Validation',
                    'Visualization',
                    'Writing - original draft',
                    'Writing - review & editing'
                ]
            }
        ]
    }
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_curated_relation_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'curated_relation': False
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'curated_relation': True
            }
        ]
    }

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['authors', 0, 'curated_relation'], True]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_emails_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'emails': [
                    'pitts.kevin@gmail.com',
                    'pitts.kevin@mit.edu'
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T.',
                'emails': [
                    'pitts.kevin@gmail.com',
                    'kevin.pitts@gmail.com',
                    'kevin.pitts@mit.edu'
                ]
            }
        ]
    }

    expected_merged = update
    expected_conflict = [['ADD_BACK_TO_HEAD', ['authors', 0, 'emails'], 'pitts.kevin@mit.edu']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_full_name_field():
    root = {
        'authors': [
            {
                'full_name': 'Pitts Kevin',
            }
        ]
    }
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin',
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
            }
        ]
    }

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['authors', 0, 'full_name'], 'Pitts, Kevin T']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_ids_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'ids': [
                    {
                        'value': 'HEPNAMES-2100',
                        'schema': 'SPIRES'
                    }
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'ids': [
                    {
                        'value': 'HEPNAMES-2101',
                        'schema': 'SPIRES'
                    }
                ]
            }
        ]
    }

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['authors', 0, 'ids', 0, 'value'], 'HEPNAMES-2101']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_inspire_roles_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'inspire_roles': [
                    'editor'
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'inspire_roles': [
                    'supervisor'
                ]
            }
        ]
    }

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_raw_affiliations_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'raw_affiliations': [
                    {
                        'source': 'arxiv',
                        'value': 'Department of Physics, Indiana University, Bloomington, IN 47405, USA'
                    }
                ]
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'raw_affiliations': [
                    {
                        'source': 'arxiv',
                        'value': 'Department of Physics, Indiana University, Bloomington, IN 47405, US'
                    }
                ]
            }
        ]
    }

    expected_merged = update
    expected_conflict = [
        [
            'SET_FIELD',
            ['authors', 0, 'raw_affiliations', 0, 'value'],
            'Department of Physics, Indiana University, Bloomington, IN 47405, USA'
        ]
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_record_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/169636'
                }
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/169637'
                }
            }
        ]
    }

    expected_merged = head
    expected_conflict = [
        [
            'SET_FIELD',
            ['authors', 0, 'record', '$ref'],
            'http://newlabs.inspirehep.net/api/literature/169637'
        ]
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_signature_block_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'signature_block': 'Mister Pitts, Kevin Travis',
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'signature_block': 'Mr. Pitts, Kevin Travis',
            }
        ]
    }

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['authors', 0, 'signature_block'], 'Mister Pitts, Kevin Travis']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('authors')
def test_merging_uuid_field():
    root = {}
    head = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'uuid': 'a2f28e91-a2f1-4466-88d7-14f3bba99a9a',
            }
        ]
    }
    update = {
        'authors': [
            {
                'full_name': 'Pitts, Kevin T',
                'uuid': 'a2f28e91-a2f1-4466-88d7-14f3bba99a9c',
            }
        ]
    }

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['authors', 0, 'uuid'], 'a2f28e91-a2f1-4466-88d7-14f3bba99a9a']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('book_series')
def test_merging_book_series_field():
    root = {
        'book_series': [
            {
                'title': 'IEEE Nucl.Sci.Symp.Conf.Rec.',
                'volume': 'bar'
            }
        ]
    }
    # record_id: 1212189
    head = {
        'book_series': [
            {
                'title': 'IEEE Nucl.Sci.Symp.Conf.Rec.',
                'volume': 'baz'
            }, {
                'title': 'CMS Web-Based Monitoring',
                'volume': 'spam'
            }
        ]
    }
    update = {
        'book_series': [
            {
                'title': 'IEEE Nucl.Sci.Symp.Conf.Rec.',
                'volume': 'spam'
            }, {
                'title': 'Proposal for Web Based Monitoring and Database Browsing"',
                'volume': 'spam'
            }
        ]
    }

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['book_series', 0, 'volume'], 'spam']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('citeable')
def test_merging_citeable_field():
    root = {'citeable': False}
    head = {'citeable': False}
    update = {'citeable': True}

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('collaborations')
def test_merging_collaborations_field():
    root = {
        'collaborations': [
            {
                'record':
                    {
                        '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                    },
                'value': 'LHCb'
            }
        ]
    }
    # record_id: 1517390
    head = {
        'collaborations': [
            {
                'record':
                    {
                        '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                    },
                'value': 'ATLAS'
            }, {
                'record':
                    {
                        '$ref': 'http://newlabs.inspirehep.net/api/literature/684122'
                    },
                'value': 'CMS'
            }
        ]
    }
    update = {
        'collaborations': [
            {
                'record':
                    {
                        '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                    },
                'value': 'ALICE'
            }
        ]
    }

    expected_merged = {
        'collaborations': [
            {
                'record':
                    {
                        '$ref': 'http://newlabs.inspirehep.net/api/literature/684121'
                    },
                'value': 'ALICE'
            }, {
                'record':
                    {
                        '$ref': 'http://newlabs.inspirehep.net/api/literature/684122'
                    },
                'value': 'CMS'
            }
        ]
    }
    expected_conflict = [['SET_FIELD', ['collaborations', 0, 'value'], 'ATLAS']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('control_number')
def test_merging_control_number_field():
    root = {'control_number': 963517}
    head = {'control_number': 963518}
    update = {'control_number': 963519}
    # record_id:

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['control_number'], 963519]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('copyright')
def test_merging_copyright_field():
    root = {
        'copyright': [
            {
                'holder': 'Elsevier',
                'material': 'preprint',
                'statement': 'Copyright @ unknown. Published by Elsevier B.V.',
                'url': 'https://www.elsevier.com/about/our-business/policies/copyright',
                'year': 2011
            }
        ]
    }
    # record_id: 963517
    head = {
        'copyright': [
            {
                'holder': 'Elsevier',
                'material': 'preprint',
                'statement': 'Copyright @ unknown. Published by Elsevier B.V.',
                'url': 'https://www.elsevier.com/about/our-business/policies/copyright',
                'year': 2011
            }
        ]
    }
    update = {
        'copyright': [
            {
                'holder': 'elsevier',
                'material': 'preprint',
                'statement': 'Copyright @ unknown. Published by Elsevier B.V.',
                'url': 'https://www.elsevier.com/about/our-business/policies/copyright',
                'year': 2011
            }
        ]
    }
    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('core')
def test_merging_core_field():
    root = {'core': False}
    head = {'core': False}
    update = {'core': True}

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('corporate_author')
def test_merging_corporate_author_field():
    root = {
        'corporate_author': [
            'The LHCb Collaboration'
        ]
    }
    # record_id: 1517390
    head = {
        'corporate_author': [
            'The LHCb Collaboration',
            'CMS Collaboration'
        ]
    }
    update = {
        'corporate_author': [
            'CMS Collaboration'
        ]
    }

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('deleted')
def test_merging_deleted_field():
    root = {'deleted': False}
    head = {'deleted': False}
    update = {'deleted': True}

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('deleted_records')
def test_merging_deleted_records_field():
    root = {
        'deleted_records': [
            {
                '$ref': 'http://newlabs.inspirehep.net/api/record/980409'
            }
        ]
    }
    # record_id: 963741
    head = {

        'deleted_records': [
            {
                '$ref': 'http://newlabs.inspirehep.net/api/record/980410'
            }
        ]
    }
    update = {
        'deleted_records': [
            {
                '$ref': 'http://newlabs.inspirehep.net/api/record/980419'
            }
        ]
    }

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('document_type')
def test_merging_document_type():
    root = {'document_type': ['thesis']}
    head = {'document_type': ['paper']}
    update = {'document_type': ['article']}

    expected_merged = update  # since the list rule is 'Keep update'

    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('document_type')
def test_merging_document_type_head_equals_to_root():
    root = {'document_type': ['thesis']}
    head = {'document_type': ['thesis']}
    update = {'document_type': ['article']}

    expected_merged = update
    # No expected conflict, since update is legally overwriting an old info
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('document_type')
def test_merging_document_type_update_equals_to_root():
    root = {'document_type': ['thesis']}
    head = {'document_type': ['article']}
    update = {'document_type': ['thesis']}

    expected_merged = update

    # No expected conflict, since update is legally overwriting an old info
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('dois')
def test_merging_dois_field():
    root = {
        'dois': [
            {
                'material': 'preprint',
                'value': '10.1023/A:1026654312961'
            }
        ]
    }
    head = {
        'dois': [
            {
                'material': 'preprint',
                'source': 'nowhere',
                'value': '10.1023/A:1026654312961'
            }
        ]
    }
    update = {
        'dois': [
            {
                'material': 'publication',
                'value': '10.1023/A:1026654312961'
            }
        ]
    }

    expected_merged = {
        'dois': [
            {
                'material': 'publication',
                'source': 'nowhere',
                'value': '10.1023/A:1026654312961'
            }
        ]
    }
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('editions')
def test_merging_editions_field():
    root = {'editions': ['edition1']}
    head = {'editions': ['editionA']}
    update = {'editions': ['edition2']}

    expected_merged = {'editions': ['editionA', 'edition2']}
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('energy_ranges')
def test_merging_energy_ranges_field():
    root = {'energy_ranges': ['0-3 GeV']}
    head = {'energy_ranges': ['3-10 GeV']}
    update = {'energy_ranges': ['3-10 GeV']}

    expected_merged = update  # just update the record with newcoming info
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('external_system_identifiers')
def test_merging_external_system_identifiers_field():
    root = {
        'external_system_identifiers': [
            {
                'schema': 'DESY',
                'value': 'DA14-kp45b'
            }, {
                'schema': 'OSTI',
                'value': '1156543'
            }
        ]
    }  # record: 1308464
    head = {
        'external_system_identifiers': [
            {
                'schema': 'DESY',
                'value': 'DA14-kp45bAAA'
            }, {
                'schema': 'OSTII',
                'value': '1156543'
            }
        ]
    }
    update = {
        'external_system_identifiers': [
            {
                'schema': 'DESY',
                'value': 'DA14-kp45bBBB'
            }, {
                'schema': 'OSTI',
                'value': '115654323'
            }
        ]
    }

    expected_merged = update
    # since `DESY` has been curated, we don't want to lose it
    # so it appears in the conflicts
    expected_conflict = [
                            [
                                'SET_FIELD',
                                ['external_system_identifiers', 0, 'value'],
                                'DA14-kp45bAAA'
                            ]
                        ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('funding_info')
def test_merging_funding_info_field():

    root = {
        'funding_info': [
            {
                'grant_number': '317089',
                'project_number': 'FP7-PEOPLE-2012-ITN'
            }
        ]
    }  # derived from record: 1508011
    head = {
        'funding_info': [
            {
                'agency': 'GATIS, Gauge Theory as an Integrable System foo',
                'grant_number': '317089',
                'project_number': 'FP7-PEOPLE-2012-ITN'
            }
        ]
    }
    update = {
        'funding_info': [
            {
                'agency': 'GATIS, Gauge Theory as foo Integrable System',
                'grant_number': '317089',
                'project_number': 'FP7-PEOPLE-2013-ITN'
            }
        ]
    }

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('imprints')
def test_merging_imprints_field():
    root = {
        'imprints': [
            {
                'date': '2017',
                'place': 'Oxford',
                'publisher': 'Oxford Univ. Press'
            }
        ]
    }  # record: 1593157
    head = {
        'imprints': [
            {
                'date': '2017',
                'place': 'Oxford',
                'publisher': 'Oxford University'
            }
        ]
    }
    update = {
        'imprints': [
            {
                'date': '2018',
                'place': 'Oxford',
                'publisher': 'Oxford Univ. foo bar'
            }
        ]
    }

    expected_merged = update
    # here, normally I would expect a conflict, but since the strategy relies
    # on the `publisher` field, for the merger they are two different objects
    # so the head is directly removed, loosing eventually curated info
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('inspire_categories')
def test_merging_inspire_categories_field():
    root = {'inspire_categories': [
        {
            'source': 'INSPIRE',
            'term':   'Theory-HEP'
        }
    ]}
    head = {'inspire_categories': [
        {
            'source': 'curator',
            'term':   'Theory-HEP'
        }, {
            'source': 'curator',
            'term': 'Theory-Nucl'
        }
    ]}
    update = {'inspire_categories': [
        {
            'source': 'arxiv',
            'term':   'Computing'
        }, {
            'source': 'arxiv',
            'term': 'Other'
        }
    ]}

    expected_merged = {'inspire_categories': [
        {
            'source': 'arxiv',
            'term':   'Computing'
        }, {
            'source': 'arxiv',
            'term': 'Other'
        }, {
            'source': 'curator',
            'term':   'Theory-HEP'
        }, {
            'source': 'curator',
            'term':   'Theory-Nucl'
        },
    ]}
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('isbns')
def test_merging_isbns_field():
    root = {'isbns': [
        {
            'medium': 'online',
            'value': '9789462392434'
        }, {
            'medium': 'print',
            'value':  '9789462392427'
        }
    ]}
    # record: 1597991
    head = {'isbns': [
        {
            'medium': 'online',
            'value': '9789462392434'
        }, {
            'medium': 'print',
            'value':  '9789462392427'
        }
    ]}
    update = {'isbns': [
        {
            'medium': 'online',
            'value': '9789462392434'
        }, {
            'medium': 'print',
            'value':  '9789462392427'
        }
    ]}

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('keywords')
def test_merging_keywords_field():
    root = {'keywords': [
        {
            'schema': 'INSPIRE',
            'value': 'colliding beams'
        }
    ]}  # record: 1518997
    head = {'keywords': [
        {
            'schema': 'INSPIRE',
            'value': 'colliding super beams'
        }, {
            'schema': 'INSPIRE',
            'value':  'scattering'
        }
    ]}
    update = {'keywords': [
        {
            'schema': 'INSPIRE',
            'value': 'mass: lower limit'
        }
    ]}

    expected_merged = {'keywords': [
        {
            'schema': 'INSPIRE',
            'value':  'mass: lower limit'
        }, {
            'schema': 'INSPIRE',
            'value':  'colliding super beams'
        }, {
            'schema': 'INSPIRE',
            'value':  'scattering'
        }
    ]}
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('languages')
def test_merging_languages_field():
    root = {}
    # not sure if this is a significant case
    head = {'languages': ['it', 'fr']}
    update = {'languages': ['it', 'fr', 'en']}

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('legacy_creation_date')
def test_merging_legacy_creation_date_field():
    root = {}  # record: 1124236
    head = {'legacy_creation_date': '2012-07-30'}
    update = {}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('license')
def test_merging_license_field():
    root = {
        'license': [
            {
                'imposing': 'Elsevier',
                'url': 'http://creativecommons.org/licenses/by/4.0/',
                'license': 'elsevier foo bar'
            }
        ]
    }
    head = {'license': [
        {
            'imposing': 'Elsevier',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'elsevier foo bar'
        },
        {
            'imposing': 'arXiv',
            'url':      'http://creativecommons.org/licenses/by/4.0/',
            'license':  'arxiv foo bar'
        }
    ]}
    update = {'license': [
        {
            'imposing': 'Elsevier',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'elsevier foo bar updated!'
        }
    ]}

    expected_merged = {'license': [
        {
            'imposing': 'Elsevier',
            'url': 'http://creativecommons.org/licenses/by/4.0/',
            'license': 'elsevier foo bar updated!'
        },
        {
            'imposing': 'arXiv',
            'url':      'http://creativecommons.org/licenses/by/4.0/',
            'license':  'arxiv foo bar'
        }
    ]}
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('new_record')
def test_merging_new_record_field():
    root = {}  # record: 37545
    head = {'new_record': {'$ref': 'd361769'}}
    update = {}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('new_record')
def test_merging_new_record_field_filled_root():
    root = {}  # record: 37545
    head = {'new_record': {'$ref': 'd361769'}}
    update = {}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('number_of_pages')
def test_merging_number_of_pages_field():
    root = {'number_of_pages': 109}  # record: 1512524
    head = {'number_of_pages': 108}
    update = {'number_of_pages': 110}

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['number_of_pages'], 108]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('persistent_identifiers')
def test_merging_persistent_identifiers_field():
    root = {}
    head = {
        'persistent_identifiers': [
            {
                'material': 'publication',
                'schema': 'HDL',
                'source': 'EDP Sciences',
                'value': '10.1051/epjconf/201713506006'
            }
        ]
    }
    update = {
        'persistent_identifiers': [
            {
                'material': 'publication',
                'schema': 'HDL foo',
                'source': 'EDP Sciences bar',
                'value': '10.1051/epjconf/201713506006'
            }
        ]
    }

    expected_merged = head
    expected_conflict = [
        ['SET_FIELD', ['persistent_identifiers', 0, 'source'], 'EDP Sciences bar'],
        ['SET_FIELD', ['persistent_identifiers', 0, 'schema'], 'HDL foo']
    ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('preprint_date')
def test_merging_preprint_date_field():
    root = {'preprint_date': '2015-05-02'}  # record: 1375944
    head = {'preprint_date': '2015-05-03'}
    update = {'preprint_date': '2015-05-04'}

    expected_merged = head
    expected_conflict = [['SET_FIELD', ['preprint_date'], '2015-05-04']]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('public_notes')
def test_merging_public_notes_field():
    root = {}  # 1598270
    head = {'public_notes': [
        {'source': 'arXiv', 'value': '50 pages, 32 figures'}]
    }
    update = {'public_notes': [
        {'source': 'arXiv', 'value': '51 pages, 33 figures'},
        {'source': 'Elsevier', 'value': '51 pages, 33 figures'}],
    }

    expected_merged = update
    expected_conflict = [['SET_FIELD',
                          ['public_notes', 0, 'value'],
                          '50 pages, 32 figures']
                         ]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('publication_info')
def test_merging_publication_info_field():
    root = {
        'publication_info': [
            {
                'artid': '948-979',
                'curated_relation': True,
                'journal_issue': 'foo',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }
        ]
    }  # record 697133
    head = {
        'publication_info': [
            {
                'artid': '948-979',
                'curated_relation': True,
                'journal_issue': '2',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }
        ]
    }
    update = {
        'publication_info': [
            {
                'artid': '948-979',
                'curated_relation': True,
                'journal_issue': '1',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }, {
                'artid': '948-977',
                'curated_relation': True,
                'journal_issue': '4',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }
        ]
    }

    expected_merged = {
        'publication_info': [
            {
                'artid': '948-979',
                'curated_relation': True,
                'journal_issue': '2',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }, {
                'artid': '948-979',
                'curated_relation': True,
                'journal_issue': '1',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }, {
                'artid': '948-977',
                'curated_relation': True,
                'journal_issue': '4',
                'journal_title': 'Adv.Theor.Math.Phys.',
                'journal_volume': '12',
                'year': 2008,
                'cnum': 'C12-03-10',
                'material': 'erratum',
                'page_end': '042',
                'page_start': '032',
                'parent_isbn': '9780521467025',
                'parent_report_number': 'CERN-PH-TH-2012-115',
            }
        ]
    }
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('publication_type')
def test_merging_publication_type_field():
    root = {'publication_type': ['introductory']}
    head = {'publication_type': ['introductory', 'lectures']}
    update = {'publication_type': ['lectures', 'review']}

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('refereed')
def test_merging_refereed_field():
    root = {}
    head = {'refereed': True}
    update = {'refereed': False}

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['refereed'], True]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('report_numbers')
def test_merging_report_numbers_field():
    root = {'report_numbers': [
                {
                    'source': 'arXiv',
                    'value': 'arXiv:1705.01099'
                }
            ]}  # record: 1598022
    head = {'report_numbers': [
                {
                    'hidden': True,
                    'source': 'arXiv',
                    'value': 'arXiv:1705.01099'
                }, {
                    'source': 'foo bar',
                    'value': 'foo:123456'
                }
            ]}
    update = {'report_numbers': [
                {
                    'hidden': False,
                    'source': 'hepcrawl',
                    'value': 'arXiv:1705.01099'
                }
            ]}

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['report_numbers', 0, 'hidden'], True]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('$ref')
def test_merging_self_field():
    root = {}
    head = {'$ref': 'url foo'}
    update = {}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict


@cover('texkeys')
def test_merging_texkeys_field():
    root = {'texkeys': ['Kotwal:2016']}
    head = {'texkeys': ['Kotwal:2016', 'Kotwalfoo:2017']}
    update = {}

    expected_merged = head
    expected_conflict = [['REMOVE_FIELD', ['texkeys'], None]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('thesis_info')
def test_merging_thesis_info_field():
    root = {
        'thesis_info': {
            'date': '2017',
            'defense_date': '2017',
            'degree_type': 'phd',
            'institutions': [
                {
                    'curated_relation': False,
                    'name': 'Columbia U.',
                    'record': {'$ref': 'foo-link'}
                }
            ]
        }
    }  # record: 1597507
    head = {
        'thesis_info': {
            'date': '2017',
            'defense_date': '2017',
            'degree_type': 'phd',
            'institutions': [
                {
                    'curated_relation': True,
                    'name': 'Columbia University',
                    'record': {'$ref': 'foo-link'}
                }
            ]
        }
    }
    update = {
        'thesis_info': {
            'date': '2017',
            'defense_date': '2017',
            'degree_type': 'phd',
            'institutions': [
                {
                    'curated_relation': False,
                    'name': 'Second university of foo bar',
                    'record': {'$ref': 'foo-link2'}
                }, {
                    'curated_relation': False,
                    'name': 'Columbia U.',
                    'record': {'$ref': 'foo-link'}
                },
            ]
        }
    }

    expected_merged = update
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('title_translations')
def test_merging_title_translations_field():
    root = {'title_translations': [
        {
            'source': 'submitter',
            'title': 'ANTARES: An observatory at the seabed '
                     'to the confines of the Universe'
        }  # record: 1519935
    ]}
    head = {'title_translations': [
        {
            'language': 'en',
            'source': 'submitter',
            'subtitle': 'this subtitle has been added by a curator',
            'title': 'ANTARES: An observatory at the seabed '
                     'to the confines of the Universe'
        }
    ]}
    update = {'title_translations': [
        {
            'source': 'submitter',
            'title': 'ANTARES: An observatory at the seabed '
                     'to the confines of the Universe'
        }, {
            'language': 'it',
            'source': 'submitter',
            'title': 'ANTARES: Un osservatorio foo bar'
        }
    ]}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('titles')
def test_merging_titles_field():
    root = {'titles': [
        {
            'source': 'submitter',
            'title':  'ANTARES: An observatory at the seabed '
                      'to the confines of the Universe'
        }  # record: 1519935
    ]}
    head = {'titles': [
        {
            'source':   'submitter',
            'subtitle': 'this subtitle has been added by a curator',
            'title':    'ANTARES: An observatory at the seabed '
                        'to the confines of the Universe'
        }
    ]}
    update = {'titles': [
        {
            'source':   'submitter',
            'title':    'ANTARES: Un osservatorio foo bar'
        }, {
            'source':   'submitter',
            'title':    'ANTARES: An observatory at the seabed '
                        'to the confines of the Universe'
        }
    ]}

    expected_merged = {'titles': [
        {
            'source':   'submitter',
            'title':    'ANTARES: Un osservatorio foo bar'
        }, {
            'source':   'submitter',
            'subtitle': 'this subtitle has been added by a curator',
            'title':    'ANTARES: An observatory at the seabed '
                        'to the confines of the Universe'
        }
    ]}
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('urls')
def test_merging_urls_field():
    root = {'urls': [
        {'description': 'descr 1', 'value': 'a'}
    ]}
    head = {'urls': [
        {'description': 'descr 1', 'value': 'a'},
        {'description': 'descr 2', 'value': 'b'},

    ]}
    update = {}

    expected_merged = head
    expected_conflict = [['REMOVE_FIELD', ['urls'], None]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('withdrawn')
def test_merging_wirthdrawn_field():
    root = {}
    head = {'withdrawn': True}
    update = {'withdrawn': False}

    expected_merged = update
    expected_conflict = [['SET_FIELD', ['withdrawn'], True]]

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


# References Field
@cover('references')
def test_merging_references_field_curated_relation():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'curated_relation': True
            }
        ]
    }

    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'curated_relation': True
            }, {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619172'
                },
                'curated_relation': True
            }
        ]
    }

    expected_conflict = None
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_raw_refs():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'raw_refs': [
                    {
                        'source': 'reference_builder',
                        'value': 'Moscow INR preprint 702',
                        'schema': 'text'
                    }
                ]
            }
        ]
    }

    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'raw_refs': [
                    {
                        'source': 'reference_builder',
                        'value': 'Moscow INR preprint 702',
                        'schema': 'text'
                    },
                    {
                        'source': 'reference_builder',
                        'value': 'Ph.D.thesis',
                        'schema': 'text'
                    }
                ]
            }
        ]
    }

    expected_conflict = None
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_authors():
    root = {}

    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'authors': [
                        {
                            'inspire_role': 'author',
                            'full_name': 'Cox, Brian',
                        }, {
                            'inspire_role': 'author',
                            'full_name': 'Dan, Brown'
                        }
                    ]
                }
            }
        ]
    }

    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'authors': [
                        {
                            'full_name': 'Cox, Brian'
                        }
                    ]
                }
            }, {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619172'
                },
                'reference': {
                    'authors': [
                        {
                            'inspire_role': 'author',
                            'full_name': 'Max Power'
                        }
                    ]
                }
            }
        ]
    }

    expected_conflict = [
        [
            'ADD_BACK_TO_HEAD',
            ['references', 0, 'reference', 'authors'],
            {'full_name': 'Dan, Brown', 'inspire_role': 'author'}
        ]
    ]
    expected_merged = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'authors': [
                        {
                            'inspire_role': 'author',
                            'full_name': 'Cox, Brian'
                        }
                    ]
                }
            }, {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619172'
                },
                'reference': {
                    'authors': [
                        {
                            'inspire_role': 'author',
                            'full_name': 'Max Power'
                        }
                    ]
                }
            }
        ]
    }

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_arxiv_eprint():
    root = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {}
            }
        ]
    }
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'arxiv_eprint': '1703.07275'
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'arxiv_eprint': '1703.07274'
                }
            }
        ]
    }

    expected_conflict = [['SET_FIELD', ['references', 0, 'reference', 'arxiv_eprint'], '1703.07275']]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_book_series():
    root = {
        'references': [
            {
                'record':    {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'book_series': {
                        'title': 'IEEE Nucl.Sci. Symp.Conf.Rec.'
                    },
                }
            }
        ]
    }
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'book_series': {
                            'title': 'IEEE Nucl.Sci. Symp.Conf.Rec.'
                    },
                }
            }
        ]
    }

    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'book_series': {
                            'title': 'IEEE Nucl.Sci. Symp.Conf.Rec. foo'
                    }
                }
            }
        ]
    }

    expected_conflict = None
    expected_merged = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'book_series': {
                            'title': 'IEEE Nucl.Sci. Symp.Conf.Rec. foo'
                    },
                }
            }
        ]
    }

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_document_type():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'document_type': 'book'
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'document_type': 'article'
                }
            }
        ]
    }

    expected_conflict = [['SET_FIELD', ['references', 0, 'reference', 'document_type'], 'book']]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_imprint():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'imprint': {'publisher': 'IAEA', 'date': '2013'}
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'imprint': {'publisher': 'IAEA', 'date': '2014'}
                }
            }
        ]
    }

    expected_conflict = [['SET_FIELD', ['references', 0, 'reference', 'imprint', 'date'], '2013']]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_isbn():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'isbn': '9780691140347'
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'isbn': '9780691140348'
                }
            }
        ]
    }

    expected_conflict = [['SET_FIELD', ['references', 0, 'reference', 'isbn'], '9780691140347']]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_label():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'label': 'feynman_be_no_label'
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'label': 'feynman be no label'
                }
            }
        ]
    }

    expected_conflict = [['SET_FIELD', ['references', 0, 'reference', 'label'], 'feynman_be_no_label']]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_misc():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'misc': [
                        'Proceedings of the International School of Physics Course CXL'
                    ]
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'misc': [
                        'Y.-a. Liao, and R. G. Hulet'
                    ]
                }
            }
        ]
    }

    expected_conflict = None
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_persistent_identifiers():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'persistent_identifiers': [
                        {
                            'value': 'hdl:1721.1/15620',
                            'schema': 'HDL'
                        }
                    ]
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'persistent_identifiers': [
                        {
                            'value': '1963/1698',
                            'schema': 'HDL'
                        }
                    ]
                }
            }
        ]
    }

    expected_conflict = None
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_report_numbers():
    root = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'report_numbers': ['IFT-UAM-CSIC-14-035']
                }
            }
        ]
    }
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'report_numbers': ['IFT-UAM-CSIC-14-036']
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'report_numbers': ['IFT-UAM-CSIC-14-037']
                }
            }
        ]
    }

    expected_conflict = None
    expected_merged = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'report_numbers': [
                        'IFT-UAM-CSIC-14-036',
                        'IFT-UAM-CSIC-14-037',
                    ]
                }
            }
        ]
    }

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_texkey():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'texkey': '998'
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'texkey': '999'
                }
            }
        ]
    }

    expected_conflict = [['SET_FIELD', ['references', 0, 'reference', 'texkey'], '998']]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_title():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'title': {
                        'title': 'Components of the dilepton continuum in Pb+Pb at $\\sqrt{s_{_{NN}}} = 2.76 $ TeV',
                        'source': 'arxiv'
                    }
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'title': {
                        'title': 'Components of the dilepton continuum in Pb+Pb $\\sqrt{s_{_{NN}}} = 2.76 $ TeV',
                        'source': 'arxiv'
                    }
                }
            }
        ]
    }

    expected_conflict = [
        [
            'SET_FIELD',
            ['references', 0, 'reference', 'title', 'title'],
            'Components of the dilepton continuum in Pb+Pb at $\sqrt{s_{_{NN}}} = 2.76 $ TeV'
        ]
    ]
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('references')
def test_merging_references_field_reference_urls():
    root = {}
    head = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'urls': [
                        {
                            'description': 'No final state energy loss is included.',
                            'value': 'http://inspirehep.net/record/1115196/files/Fig1a_histNoEloss_Pt.png'
                        }, {
                            'description': 'Here we include final state energy loss assuming that the charm and bottom '
                                           'quark $R_{AA}$ is the same, as discussed in the text.',
                            'value': 'http://inspirehep.net/record/1115196/files/Fig2a_histEloss_Pt.png'
                        }
                    ]
                }
            }
        ]
    }
    update = {
        'references': [
            {
                'record': {
                    '$ref': 'http://newlabs.inspirehep.net/api/literature/619171'
                },
                'reference': {
                    'urls': [
                        {
                            'description': 'No final state energy loss is included.',
                            'value': 'http://inspirehep.net/record/1115196/files/Fig1a_histNoEloss_Pt.jpeg'
                        }, {
                            'description': 'Here we include final state energy loss assuming that the charm and bottom '
                                           'quark $R_{AA}$ is the same, as discussed in the text.',
                            'value': 'http://inspirehep.net/record/1115196/files/Fig2a_histEloss_Pt.jpeg'
                        }
                    ]
                }
            }
        ]
    }

    expected_conflict = None
    expected_merged = update

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


@cover('self')
def test_self_field():
    root = {}
    head = {
        "self": {
            "$ref": "http://labs.inspirehep.net/api/literature/1622230"
        }
    }
    conflict_val = "http://labs.inspirehep.net/api/literature/9874654321"
    update = {
        "self": {
            "$ref": conflict_val
        }
    }

    expected_merged = head
    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == [[u'SET_FIELD', [u'self', u'$ref'], conflict_val]]
    validate_subschema(merged)


@pytest.mark.xfail
@cover('documents')
def test_documents_field():
    pytest.fail("Not tested. Merger doesn't have to handle this field.")


@pytest.mark.xfail
@cover('figures')
def test_figures_field():
    pytest.fail("Not tested. Merger doesn't have to handle this field.")


@cover('record_affiliations')
def test_record_affiliations_field():
    root = {}
    head = {
        'record_affiliations': [
            {
                "curated_relation": True,
                "record": {"$ref": "http://labs.inspirehep.net/api/literature/9874654321"},
                "value": "parent",
            },
        ]
    }
    update = {
        'record_affiliations': [
            {
                "curated_relation": False,
                "record": {"$ref": "http://labs.inspirehep.net/api/literature/9874654321"},
                "value": "precedessor",
            },
        ]
    }
    expected_merged = {
        'record_affiliations': [
            head['record_affiliations'][0],
            update['record_affiliations'][0]
        ]
    }
    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict is None
    validate_subschema(merged)


@cover('related_records')
def test_related_records_field():
    root = {}
    head = {
        'related_records': [
            {
                "curated_relation": True,
                "record": {"$ref": "http://labs.inspirehep.net/api/literature/9874654321"},
                "relation": "parent",
            },
        ]
    }
    update = {
        'related_records': [
            {
                "curated_relation": False,
                "record": {"$ref": "http://labs.inspirehep.net/api/literature/9874654321"},
                "relation": "predecessor",
            },
        ]
    }
    expected_merged = {
        'related_records': [
            head['related_records'][0],
            update['related_records'][0]
        ]
    }
    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict is None
    validate_subschema(merged)


@cover('curated')
def test_curated():
    root = {}
    head = {
        'curated': True
    }
    # will never come from updates
    update = {}

    expected_merged = head
    expected_conflict = None

    root, head, update, expected_merged = add_arxiv_source(root, head, update, expected_merged)
    merged, conflict = inspire_json_merge(root, head, update)

    expected_conflict = sort_conflicts(expected_conflict)

    merged = add_arxiv_source(merged)
    assert merged == expected_merged
    assert conflict == expected_conflict
    validate_subschema(merged)


def test_schema_keys_coverage():
    # This test check that every key in the schema has been covered by at
    # least one test.
    # IMPORTANT: this test depends on the others, so keep it as the last
    schema = load_schema('hep')
    key_list = schema['properties'].keys()
    missing = []
    for key in key_list:
        if key not in COVERED_SCHEMA_KEYS:
            missing.append(key)
    assert not missing
