import sys,os,json,re
from elasticsearch import Elasticsearch

es = Elasticsearch()

wikiurilabeldict = json.loads(open('../../../data/wikiurilabeldict1.json').read())
gold = []
f = open('/home/sda-srv05/debayan/LC-QuAD2.0/dataset/test.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: int(x['uid']))

for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = ['http://wikidata.dbpedia.org/resource/'+ent for ent in _ents]
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    gold.append(unit)


def getlabels(urls):
    labels = []
    for url in urls:
         if 'entity' in url:
             if url in wikiurilabeldict:
                 labels.append([url,wikiurilabeldict[url]])
             else:
                 labels.append([url,[]])
         else:
             res = es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri":url}},"size":100})
             for idx,hit in enumerate(res['hits']['hits']):
                labels.append([url,hit['_source']['wikidataLabel']])
    return labels


f = open('erspanmdp1.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: int(x[0]))

tpentity = 0
fpentity = 0
fnentity = 0
tprelation = 0
fprelation = 0
fnrelation = 0
totalentchunks = 0
totalrelchunks = 0
mrrent = 0
mrrrel = 0
chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    if len(queryitem[1]) == 0:
        continue
    if queryitem[0] != golditem['uid']:
        print('uid mismatch')
        sys.exit(1)
    queryentities = []
    queryrelations = []
    if 'rerankedlists' in queryitem[1]:
        for num,urltuples in queryitem[1]['rerankedlists'].iteritems():
            if queryitem[1]['chunktext'][int(num)]['class'] == 'entity':
                for urltuple in urltuples:
                    queryentities.append(urltuple[1][0])
                    break
            if  queryitem[1]['chunktext'][int(num)]['class'] == 'relation':
                for urltuple in urltuples:
                    if '_' in urltuple[1][0]:
                        relid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[0]
                        qualid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[1]
                        queryrelations.append('http://www.wikidata.org/entity/'+relid)
                        queryrelations.append('http://www.wikidata.org/entity/'+qualid)
                    else:
                        queryrelations.append(urltuple[1][0])
                    break
    #print(getlabels(golditem['entities']),getlabels(queryentities),getlabels(golditem['relations']), getlabels(queryrelations), golditem['question'], queryitem[1]['chunktext'])
    for goldentity in golditem['entities']:
        totalentchunks += 1
        if goldentity in queryentities:
            tpentity += 1
        else:
            fnentity += 1
    for goldrelation in golditem['relations']:
        totalrelchunks += 1
        if goldrelation in queryrelations:
            tprelation += 1
        else:
            fnrelation += 1
    for queryentity in queryentities:
        if queryentity not in golditem['entities']:
            fpentity += 1
    for queryrelation in queryrelations:
        if queryrelation not in golditem['relations']:
            fprelation += 1

precisionentity = tpentity/float(tpentity+fpentity)
recallentity = tpentity/float(tpentity+fnentity)
f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
print("precision entity = ",precisionentity)
print("recall entity = ",recallentity)
print("f1 entity = ",f1entity)

precisionrelation = tprelation/float(tprelation+fprelation)
recallrelation = tprelation/float(tprelation+fnrelation)
f1relation = 2*(precisionrelation*recallrelation)/(precisionrelation+recallrelation)
print("precision relation = ",precisionrelation)
print("recall relation = ",recallrelation)
print("f1 relation = ",f1relation)

mrrent = 0
mrrrel = 0
faketotent = 0
faketotrel = 0

chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    if len(queryitem[1]) == 0:
        continue
    if 'rerankedlists' in queryitem[1]:
        for num,urltuples in queryitem[1]['rerankedlists'].iteritems():
            if queryitem[1]['chunktext'][int(num)]['class'] == 'entity':
                for goldentity in golditem['entities']:
                    if goldentity in [urltuple[1][0] for urltuple in urltuples]:
                        mrrent += 1.0/float([urltuple[1][0] for urltuple in urltuples].index(goldentity)+1)
                        faketotent += 1
            if queryitem[1]['chunktext'][int(num)]['class'] == 'relation':
                queryrelations = []
                for urltuple in urltuples:
                    if '_' in urltuple[1][0]:
                        relid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[0]
                        qualid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[1]
                        queryrelations.append('http://www.wikidata.org/entity/'+relid)
                        queryrelations.append('http://www.wikidata.org/entity/'+qualid)
                    else: 
                        queryrelations.append(urltuple[1][0])
                for goldrelation in golditem['relations']:
                    if goldrelation in queryrelations:
                        mrrrel += 1.0/float(queryrelations.index(goldrelation)+1)
                        faketotrel += 1

totmrrent = mrrent/totalentchunks
totmrrrel = mrrrel/totalrelchunks
print('ent mrr = %f'%totmrrent)
print('rel mrr = %f'%totmrrrel)
faketotmrrent = mrrent/faketotent
faketotmrrrel = mrrrel/faketotrel
print('fake ent mrr = %f'%faketotmrrent)
print('fake rel mrr = %f'%faketotmrrrel)

presentent = 0
presentrel = 0
chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    if len(queryitem[1]) == 0:
        continue
    for num,urltuples in queryitem[1]['rerankedlists'].iteritems():
        if queryitem[1]['chunktext'][int(num)]['class'] == 'entity':
            for goldentity in golditem['entities']:
                for urltuple in urltuples:
                    if urltuple[1][0] == goldentity:
                        presentent += 1
#        if queryitem[0]['chunktext'][int(num)]['class'] == 'relation':
#             queryrelations = []
#             for queryrelation in chunk['topkmatches']:
#                if '_' in queryrelation:
#                    relid = queryrelation.split('http://www.wikidata.org/entity/')[1].split('_')[0]
#                    qualid = queryrelation.split('http://www.wikidata.org/entity/')[1].split('_')[1]
#                    queryrelations.append('http://www.wikidata.org/entity/'+relid)
#                    queryrelations.append('http://www.wikidata.org/entity/'+qualid)
#                else:
#                    queryrelations.append(queryrelation)
#             for goldrelation in golditem['relations']:
#                if goldrelation in queryrelations:
#                    presentrel += 1


print('entity pipeline failure = %f'%((totalentchunks-presentent)/float(totalentchunks)))
#print('relation pipeline failure = %f'%((totalrelchunks-presentrel)/float(totalrelchunks)))




