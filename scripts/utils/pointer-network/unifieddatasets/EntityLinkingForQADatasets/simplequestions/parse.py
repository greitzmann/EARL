#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests,re
from multiprocessing import Pool

def hiturl(questionserial):
    question = questionserial[0]
    serial = questionserial[1]
    req = urllib2.Request('http://localhost:4440/processQuery')
    req.add_header('Content-Type', 'application/json')
    try:
        print(question)
        question = re.sub(r"[^a-zA-Z0-9]+", ' ', question)
        print(question)
        inputjson = {'nlquery': question}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = response.read()
        return (int(serial),response,questionserial[1])
    except Exception,e:
        return(int(serial),'[]',questionserial[1])

f = open('annotated_wd_data_test.txt')
count = 0
questions = []
for line in f.readlines():
    line = line.strip()
    s,p,o,q = line.split('\t') 
    questions.append((q,count))
    count += 1
f.close()

pool = Pool(8)
responses = pool.imap(hiturl,questions)

_results = []

count = 0
totalentchunks = 0
tpentity = 0
fpentity = 0
fnentity = 0
for response in responses:
    count += 1
    print(count)
#    item = response[2]
#    goldentities = re.findall( r'wd:(.*?) ', item['sparql_wikidata'])
#    queryentities = []
#    if 'rerankedlists' in json.loads(response[1]):
#        for num,urltuples in json.loads(response[1])['rerankedlists'].iteritems():
#            if json.loads(response[1])['chunktext'][int(num)]['class'] == 'entity':
#                for urltuple in urltuples:
#                    queryentities.append(urltuple[1][0])
#                    break
#    for ent in goldentities:
#        totalentchunks += 1
#        if ent in queryentities:
#            tpentity += 1
#        else:
#            fpentity += 1
#    for ent in queryentities:
#        if ent not in goldentities:
#            fnentity += 1
#    try:
#        precisionentity = tpentity/float(tpentity+fpentity)
#        recallentity = tpentity/float(tpentity+fnentity)
#        f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
#        print("precision entity = ",precisionentity)
#        print("recall entity = ",recallentity)
#        print("f1 entity = ",f1entity)
#    except Exception:
#        pass
    _results.append((response[0],json.loads(response[1])))

#_results = sorted(_results, key=lambda tup: tup[0])

results = []
for result in _results:
    results.append(result)

 
f1 = open('simplequestiionsout.json','w')
print(json.dumps(results),file=f1)
f1.close()