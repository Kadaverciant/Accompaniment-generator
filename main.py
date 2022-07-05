import random
from mido import MidiFile, Message, MidiTrack, MetaMessage
from random import randint, shuffle
import copy

# INPUT_FILE_NAME = r'...\barbiegirl.mid'  # insert the absolute path to the midi file
INPUT_FILE_NAME = 'input3.mid'  # or use just the file name if it is stored in the same folder as the code being run
OUTPUT_FILE_NAME = 'VsevolodKlyushevOutput3.mid'
MUTATION = 1
CROSSOVER = 0.6
NUM_OF_GENERATIONS = 100
POPULATION_SIZE = 1000
INTERVALS = [5, 7, 3, 4, 8, 9]
CONSONANT = [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0]
DELTA = 24
MIN_NOTE = 0
VELOCITY = 100
TEMPO = 0
MELODY_NOTES = []


def fitness(individual):
    """
    This function calculates the fitness value of a certain chord sequence from individual with respect to the original
    melody.
    :param individual: an individual which is a dictionary containing both notes from the melody and generated chords
    for accompaniment.
    :return: a floating-point number that evaluates how good the accompaniment is in relation to the melody.
    """
    fitness_val = 0
    for elem in individual:
        i = elem.get('tritone')
        sorted_tritone = copy.copy(sorted(i))
        set_of_notes = set(sorted_tritone)
        note_1 = sorted_tritone.pop()
        note_2 = sorted_tritone.pop()
        note_3 = sorted_tritone.pop()
        consonant_score = 0
        k = 0
        for note in elem.get('notes'):
            notes_score = 0
            k += 1
            notes_score += CONSONANT[abs(note - note_1) % 12]
            notes_score += CONSONANT[abs(note - note_2) % 12]
            notes_score += CONSONANT[abs(note - note_2) % 12]
            consonant_score += notes_score
        if k == 0:
            k = 1/3
            consonant_score = 1
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
        if (note_1 - note_3) > 12:
            cord_score = 0
        if 3 != len(set_of_notes):
            cord_score = 0
        if note_1 >= octave + DELTA or note_2 >= octave + DELTA or note_3 >= octave + DELTA \
                or note_1 < MIN_NOTE - DELTA or note_2 < MIN_NOTE - DELTA or note_3 < MIN_NOTE - DELTA:
            cord_score = 0
        melody_score = 0
        if note_1 % 12 in MELODY_NOTES:
            melody_score += 1/3
        if note_2 % 12 in MELODY_NOTES:
            melody_score += 1/3
        if note_3 % 12 in MELODY_NOTES:
            melody_score += 1/3
        fitness_val += cord_score * consonant_score * melody_score
    return fitness_val


def mutation(individual):
    """
    This function produces some mutations on the sequence of chords from given individual.
    :param individual: an individual which is a dictionary containing generated chords for accompaniment.
    """
    for elem in individual:
        elem.get('tritone')[0] = (elem.get('tritone')[0] + randint(-7, 7)) % (octave + DELTA + 1)
        elem.get('tritone')[1] = (elem.get('tritone')[1] + randint(-7, 7)) % (octave + DELTA + 1)
        elem.get('tritone')[2] = (elem.get('tritone')[2] + randint(-7, 7)) % (octave + DELTA + 1)


def crossover(population):
    """
    This function produces list of offsprings between individuals in given population.
    :param population: list of individuals which are dictionary objects that contain all the information necessary to
    create some accompaniment for the initial melody.
    :return: a list of offsprings which are dictionary objects that was produced by crossover operation between
    individuals from population.
    """
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
    """
    This function produces a series of crosses and samples over a given population consisting of dictionary-type
    elements, each of which contains the information required to create an accompaniment.
    :param population_for_evolution: a list of individuals which are dictionary objects.
    :param generations: a number of required amount of crossovers and samples of population.
    :return: a population which is list of dictionary-type elements.
    """
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


