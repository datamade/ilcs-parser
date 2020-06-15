import os
import csv
import sys
from collections import OrderedDict

from lxml import etree
from parserator.data_prep_utils import TrainingData, list2file
from parserator.manual_labeling import printHelp, print_table, manualTagging

import ilcs_parser


def consoleLabel(raw_strings, labels, module):
    """
    Adapted from parserator to preserve order of strings. See:
    https://github.com/datamade/parserator/blob/4dc69b0d115bf33e2d169ff40b05143257a5f481/parserator/manual_labeling.py#L24-L74
    """
    print('\nStart console labeling!\n')
    valid_input_tags = OrderedDict([(str(i), label) for i, label in enumerate(labels)])
    printHelp(valid_input_tags)

    valid_responses = ['y', 'n', 's', 'f', '']
    finished = False

    strings_left_to_tag = raw_strings.copy()
    total_strings = len(raw_strings)

    # Use a list to preserve order of strings
    tagged_strings = []

    for i, raw_sequence in enumerate(raw_strings, 1):

        if not finished:

            print('\n(%s of %s)' % (i, total_strings))
            print('-'*50)
            print('STRING: %s' % raw_sequence)

            preds = module.parse(raw_sequence)

            user_input = None
            while user_input not in valid_responses:

                friendly_repr = [(token[0].strip(), token[1]) for token in preds]
                print_table(friendly_repr)

                sys.stderr.write('Is this correct? (y)es / (n)o / (s)kip / (f)inish tagging / (h)elp\n')
                user_input = sys.stdin.readline().strip()

                if user_input == 'y':
                    tagged_strings.append(tuple(preds))
                    strings_left_to_tag.remove(raw_sequence)

                elif user_input == 'n':
                    corrected_string = manualTagging(
                        preds,
                        valid_input_tags
                    )
                    tagged_strings.append(tuple(corrected_string))
                    strings_left_to_tag.remove(raw_sequence)

                elif user_input in ('h', 'help', '?'):
                    printHelp(valid_input_tags)

                elif user_input in ('' or 's'):
                    print('Skipped\n')
                elif user_input == 'f':
                    finished = True

    print('Done! Yay!')
    return tagged_strings, strings_left_to_tag


if __name__ == '__main__':
    infile = sys.argv[1]
    outfile = sys.argv[2]

    try:
        with open(outfile, 'r') as fobj:
            tree = etree.parse(fobj)
            xml = tree.getroot()
    except (OSError, IOError):
        xml = None
    except etree.XMLSyntaxError as e:
        if 'Document is empty' in str(e):
            xml = None
        else:
            raise(e)

    training_data = TrainingData(xml, ilcs_parser)

    with open(infile) as fobj:
        reader = csv.reader(fobj)
        strings = [row[0] for row in reader]

    labeled_list, raw_strings_left = consoleLabel(strings, ilcs_parser.LABELS, ilcs_parser)

    training_data.extend(labeled_list)

    with open(outfile, 'wb'):
        training_data.write(outfile)

    file_slug = os.path.basename(infile)
    if not file_slug.startswith('unlabeled'):
        file_slug = 'unlabeled_' + file_slug
    remainder_file = os.path.dirname(infile) + file_slug

    list2file(raw_strings_left, remainder_file)
