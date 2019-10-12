import sys,os,json,re


gold = []
f = open('/data/home/sda-srv05/debayan/LC-QuAD2.0/dataset/test.json')
d = json.loads(f.read())

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

f = open('erspanjointrerankernewentityspantrainedparseou6.json')
d = json.loads(f.read())
print(len(d))
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
    uid = queryitem[0]
    queryitem = queryitem[1]
    if len(queryitem) == 0:
        continue
    if uid != golditem['uid']:
        print('uid mismatch')
        sys.exit(1)
    queryentities = []
    queryrelations = []
    if 'rerankedlists' in queryitem[0]:
        for num,urltuples in queryitem[0]['rerankedlists'].iteritems():
            if queryitem[0]['chunktext'][int(num)]['class'] == 'entity':
                for urltuple in urltuples:
                    queryentities.append(urltuple[1][0])
                    break
            if  queryitem[0]['chunktext'][int(num)]['class'] == 'relation':
                for urltuple in urltuples:
                    if '_' in urltuple[1][0]:
                        relid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[0]
                        qualid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[1]
                        queryrelations.append('http://www.wikidata.org/entity/'+relid)
                        queryrelations.append('http://www.wikidata.org/entity/'+qualid)
                    else:
                        queryrelations.append(urltuple[1][0])
                    break
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

#precisionrelation = tprelation/float(tprelation+fprelation)
#recallrelation = tprelation/float(tprelation+fnrelation)
#f1relation = 2*(precisionrelation*recallrelation)/(precisionrelation+recallrelation)
#print("precision relation = ",precisionrelation)
#print("recall relation = ",recallrelation)
#print("f1 relation = ",f1relation)
#
mrrent = 0
mrrrel = 0
faketotent = 0
faketotrel = 0

chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    queryitem = queryitem[1]
    if len(queryitem) == 0:
        continue
    if 'rerankedlists' in queryitem[0]:
        for num,urltuples in queryitem[0]['rerankedlists'].iteritems():
            if queryitem[0]['chunktext'][int(num)]['class'] == 'entity':
                for goldentity in golditem['entities']:
                    if goldentity in [urltuple[1][0] for urltuple in urltuples]:
                        mrrent += 1.0/float([urltuple[1][0] for urltuple in urltuples].index(goldentity)+1)
                        faketotent += 1
            if queryitem[0]['chunktext'][int(num)]['class'] == 'relation':
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
#totmrrrel = mrrrel/totalrelchunks
print('ent mrr = %f'%totmrrent)
#print('rel mrr = %f'%totmrrrel)
faketotmrrent = mrrent/faketotent
#faketotmrrrel = mrrrel/faketotrel
print('fake ent mrr = %f'%faketotmrrent)
#print('fake rel mrr = %f'%faketotmrrrel)

presentent = 0
presentrel = 0
chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    queryitem = queryitem[1]
    if len(queryitem) == 0:
        continue
    for num,urltuples in queryitem[0]['rerankedlists'].iteritems():
        if queryitem[0]['chunktext'][int(num)]['class'] == 'entity':
            for goldentity in golditem['entities']:
                for urltuple in urltuples:
                    if urltuple[1][0] == goldentity:
                        presentent += 1

print('entity pipeline failure @1 = %f'%((totalentchunks-presentent)/float(totalentchunks)))

presentent = 0
presentrel = 0
chunkingerror = 0
for queryitems,golditem in zip(d,gold):
    queryitems = queryitems[1]
    if len(queryitems) == 0:
        continue
    presententlist = []
    for queryitem in queryitems:
        if len(queryitem) == 0:
            continue 
        for num,urltuples in queryitem['rerankedlists'].iteritems():
            if queryitem['chunktext'][int(num)]['class'] == 'entity':
                for urltuple in urltuples:
                    presententlist.append(urltuple[1][0])
    for goldentity in golditem['entities']:
        if goldentity in presententlist:
            presentent += 1
        else:
            print(golditem, [queryitem['chunktext'] for queryitem in queryitems]) 
print('entity pipeline failure @5 = %f'%((totalentchunks-presentent)/float(totalentchunks)))

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


#print('relation pipeline failure = %f'%((totalrelchunks-presentrel)/float(totalrelchunks)))




