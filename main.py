import random

import mido
from mido import MidiFile, Message, MidiTrack
from random import randint
import copy

MUTATION = 1
CROSSOVER = 0.7
NUMOFGENERATIONS = 100
POPULATIONSIZE = 1000
INTERVALS = [5, 7, 3, 4, 8, 9]


def consonant(first, second):
    value = abs(first - second) % 12
    cost = {
        0: 1,
        1: 0.1,
        2: 0.1,
        3: 0.7,
        4: 0.7,
        5: 0.8,
        6: 0.1,
        7: 0.8,
        8: 0.8,
        9: 0.6,
        10: 0.1,
        11: 0.1
    }.get(value)
    return cost


def fitness(gen):
    cordScore = 0
    for elem in gen:
        notesScore = 1
        for note in elem.get('notes'):
            for i in elem.get('triton'):
                notesScore *= consonant(note, i)
                # print(notesScore)
        cordScore += notesScore
        # print(f"result: ", cordScore)

    # polynoms = []
    # for i in range(len(gen)-1):
    #     elem = gen[i]
    #     for i in elem.get('triton'):
    #         a = sorted(i)
    #         polynom = 144*a.pop() + 12 * a.pop() + a.pop()
    #         polynoms.append(polynom)

    intervalValue = 1
    for elem in gen:
        i = elem.get('triton')
        # print(i)
        a = copy.copy(sorted(i))
        b = set(a)
        # print(a,b)
        n1 = a.pop()
        n2 = a.pop()
        n3 = a.pop()
        if (n1 - n3) > 12:
            cordScore = 0
        # if (n1 - n3) == 12:
        #     cordScore *= 1.2
        setOfIntervals = [n2 - n1, n3 - n2, (n1 - n3 + 12) % 12]
        bad = 0
        for interval in setOfIntervals:
            if interval not in INTERVALS:
                bad = 1
                intervalValue /= 1.05
        if (bad == 0):
            intervalValue *= 1.3
        # polynom = (144*a.pop() + 12 * a.pop() + a.pop())
        # polynoms.append(polynom)
        if (3 != len(b)):
            cordScore = 0

    # unique = set(polynoms)
    # if len(unique) != len(polynoms):
    #     cordScore = 0
    return cordScore*intervalValue


def mutation(gen):
    for elem in gen:
        # print(elem)
        elem.get('triton')[0] = (elem.get('triton')[0] + randint(-7, 7))
        elem.get('triton')[1] = (elem.get('triton')[1] + randint(-7, 7))
        elem.get('triton')[2] = (elem.get('triton')[2] + randint(-7, 7))


def crossover(population):
    parents = [[population[i], population[i + 1]] for i in range(0, len(population), 2)]
    children = []
    for par1, par2 in parents:
        childM = []
        child = []
        for i in range(len(par1)):
            if random.uniform(0, 1) <= CROSSOVER:
                childM.append(copy.deepcopy(par1[i]))
                child.append(copy.deepcopy(par1[i]))
            else:
                childM.append(copy.deepcopy(par2[i]))
                child.append(copy.deepcopy(par2[i]))
        if random.uniform(0, 1) <= MUTATION:
            mutation(childM)
        children.append(child)
        children.append(childM)
    return children


def evolution(population, generations):
    for i in range(generations):
        print(i)
        parentFitness = [fitness(gen) for gen in population]
        populationWithFitness = [{'fitness': parentFitness[i], 'population': population[i]} for i in
                                 range(len(population))]
        children = crossover(population)
        childrenFitness = [fitness(gen) for gen in children]
        childrenWithFitness = [{'fitness': childrenFitness[i], 'population': children[i]} for i in range(len(children))]
        populationWithFitness += childrenWithFitness
        # for k in populationWithFitness:
        #     print(k)
        # print('Childrens:')
        # for k in childrenWithFitness:
        #     print(k)
        populationWithFitness.sort(key=lambda x: -x.get('fitness'))
        # print('initial')
        # for k in population:
        #     print(k)
        # print('crossover')
        # for k in populationWithFitness:
        #     print(k)
        size = len(population)
        population = [populationWithFitness[i].get('population') for i in range(size)]
        # print('after')
        # for k in population:
        #     print(k)
    return population


mid = MidiFile('barbiegirl.mid', clip=True)
totalTime = 0
songMSG = []
q = mid.ticks_per_beat * 2  # 1/2 of tact

for track in mid.tracks:
    for msg in track:
        # print(msg)
        totalTime += msg.time
        songMSG.append(msg.copy())

gen = [{'notes': [], 'time': (i + 1) * q, 'triton': []} for i in range(totalTime // q)]

for track in mid.tracks:
    curTime = 0
    ptr = 0
    length = len(songMSG)
    curNotes = []
    for elem in gen:
        notes = elem.get('notes')
        notes += curNotes
        finishTime = elem.get('time')
        while length > ptr and curTime + songMSG[ptr].time <= finishTime:
            ptr += 1
            msg = songMSG[ptr]
            curTime += msg.time
            # print(msg.type)
            if msg.type == 'note_on':
                if curTime != finishTime:
                    if msg.note not in notes:
                        notes.append(msg.note)
                else:
                    if msg.note not in curNotes:
                        curNotes.append(msg.note)
            else:
                if msg.type == 'note_off' and msg.note in curNotes:
                    curNotes.remove(msg.note)

population = []
for i in range(POPULATIONSIZE):
    a = copy.deepcopy(gen)
    population.append(a)

for j in population:
    for i in j:
        val = random.sample(range(0, 23), 3)
        i.get('triton').append(val.pop())
        i.get('triton').append(val.pop())
        i.get('triton').append(val.pop())
        # print(i)
    # fitnesses.append(fitness(j))
    # mutation(j)
    # fitnessesM.append(fitness(j))

# for i in population:
#     print(i)
#
population = evolution(population, NUMOFGENERATIONS)
# print('----')
# for i in population:
#     print(fitness(i),i)
# print(max(fitnesses))
# print(max(fitnessesM))
# w = population.pop()
# print(w[1])
# print(w)
# print(fitness(w))

accompaniment = MidiFile()
accompanimentTrack = MidiTrack()
fullSong = MidiFile()

bestAccompaniment = population[0]
print(fitness(bestAccompaniment))
octave = 3 * 12
for elem in bestAccompaniment:
    sTime = elem.get('time')
    triton = elem.get('triton')
    accompanimentTrack.append(Message('note_on', note=triton[0] + octave, time=0))
    accompanimentTrack.append(Message('note_on', note=triton[1] + octave, time=0))
    accompanimentTrack.append(Message('note_on', note=triton[2] + octave, time=0))
    accompanimentTrack.append(Message('note_off', note=triton[0] + octave, time=q))
    accompanimentTrack.append(Message('note_off', note=triton[1] + octave, time=0))
    accompanimentTrack.append(Message('note_off', note=triton[2] + octave, time=0))

accompaniment.tracks.append(accompanimentTrack)
accompaniment.save('accompaniment.mid')
for track in mid.tracks:
    fullSong.tracks.append(track)
fullSong.tracks.append(accompanimentTrack)
fullSong.save('fullSong.mid')
