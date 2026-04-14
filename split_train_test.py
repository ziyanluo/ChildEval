#encoding=utf8
import sys
import random
data_dir=sys.argv[1]
lines = []
for line in sys.stdin:
    lines.append(line.strip())

train_ratio = 0.8
train_file = f'{data_dir}/train.json'
test_file = f'{data_dir}/test.json'


indices = list(range(len(lines)))
random.shuffle(indices)

train_size = int(len(indices) * train_ratio)

train_indices = indices[:train_size]
test_indices = indices[train_size:]

print(f"train_size:{train_size}")
print(f"test_size:{len(indices)-train_size}")
        
with open(train_file, 'w', encoding='utf-8') as f:
    for idx in train_indices:
        f.write(lines[idx]+'\n')

with open(test_file, 'w', encoding='utf-8') as f:
    for idx in test_indices:
        f.write(lines[idx]+'\n')
