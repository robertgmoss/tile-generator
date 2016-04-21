#!/usr/bin/env python

import os
import zipfile
import yaml
import json

LIB_PATH = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = os.path.realpath(os.path.join(LIB_PATH, '..'))

def patch(tilefile, patchfile):

	with zipfile.ZipFile(tilefile, 'a', allowZip64=True) as f:
		tiledir = tilefile.rsplit('.', 1)[0]
		f.extractall(tiledir)

	with open(os.path.join(tiledir, 'metadata/cf.yml'), 'rb') as f:
		metadata = yaml.safe_load(f)

	metadata['product_version'] = metadata.get('product_version', 'custom') + '-route-services'
	job_types = metadata.get('job_types', [])
	router_job = ([ j for j in job_types if j['name'] == 'router'] + [ {} ])[0]
	router_manifest = yaml.safe_load(router_job.get('manifest', ''))
	router_manifest['router'] = router_manifest.get('router', {})
	router_manifest['router']['ssl_skip_validation'] = 'true'
	router_manifest['router']['route_services_timeout'] = 60
	router_manifest['router']['route_services_secret'] = 'route-services-secret'
	router_manifest['router']['route_services_recommend_https'] = 'false'
	router_job['manifest'] = yaml.safe_dump(router_manifest)
	controller_job = ([ j for j in job_types if j['name'] == 'cloud_controller'] + [ {} ])[0]
	controller_manifest = yaml.safe_load(controller_job.get('manifest', ''))
	controller_manifest['router'] = controller_manifest.get('router', {})
	controller_manifest['router']['route_services_secret'] = 'route-services-secret'
	controller_job['manifest'] = yaml.safe_dump(controller_manifest)

	with open(os.path.join(tiledir, 'metadata/cf.yml'), 'wb') as f:
		f.write(yaml.safe_dump(metadata))

	with open(os.path.join(tiledir, 'metadata/cf.yml'), 'rb') as f:
		metadata = yaml.safe_load(f)
		print metadata['product_version']

	patchedfile = tiledir + '-route-services.pivotal'
	with zipfile.ZipFile(patchedfile, 'w', allowZip64=True) as f:
		os.chdir(tiledir)
		for root, dirs, files in os.walk('.'):
		    for file in files:
		    	filename = os.path.join(root, file).lstrip('./')
		    	f.write(filename)