def retrieve_information():
    """
    This function retrieve all necessary information from midi file and generate frame for individual in population.
    :return: mid - object which contain information about initial melody,
    gen - frame for individual with information about notes in initial melody at certain time,
    octave - some offset which indicates in what octaves we can generate melody,
    tritone_len - time variable which indicates how long each tritone would play.
    """
    mid = MidiFile(INPUT_FILE_NAME, clip=True)
    total_time = 0
    song_msg = []
    velocity = 0
    tempo = 0
    tritone_len = mid.ticks_per_beat * 2
    min_note = 999
    increased = 0
    for track in mid.tracks:
        for msg in track:
            # print(msg)
            if msg.type == 'note_on' or 'note_off':
                total_time += msg.time
                if msg.type == 'note_on' and msg.note < min_note:
                    min_note = msg.note
                    velocity = msg.velocity
                if msg.type == 'note_on' and msg.note % 12 not in MELODY_NOTES:
                    MELODY_NOTES.append(msg.note % 12)
                if msg.type == 'note_off' and msg.time >= tritone_len and increased == 0:
                    tritone_len *= 2
                    increased = 1
                song_msg.append(msg.copy())
            if msg.type == 'set_tempo':
                tempo = msg.tempo
    octave = (min_note // 12 - 2) * 12
    gen = [{'notes': [], 'time': (i + 1) * tritone_len, 'tritone': []} for i in range(total_time // tritone_len)]
    for track in mid.tracks:
        cur_time = 0
        ptr = 0
        length = len(song_msg)
        cur_notes = []
        for elem in gen:
            notes = elem.get('notes')
            notes += cur_notes
            finish_time = elem.get('time')
            while length > ptr+1 and cur_time + song_msg[ptr].time <= finish_time:
                ptr += 1
                msg = song_msg[ptr]
                cur_time += msg.time
                if msg.type == 'note_on':
                    if cur_time != finish_time:
                        if msg.note not in notes:
                            notes.append(msg.note)
                    else:
                        if msg.note not in cur_notes:
                            cur_notes.append(msg.note)
                else:
                    if msg.type == 'note_off' and msg.note in cur_notes:
                        cur_notes.remove(msg.note)
    return mid, gen, octave, tritone_len, min_note, velocity, tempo


def generate_population(template):
    """
    This function generates population, each of individuals of which is based on given template.
    :param template: a template, on which each individual from future population would be based.
    :return: population - list of individuals
    """
    population = []
    for i in range(POPULATION_SIZE):
        a = copy.deepcopy(template)
        population.append(a)
    for j in population:
        for i in j:
            val = random.sample(range(0, DELTA-1), 3)
            i.get('tritone').append(val.pop() + octave)
            i.get('tritone').append(val.pop() + octave)
            i.get('tritone').append(val.pop() + octave)
    return population


def save_melody_with_accompaniment():
    """
    This functions stores melody with accompaniment.
    """
    accompaniment = MidiFile()
    accompaniment_track = MidiTrack()
    full_song = MidiFile()
    best_accompaniment = population[0]
    print(fitness(best_accompaniment))
    if TEMPO != 0:
        accompaniment_track.append(MetaMessage('set_tempo', tempo=TEMPO, time=0))
    accompaniment_track.append(MetaMessage('track_name', name='Elec. Piano (Classic)', time=0))
    for elem in best_accompaniment:
        tritone = elem.get('tritone')
        accompaniment_track.append(Message('note_on', note=tritone[0], velocity=VELOCITY, time=0))
        accompaniment_track.append(Message('note_on', note=tritone[1], velocity=VELOCITY, time=0))
        accompaniment_track.append(Message('note_on', note=tritone[2], velocity=VELOCITY, time=0))
        accompaniment_track.append(Message('note_off', note=tritone[0], velocity=VELOCITY, time=tritone_len))
        accompaniment_track.append(Message('note_off', note=tritone[1], velocity=VELOCITY, time=0))
        accompaniment_track.append(Message('note_off', note=tritone[2], velocity=VELOCITY, time=0))
    accompaniment.tracks.append(accompaniment_track)
    # accompaniment.save('accompaniment.mid')
    for track in mid.tracks:
        full_song.tracks.append(track)
    full_song.tracks.append(accompaniment_track)
    full_song.save(OUTPUT_FILE_NAME)


mid, template, octave, tritone_len, MIN_NOTE, VELOCITY, TEMPO = retrieve_information()
population = generate_population(template)
population = evolution(population, NUM_OF_GENERATIONS)
save_melody_with_accompaniment()