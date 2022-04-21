import random

from mido import MidiFile, Message, MidiTrack
from random import randint, shuffle
import copy

MUTATION = 1
CROSSOVER = 0.6
NUMOFGENERATIONS = 100
POPULATIONSIZE = 1000
INTERVALS = [5, 7, 3, 4, 8, 9]
CONSONANT = [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0]
OFFSET = 0

def fitness(gen):
    fitnessVal = 0
    for elem in gen:
        i = elem.get('triton')
        a = copy.copy(sorted(i))
        b = set(a)
        n1 = a.pop()
        n2 = a.pop()
        n3 = a.pop()
        n = 0
        k = 0
        for note in elem.get('notes'):
            notesScore = 0
            k+= 1
            notesScore += CONSONANT[abs(note - n1) % 12]
            notesScore += CONSONANT[abs(note - n2) % 12]
            notesScore += CONSONANT[abs(note - n2) % 12]
            n += notesScore
        n /= (3*k)
        cordScore = 0
        setOfIntervals = [n1 - n2, n2 - n3, (n3 - n1 + 12) % 12]
        bad = 0
        for interval in setOfIntervals:
            if interval in INTERVALS:
                cordScore += 1
            else:
                bad = 1
        if bad == 1:
            cordScore = 0

        if (n1 - n3) > 13:
            cordScore = 0
        if 3 != len(b):
            cordScore = 0
        if n1 > OFFSET + 12  or n2 > OFFSET + 12  or n3 > OFFSET + 12:
            cordScore = 0
        fitnessVal += cordScore*n
    return fitnessVal

def mutation(gen):
    for elem in gen:
        elem.get('triton')[0] = elem.get('triton')[0] + (elem.get('triton')[0] + randint(-7, 7)) % OFFSET
        elem.get('triton')[1] = elem.get('triton')[1] + (elem.get('triton')[0] + randint(-7, 7)) % OFFSET
        elem.get('triton')[2] = elem.get('triton')[2] + (elem.get('triton')[0] + randint(-7, 7)) % OFFSET

def crossover(population):
    parents = [[population[i], population[i + 1]] for i in range(0, len(population), 2)]
    children = []
    for par1, par2 in parents:
        childM = []
        child = []
        if fitness(par2) > fitness(par1):
            par1, par2 = par2, par1
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
        print(i+1, fitness(population[0]))
        shuffle(population)
        parentFitness = [fitness(gen) for gen in population]
        populationWithFitness = [{'fitness': parentFitness[i], 'population': population[i]} for i in
                                 range(len(population))]
        children = crossover(population)
        childrenFitness = [fitness(gen) for gen in children]
        childrenWithFitness = [{'fitness': childrenFitness[i], 'population': children[i]} for i in range(len(children))]
        populationWithFitness += childrenWithFitness
        populationWithFitness.sort(key=lambda x: -x.get('fitness'))
        size = len(population)
        population = [populationWithFitness[i].get('population') for i in range(size)]
    return population


mid = MidiFile('barbiegirl.mid', clip=True)
totalTime = 0
songMSG = []
q = mid.ticks_per_beat * 2  # 1/2 of tact
minNote = 999
for track in mid.tracks:
    for msg in track:
        totalTime += msg.time
        if msg.type == 'note_on' and msg.note < minNote:
            minNote = msg.note
        songMSG.append(msg.copy())

octave = (minNote // 12 - 1) * 12
OFFSET = octave

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
        val = random.sample(range(0, 11), 3)
        i.get('triton').append(val.pop() + octave)
        i.get('triton').append(val.pop() + octave)
        i.get('triton').append(val.pop() + octave)

population = evolution(population, NUMOFGENERATIONS)

accompaniment = MidiFile()
accompanimentTrack = MidiTrack()
fullSong = MidiFile()

bestAccompaniment = population[0]
print(fitness(bestAccompaniment))

for elem in bestAccompaniment:
    sTime = elem.get('time')
    triton = elem.get('triton')
    accompanimentTrack.append(Message('note_on', note=triton[0], time=0))
    accompanimentTrack.append(Message('note_on', note=triton[1], time=0))
    accompanimentTrack.append(Message('note_on', note=triton[2], time=0))
    accompanimentTrack.append(Message('note_off', note=triton[0], time=q))
    accompanimentTrack.append(Message('note_off', note=triton[1], time=0))
    accompanimentTrack.append(Message('note_off', note=triton[2], time=0))

accompaniment.tracks.append(accompanimentTrack)
accompaniment.save('accompaniment.mid')
for track in mid.tracks:
    fullSong.tracks.append(track)
fullSong.tracks.append(accompanimentTrack)
fullSong.save('fullSong.mid')
