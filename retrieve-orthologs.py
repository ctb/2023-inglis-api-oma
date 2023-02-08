#! /usr/bin/env python
import urllib3
import json
import sys
import argparse


def get_orthologs(http, url):
    r = http.request('GET', url)

    results = r.data.decode('utf-8')
    return json.loads(results)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('id_file')
    args = p.parse_args()

    id_list = [ x.strip() for x in open(args.id_file, 'rt') ]
    id_list = [ x for x in id_list if x ]

    query_body = dict(ids=id_list)
    query_json = json.dumps(query_body)

    http = urllib3.PoolManager()
    r = http.request('POST',
                     'https://omabrowser.org/api/protein/bulk_retrieve/',
                     body = query_json,
                     headers = { 'Content-Type': 'application/json'})

    query_results_text = r.data.decode('utf-8')
    query_results = json.loads(query_results_text)

    print(f"Got {len(query_results)} back, yay!")


    ortholog_list = []

    for pid, qr in zip(id_list, query_results):
        ortholog_url = qr['target']['orthologs']
        print(f"loading {ortholog_url}")
        ortholog_info = get_orthologs(http, ortholog_url)
        ortholog_list.append(ortholog_info)

        print(f"got {len(ortholog_info)} orthologs back.")

        # save back to a local JSON file so I can stop querying shit
        outfile = f"{pid}.bulk.json"
        with open(outfile, 'wt') as fp:
            fp.write(json.dumps(ortholog_info))


if __name__ == '__main__':
    sys.exit(main())
