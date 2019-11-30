import sys,os,json,torch,re
import torch.optim as optim
from torch.nn import functional as F


torch.manual_seed(1)
d = json.loads(open('embedsimpletrainvectors1.json').read())
inputs = []
outputs = []
ocount = 0
zcount = 0
_zcount = 0
for item in d:
    if item[5] == 1.0:
        vector = [item[1]] + item[2] + item[4]
        inputs.append(vector)
        outputs.append(1.0)
        ocount += 1
    else:
        if zcount%40 == 0:
            vector = [item[1]] + item[2] + item[4]
            inputs.append(vector)
            outputs.append(0.0)
            _zcount += 1
        zcount += 1

print(ocount,zcount)

d = json.loads(open('embedsimpletestvectors1.json').read())
testinputs = []
testoutputs = []
ocount = 0
zcount = 0
_zcount = 0
for item in d:
    if item[5] == 1.0:
        vector = [item[1]] + item[2] + item[4]
        testinputs.append(vector)
        testoutputs.append(1.0)
        ocount += 1
    else:
        if zcount%30 == 0:
            vector = [item[1]] + item[2] + item[4]
            testinputs.append(vector)
            testoutputs.append(0.0)
            _zcount += 1
        zcount += 1


f = open('testentityspans1.json')
s = f.read()
d2 = json.loads(s)
f.close()


device = torch.device('cuda')
batch_size = 5000
N, D_in, H1, H2, H3, D_out = batch_size, 501, 300, 100, 10, 1

x = torch.FloatTensor(inputs).cuda()
y = torch.FloatTensor(outputs).cuda()
xtest = torch.FloatTensor(testinputs).cuda()
ytest = torch.FloatTensor(testoutputs).cuda()

model = torch.nn.Sequential(
          torch.nn.Linear(D_in, H1),
          torch.nn.ReLU(),
          torch.nn.Linear(H1, H2),
          torch.nn.ReLU(),
          torch.nn.Linear(H2, H3),
          torch.nn.ReLU(),
          torch.nn.Linear(H3, D_out)
        ).to(device)

loss_fn = torch.nn.MSELoss(reduction='mean')
#loss_fn = torch.nn.BCELoss(reduction='mean')
optimizer = optim.SGD(model.parameters(), lr=0.001)#,nesterov=True, momentum=0.5)
iter = 0
besttrue = 0
urilabeldict = {}
bestloss = 999
while 1:
    iter += 1
    permutation = torch.randperm(x.size()[0])
    for i in range(0,x.size()[0],batch_size):
        indices = permutation[i:i+batch_size]
        _x,_y = x[indices],y[indices]
        y_pred = model(_x)
        loss = loss_fn(y_pred.reshape(-1), _y)
        model.zero_grad()
        loss.backward()
        optimizer.step()
    if iter%1000 == 0:
        print(iter,loss)
        with torch.no_grad():
            preds = model(xtest).cuda()
            testlossfn = torch.nn.MSELoss(reduction='mean')
            testloss = testlossfn(preds.reshape(-1),ytest)
            print("test set mseloss = %f bestloss = %f"%(testloss, bestloss))
            if testloss < bestloss:
                bestloss = loss
                torch.save(model.state_dict(), 'embedentreranker.model')
                 
                