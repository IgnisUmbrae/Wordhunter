import random

# Simulate a discrete probability distribution (provided as a list of (item,prob) tuples) by calculating its CDF.
def discrete_sample(dist, num):
	items = []
	for i in range(num):
		r = random.uniform(0, 1)
		s = 0
		for d in dist:
			s += d[1]
			if s >= r:
				items.append(d[0])
				break
		else: items.append(dist[-1][0]) # Fallback to account for possible floating point errors
	return items

#http://stackoverflow.com/questions/2161406/how-do-i-generate-a-uniform-random-integer-partition

cache = {}

def count_partitions(n, limit):
    if n == 0:
        return 1
    if (n, limit) in cache:
        return cache[n, limit]
    x = cache[n, limit] = sum(count_partitions(n-k, k) for k in range(1, min(limit, n) + 1))
    return x

def random_partition(n):
    a = []
    limit = 26
    total = count_partitions(n, limit)
    which = random.randrange(total)
    while n:
        for k in range(1, min(limit, n) + 1):
            count = count_partitions(n-k, k)
            if which < count:
                break
            which -= count
        a.append(k)
        limit = k
        n -= k
    return a