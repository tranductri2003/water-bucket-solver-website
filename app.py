import streamlit as st
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
        self.numBuckets = len(initBucket)
    
    def printBucket(self, currentBucket):
        bucket_info = ""
        for i in range(self.numBuckets):
            if i != self.numBuckets - 1:
                bucket_info += f"- **Bucket {i+1}:** {currentBucket[i]}/{self.bucketCapacity[i]} Litre\n"
            else:
                bucket_info += f"- **Tank:** {currentBucket[i]}/{self.targetBucket} Litre\n"
        st.markdown(bucket_info)
  
            
    def visualizeBucket(self, buckets):
        for i, (water_level, capacity) in enumerate(zip(buckets[:-1], self.bucketCapacity)):
            water_fraction = water_level / capacity
            st.write(f"Bucket {i+1}:")
            st.progress(water_fraction)
            st.markdown(f"<span style='color:blue'>{water_level}/{capacity} Litre</span>", unsafe_allow_html=True)

        tank_water_fraction = buckets[-1] / self.targetBucket
        st.write("Tank:")
        st.progress(tank_water_fraction)
        st.markdown(f"<span style='color:blue'>{buckets[-1]}/{self.targetBucket} Litre</span>", unsafe_allow_html=True)



        
    def countMahattan(self, currentBucket):
        mahattanValue = abs(self.targetBucket - currentBucket[-1])
        return mahattanValue
    
    def waterTransfer(self, currentBucket):
        availableBucket = []
        
        # Case 1: Pour water from river into buckets
        for i in range(self.numBuckets - 1):
            tempBucket = currentBucket.copy()
            if tempBucket[i] < self.bucketCapacity[i]:
                waterAmount = self.bucketCapacity[i] - tempBucket[i] 
                tempBucket[i] = self.bucketCapacity[i]
                availableBucket.append(tempBucket)
        
        # Case 2: Pour water from buckets into river
        for i in range(self.numBuckets - 1):
            tempBucket = currentBucket.copy()
            if tempBucket[i] > 0:
                waterAmount = tempBucket[i] 
                tempBucket[i] = 0
                availableBucket.append(tempBucket)
        
        # Case 3: Pour water from bucket into tank
        for i in range(self.numBuckets - 1):
            tempBucket = currentBucket.copy()
            if tempBucket[i] > 0:
                waterAmount = tempBucket[i]
                tempBucket[i] = 0
                tempBucket[-1] += waterAmount
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
                    availableBucket.append(tempBucket)
        
        return availableBucket

    def checkAction(self, previousState, currentState):
        pourWaterFromRiverToBucket = all(currentState[i] >= previousState[i] for i in range(self.numBuckets))
        pourWaterFromBucketToRiver = all(currentState[i] <= previousState[i] for i in range(self.numBuckets))
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
        return message
        
    def A_Star(self):
        open_set = []
        close_set = set()
        ancestor = defaultdict(list)

        start_state = State(self.initBucket, 0, self.countMahattan(self.initBucket))
        heapq.heappush(open_set, (start_state.f, start_state))
        
        while open_set:
            _, current_state = heapq.heappop(open_set)

            if current_state.bucket[-1] == self.targetBucket:
                self.lastState= current_state.bucket
                st.write("\n\n\nSolution found!\n\n\n")
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
            st.write("\n\n\nNo solution exists!\n\n\n")
            return

        path = []
        currentBucket = tuple(self.lastState)

        while currentBucket != tuple(self.initBucket):
            path.append(tuple(currentBucket))
            currentBucket = tuple(ancestor[currentBucket])

        path.append(tuple(self.initBucket))

        path = path[::-1]

        solution = defaultdict()
        step = 1
        
        for i, bucket in enumerate(path):
            if i >= 1:
                action = self.checkAction(path[i-1], path[i])
                st.markdown("---")
                st.write(f"**Step {step}:** {action}")
                st.markdown("---")
                self.printBucket(bucket) 
                self.visualizeBucket(bucket)
                if i < len(path) - 1:
                    st.markdown("---")

                step += 1
            else:
                st.write(f"**Initial state:** ")
                self.printBucket(bucket)
                self.visualizeBucket(bucket)
                if len(path) > 1:
                    st.markdown("---")



        solution[i] = bucket 

        return solution

default_num_buckets = 3
default_target_bucket = 17
default_bucket_capacity = "7 8 9"

numBucket = st.number_input("How many buckets in total? (e.g: 3)", min_value=1, step=1, value=default_num_buckets)
initBucket = [0] * (numBucket + 1)
targetBucket = st.number_input("How much water do you want? (e.g: 17)", min_value=1, step=1, value=default_target_bucket)
bucketCapacity = st.text_input("What are your capacities? (Enter values separated by space) (e.g: 7 8 9)", value=default_bucket_capacity)

if st.button("Run"):
    bucketCapacity = list(map(int, bucketCapacity.split()))
    graph = Graph(initBucket, targetBucket, bucketCapacity)
    graph.A_Star()
