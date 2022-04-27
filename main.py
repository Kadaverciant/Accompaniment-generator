import random

from mido import MidiFile, Message, MidiTrack
from random import randint, shuffle
import copy

MUTATION = 1
CROSSOVER = 0.6
NUM_OF_GENERATIONS = 100
POPULATION_SIZE = 1000
INTERVALS = [5, 7, 3, 4, 8, 9]
CONSONANT = [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0]
OFFSET = 0
DELTA = 24
MIN_NOTE = 0


def fitness(gen):
    fitness_val = 0
    for elem in gen:
        i = elem.get('triton')
        sorted_triton = copy.copy(sorted(i))
        set_of_notes = set(sorted_triton)
        note_1 = sorted_triton.pop()
        note_2 = sorted_triton.pop()
        note_3 = sorted_triton.pop()
        consonant_score = 0
        k = 0
        for note in elem.get('notes'):
            notes_score = 0
            k += 1
            notes_score += CONSONANT[abs(note - note_1) % 12]
            notes_score += CONSONANT[abs(note - note_2) % 12]
            notes_score += CONSONANT[abs(note - note_2) % 12]
            consonant_score += notes_score
        consonant_score /= (3*k)
        cord_score = 0
        set_of_intervals = [note_1 - note_2, note_2 - note_3, (note_3 - note_1 + 12) % 12]
        bad = 0
        for interval in set_of_intervals:
            if interval in INTERVALS:
                cord_score += 1
            else:
                bad = 1
        if bad == 1:
            cord_score = 0
        if (note_1 - note_3) > 13:
            cord_score = 0
        if 3 != len(set_of_notes):
            cord_score = 0
        if note_1 > OFFSET + DELTA or note_2 > OFFSET + DELTA or note_3 > OFFSET + DELTA or note_1 < MIN_NOTE - DELTA \
                or note_2 < MIN_NOTE - DELTA or note_3 < MIN_NOTE - DELTA:
            cord_score = 0
        fitness_val += cord_score*consonant_score
    return fitness_val


def mutation(gen):
    for elem in gen:
        elem.get('triton')[0] = (elem.get('triton')[0] + randint(-7, 7)) % (OFFSET + DELTA + 1)
        elem.get('triton')[1] = (elem.get('triton')[1] + randint(-7, 7)) % (OFFSET + DELTA + 1)
        elem.get('triton')[2] = (elem.get('triton')[2] + randint(-7, 7)) % (OFFSET + DELTA + 1)


def crossover(population):
    parents = [[population[i], population[i + 1]] for i in range(0, len(population), 2)]
    children = []
    for par1, par2 in parents:
        child_mut = []
        child = []
        if fitness(par2) > fitness(par1):
            par1, par2 = par2, par1
        for i in range(len(par1)):
            if random.uniform(0, 1) <= CROSSOVER:
                child_mut.append(copy.deepcopy(par1[i]))
                child.append(copy.deepcopy(par1[i]))
            else:
                child_mut.append(copy.deepcopy(par2[i]))
                child.append(copy.deepcopy(par2[i]))
        if random.uniform(0, 1) <= MUTATION:
            mutation(child_mut)
        children.append(child)
        children.append(child_mut)
    return children


def evolution(population_for_evolution, generations):
    for i in range(generations):
        print(i + 1, fitness(population_for_evolution[0]))
        shuffle(population_for_evolution)
        parent_fitness = [fitness(gen) for gen in population_for_evolution]
        population_with_fitness = [{'fitness': parent_fitness[i], 'population': population_for_evolution[i]} for i in
                                   range(len(population_for_evolution))]
        children = crossover(population_for_evolution)
        children_fitness = [fitness(gen) for gen in children]
        children_with_fitness = [{'fitness': children_fitness[i], 'population': children[i]} for i in range(len(children))]
        population_with_fitness += children_with_fitness
        population_with_fitness.sort(key=lambda x: -x.get('fitness'))
        size = len(population_for_evolution)
        population_for_evolution = [population_with_fitness[i].get('population') for i in range(size)]
    return population_for_evolution


mid = MidiFile('barbiegirl.mid', clip=True)
total_time = 0
song_msg = []
q = mid.ticks_per_beat * 2  # 1/2 of tact
min_note = 999
for track in mid.tracks:
    for msg in track:
        total_time += msg.time
        if msg.type == 'note_on' and msg.note < min_note:
            min_note = msg.note
        song_msg.append(msg.copy())

octave = (min_note // 12 - 2) * 12
MIN_NOTE = min_note
print(min_note)
print(octave)
OFFSET = octave

gen = [{'notes': [], 'time': (i + 1) * q, 'triton': []} for i in range(total_time // q)]

for track in mid.tracks:
    cur_time = 0
    ptr = 0
    length = len(song_msg)
    cur_notes = []
    for elem in gen:
        notes = elem.get('notes')
        notes += cur_notes
        finishTime = elem.get('time')
        while length > ptr and cur_time + song_msg[ptr].time <= finishTime:
            ptr += 1
            msg = song_msg[ptr]
            cur_time += msg.time
            # print(msg.type)
            if msg.type == 'note_on':
                if cur_time != finishTime:
                    if msg.note not in notes:
                        notes.append(msg.note)
                else:
                    if msg.note not in cur_notes:
                        cur_notes.append(msg.note)
            else:
                if msg.type == 'note_off' and msg.note in cur_notes:
                    cur_notes.remove(msg.note)

population = []
for i in range(POPULATION_SIZE):
    a = copy.deepcopy(gen)
    population.append(a)


for j in population:
    for i in j:
        val = random.sample(range(0, 23), 3)
        i.get('triton').append(val.pop() + octave)
        i.get('triton').append(val.pop() + octave)
        i.get('triton').append(val.pop() + octave)

population = evolution(population, NUM_OF_GENERATIONS)

accompaniment = MidiFile()
accompaniment_track = MidiTrack()
full_song = MidiFile()

best_accompaniment = population[0]
print(fitness(best_accompaniment))

for elem in best_accompaniment:
    sTime = elem.get('time')
    triton = elem.get('triton')
    accompaniment_track.append(Message('note_on', note=triton[0], time=0))
    accompaniment_track.append(Message('note_on', note=triton[1], time=0))
    accompaniment_track.append(Message('note_on', note=triton[2], time=0))
    accompaniment_track.append(Message('note_off', note=triton[0], time=q))
    accompaniment_track.append(Message('note_off', note=triton[1], time=0))
    accompaniment_track.append(Message('note_off', note=triton[2], time=0))

accompaniment.tracks.append(accompaniment_track)
accompaniment.save('accompaniment.mid')
for track in mid.tracks:
    full_song.tracks.append(track)
full_song.tracks.append(accompaniment_track)
full_song.save('full_song.mid')
