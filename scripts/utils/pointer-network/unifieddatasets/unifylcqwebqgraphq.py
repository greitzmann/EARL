import sys,os,json,re


d = json.loads(open('LC-QuAD2.0/dataset/train.json').read())

trainingdata = []

for item in d:
    question = item['question']
    paraphrased_question = item['paraphrased_question']
    wikisparql = item['sparql_wikidata']
    entities = re.findall( r'wd:(.*?) ', wikisparql)
    if question and len(question) > 10 and len(question) < 500:
        trainingdata.append({'question':question, 'entities': entities, 'source':'lcq2train', 'id':item['uid']})
    if paraphrased_question and len(paraphrased_question) > 10 and len(paraphrased_question) < 500:
        trainingdata.append({'question':question, 'entities': entities, 'source':'lcq2train', 'id':item['uid']})

d = json.loads(open('EntityLinkingForQADatasets/graphquestions/input/graph.train.entities.json').read())

for item in d:
    question = item['utterance']
    entities = item['entities']
    qid = item['question_id']
    trainingdata.append({'question':question, 'entities': entities, 'source':'graphqtrain', 'id':qid})

d = json.loads(open('EntityLinkingForQADatasets/webqsp/input/webqsp.train.entities.json').read())

for item in d:
    question = item['utterance']
    entities = item['entities']
    qid = item['question_id']
    trainingdata.append({'question':question, 'entities': entities, 'source':'webqtrain', 'id':qid})

testingdata = []

d = json.loads(open('LC-QuAD2.0/dataset/test.json').read())

for item in d:
    question = item['question']
    paraphrased_question = item['paraphrased_question']
    wikisparql = item['sparql_wikidata']
    entities = re.findall( r'wd:(.*?) ', wikisparql)
    if question and len(question) > 10 and len(question) < 500:
        testingdata.append({'question':question, 'entities': entities, 'source':'lcq2train', 'id':item['uid']})
    if paraphrased_question and len(paraphrased_question) > 10 and len(paraphrased_question) < 500:
        testingdata.append({'question':question, 'entities': entities, 'source':'lcq2train', 'id':item['uid']})

d = json.loads(open('EntityLinkingForQADatasets/graphquestions/input/graph.test.entities.json').read())

for item in d:
    question = item['utterance']
    entities = item['entities']
    qid = item['question_id']
    testingdata.append({'question':question, 'entities': entities, 'source':'graphqtrain', 'id':qid})

d = json.loads(open('EntityLinkingForQADatasets/webqsp/input/webqsp.test.entities.with_classes.json').read())

for item in d:
    question = item['utterance']
    entities = item['entities']
    qid = item['question_id']
    testingdata.append({'question':question, 'entities': entities, 'source':'webqtrain', 'id':qid})


f = open('unifiedtrain.json','w')
f.write(json.dumps(trainingdata,indent=4))
f.close()


f = open('unifiedtest.json','w')
f.write(json.dumps(testingdata,indent=4))
f.close()






