import numpy as np
import sys, os
import nltk
nltk.download('wordnet') # download wordnet, checks automatically so no need to catch errors.
from nltk.corpus import wordnet as wn

import argparse

parser = argparse.ArgumentParser(description='Data preprocessing for hypernyms in WordNet.')
parser.add_argument('--load', help="Toggle for loading numpy array if it exists.", action='store_true')
parser.add_argument('--data_dir', type=str, default='./', help='root data file directory')

def get_data(args, noun_list):

    # load numpy arrays if they already exists and load toggle on.
    if os.path.isfile(args.data_dir + 'links.npy') and os.path.isfile(args.data_dir + 'noun_hypernym_list.npy') and args.load:
        links = np.load('./links.npy')
        noun_hypernym_list = np.load('./noun_hypernym_list.npy')
        print('Loaded links.npy and noun_hypernym_list.npy.')
        
    else:
        # hypernym lambda functions
        hyper = lambda s: s.hypernyms()

        # we need to use dictionary for faster links search. (dict -> O(n), list.index() -> O(n^2))
        noun_list_dict = dict((value, idx) for idx, value in enumerate(noun_list))

        print('There are total of %i nouns in wordnet.' % len(noun_list))

        num_synsets = len(noun_list)
        links = []
        noun_hypernym_list = []

        # add (u, v) to links list if v is a hypernym of u
        for i, u in enumerate(noun_list):

            # closure outputs generator class! Use list here
            hyper_list = list(u.closure(hyper))

            # if hyper list is empty then skip
            if not hyper_list:
                noun_hypernym_list.append(None)
                sys.stdout.write('\r' + ('Processing word %i / %i' % (i, num_synsets)))
                sys.stdout.flush() 
                continue

            i_list = np.full((len(hyper_list)), i)
            code_list = [noun_list_dict[x] for x in hyper_list] # convert synsets to number labels
            links_list = np.stack((i_list, code_list), axis=-1)

            # append each u's hyernyms relation to noun_hypernym_list
            noun_hypernym_list.append(code_list)

            # append [u, v1], [u, v2], ... to links list. Use extend so we have shape (num_samples, 2) at the end.
            links.extend(links_list)

            sys.stdout.write('\r' + ('Processing word %i / %i' % (i, num_synsets)))
            sys.stdout.flush() 

        print('\n')
        print('There are %i training samples loaded.' % len(links))

        # save results to disk for faster loading next time.
        np.save(args.data_dir + 'links.npy', np.asarray(links))  
        np.save(args.data_dir + 'noun_hypernym_list.npy', np.asarray(noun_hypernym_list))
        print('Successfully saved links to links.npy and noun_hypernym_list to noun_hypernym_list.npy!')

    return links, noun_hypernym_list

if __name__ == "__main__":
    # args from parser
    args = parser.parse_args()
    # get the list of all synsets
    noun_list = list(wn.all_synsets('n'))
    _, _ = get_data(args, noun_list)
    

