from collections import defaultdict
import heapq

class State:
    def __init__(self, bucket, g=0, h=0):
        self.bucket = bucket
        self.g = g
        self.h = h
        self.f = self.g + self.h

    def __lt__(self, other):
        return self.f < other.f
    
class Graph:
    def __init__(self, initBucket, targetBucket, bucketCapacity):
        self.initBucket = initBucket
        self.targetBucket = targetBucket
        self.bucketCapacity = bucketCapacity
        self.numBuckets = len(targetBucket)
    
    def printBucket(self, currentBucket):
        bucket_info = ""
        for i in range(self.numBuckets):
            if i != self.numBuckets - 1:
                bucket_info += f"\033[94mBucket {i+1}: {currentBucket[i]}/{self.bucketCapacity[i]} Litre\033[0m, "
            else:
                bucket_info += f"\033[92mTank: {currentBucket[i]}/{self.targetBucket[i]} Litre\033[0m"
        print(bucket_info)   
        
    def countMahattan(self, currentBucket):
        mahattanValue = abs(self.targetBucket[-1] - currentBucket[-1])
        
        # for i in range(self.numBuckets):
        #     mahattanValue += abs(self.targetBucket[i] - currentBucket[i])
        
        return mahattanValue
    
    def waterTransfer(self, currentBucket):
        availableBucket = []
        
        # Case 1: Pour water from river into buckets
        for i in range(self.numBuckets - 1):
            tempBucket = currentBucket.copy()
            if tempBucket[i] < self.bucketCapacity[i]:
                waterAmount = self.bucketCapacity[i] - tempBucket[i] 
                tempBucket[i] = self.bucketCapacity[i]
                message = f"Pour {waterAmount} litres water from river into bucket {i+1}"
                
                # availableBucket.append((tempBucket, message))
                availableBucket.append(tempBucket)
        
        # Case 2: Pour water from buckets into river
        for i in range(self.numBuckets - 1):
            tempBucket = currentBucket.copy()
            if tempBucket[i] > 0:
                waterAmount = tempBucket[i] 
                tempBucket[i] = 0
                message = f"Pour {waterAmount} litres water from bucket {i+1} into river"
                
                # availableBucket.append((tempBucket, message))
                availableBucket.append(tempBucket)
        
        # Case 3: Pour water from bucket into tank
        for i in range(self.numBuckets - 1):
            tempBucket = currentBucket.copy()
            if tempBucket[i] > 0:
                waterAmount = tempBucket[i]
                tempBucket[i] = 0
                tempBucket[-1] += waterAmount
                message = f"Pour {waterAmount} litres water from bucket {i+1} into tank"

                # availableBucket.append((tempBucket, message))
                availableBucket.append(tempBucket)


        # Case 4: Pour water between buckets (from bucket i to bucket j)
        for i in range(self.numBuckets - 1):
            for j in range(self.numBuckets - 1):
                if i != j and currentBucket[i] > 0:
                    tempBucket = currentBucket.copy()

                    if tempBucket[j] + tempBucket[i] <= self.bucketCapacity[j]:
                        waterAmount = tempBucket[i]
                        tempBucket[i] = 0
                        tempBucket[j] += waterAmount
                    else:
                        waterAmount = self.bucketCapacity[j] - tempBucket[j]
                        tempBucket[i] -= waterAmount
                        tempBucket[j] = self.bucketCapacity[j]
                    message = f"Pour {waterAmount} litres water from bucket {i+1} into bucket {j+1}"

                    # availableBucket.append((tempBucket, message))
                    availableBucket.append(tempBucket)

        
        return availableBucket

    def checkAction(self, previousState, currentState):
        pourWaterFromRiverToBucket = all(currentState[i] >= previousState[i] for i in range(self.numBuckets))
        pourWaterFromBucketToRiver = all(currentState[i] <= previousState[i] for i in range(self.numBuckets))   #Does not count step
        pourWaterFromBucketToTank = currentState[-1] > previousState[-1]
        pourWaterFromBucketToBucket = not pourWaterFromRiverToBucket and not pourWaterFromBucketToRiver and not pourWaterFromBucketToTank
        
        if pourWaterFromRiverToBucket:
            for i in range(self.numBuckets):
                if currentState[i] > previousState[i]:
                    message = f"Pour {currentState[i] - previousState[i]} litres water from river into bucket {i+1}"
                    break
        elif pourWaterFromBucketToRiver:
            for i in range(self.numBuckets):
                if currentState[i] < previousState[i]:
                    message = f"Pour {previousState[i] - currentState[i]} litres water from bucket {i+1} into river"
                    break
        elif pourWaterFromBucketToTank:
            for i in range(self.numBuckets):
                if currentState[i] < previousState[i]:
                    message = f"Pour {currentState[-1] - previousState[-1]} litres water from bucket {i+1} into tank"
                    break
        elif pourWaterFromBucketToBucket:
            for i in range(self.numBuckets):
                if currentState[i] < previousState[i]:
                    for j in range(self.numBuckets):
                        if currentState[j] > previousState[j]:
                            waterAmount = previousState[i] - currentState[i]
                            message = f"Pour {waterAmount} litres water from bucket {i+1} into bucket {j+1}"
                            break
                    break
        
  
        return not pourWaterFromBucketToRiver, message
                

        
        
            
            
        
    def A_Star(self):
        open_set = []
        close_set = set()
        ancestor = defaultdict(list)

        start_state = State(self.initBucket, 0, self.countMahattan(self.initBucket))
        heapq.heappush(open_set, (start_state.f, start_state))
        
        while open_set:
            _, current_state = heapq.heappop(open_set)

            if current_state.bucket == self.targetBucket:
                print("Solution found!")
                break
            else:
                close_set.add(tuple(current_state.bucket))

                for neighbor_bucket in self.waterTransfer(current_state.bucket):
                    neighbor_state = State(neighbor_bucket, current_state.g + 1, self.countMahattan(neighbor_bucket))
                    
                    if tuple(neighbor_state.bucket) not in close_set:
                        neighbor_state.f = neighbor_state.g + neighbor_state.h
                        heapq.heappush(open_set, (neighbor_state.f, neighbor_state))
                        ancestor[tuple(neighbor_bucket)] = current_state.bucket
        else:
            print("No solution exists!")
            return

        path = []
        currentBucket = tuple(self.targetBucket)
        
        while currentBucket != tuple(self.initBucket):
            path.append(tuple(currentBucket))
            currentBucket = tuple(ancestor[currentBucket])
        
        path.append(tuple(self.initBucket))

        path = path[::-1]
        
        solution = defaultdict()
        step = 1
        for i, bucket in enumerate(path):
            if i >=1:
                countStep, action = self.checkAction(path[i-1], path[i])
                if countStep:
                    print(f"Step {step}: {action}")
                    self.printBucket(bucket) 
                    if i < len(path) - 1:
                        print("↓")
                    step += 1
                else:
                    print(f"{action}")
                    self.printBucket(bucket) 
                    if i < len(path) - 1:
                        print("↓")
            else:
                print(f"Initial state: ")
                self.printBucket(bucket)
                print("↓")
                
        solution[i] = bucket 
        print()
                
        return solution

# Input đề bài
initBucket = [0,0,0,0]       
targetBucket = [0,0,0,17]
bucketCapacity = [7,8,9]

# initBucket = [0, 0]
# targetBucket = [0, 5]
# bucketCapacity = [5]

graph = Graph(initBucket, targetBucket, bucketCapacity)
graph.A_Star()
                    

             
    
        