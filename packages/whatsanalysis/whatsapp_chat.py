"""
This is the fundamental set of classes and functions for the analysis of WhatsApp conversations.
"""

import numpy as np  # fundamental data analysis and plotting packages
import pandas as pd
from datetime import datetime  # package to deal with the dates and times of the messages
import matplotlib.pyplot as plt

def is_message(entry):
    return entry['type']=='message'

def is_message_or_media(entry):
    return (entry['type']=='message') | (entry['type']=='media')

def is_media(entry):
    return entry['type']=='media'

def is_event(entry):
    return entry['type']=='event'

class WhatsAppChat:
    def __init__(self, file_name):
        self.file_name = file_name  # The file name of the exported whatsapp conversation.
        self.file_to_dataframe()

    def file_to_dataframe(self):
        """This is internal use only"""

        chat = []
        with open(self.file_name, 'r') as ins:
            for line in ins:
                datetime_str = line[:17] #The first part of each new message contains the date/time
                try:
                    time = datetime.strptime(datetime_str, '%d/%m/%Y, %H:%M')
                    new_message = True
                except ValueError:      #If it is not of the date time format, then that means it is a continuation of
                    new_message = False #the previous message, so just need to append the text to the last entry.

                if new_message:
                    main_part = line[20:] #The `main_part' contains the person writing the message and the message, sep
                    main_part_separated = main_part.split(':', 1) #by a :. If there is no colon then this is an event
                    if len(main_part_separated) == 2: #Decide on the type of entry, either message, media or event
                        if '<Media omitted>' in main_part_separated[1].strip():
                            entry = {
                                'time': time,
                                'name': main_part_separated[0].strip(),
                                'type': 'media'
                            }
                        else:
                            entry = {
                                'time': time,
                                'name': main_part_separated[0].strip(),
                                'text_original': main_part_separated[1].strip(),
                                'text_lowercase': main_part_separated[1].strip().lower(),
                                'type': 'message'
                            }
                    else:
                        entry = {
                            'time': time,
                            'text_original': main_part_separated[0].strip(),
                            'text_lowercase': main_part_separated[0].strip().lower(),
                            'type': 'event'
                        }
                    chat.append(entry)
                else:
                    additional_text = line
                    chat[-1]['text_original'] = (chat[-1]['text_original'] + ' ' + additional_text).strip()
                    chat[-1]['text_lowercase'] = (chat[-1]['text_lowercase'] + ' ' + additional_text.lower()).strip()

        self.chat = pd.DataFrame(chat)
        self.chat['ordinal_time'] = self.chat.time.apply(datetime.toordinal)

    def find_people(self):
        """find unique people in the chat, and calculate some basic properties about them"""
        self.people = self.chat.groupby(['name']) #Group messages by person
        print self.people.describe()

    def plot_messages_over_time(self, person='all', ax=None, bins=10, range=None, **kwargs):
        """plot the number of messages and the messages rate over time for a given person, or all people.
        person='all' plots every person
        person='total' plots the total messages over time
        person=array-of-names plots for the people named in the array
        person=name plots for just that person"""
        if ax==None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        ax_rate = ax.twinx()

        all_messages = self.chat[is_message_or_media(self.chat)]['ordinal_time']
        n_all_messages, bins = np.histogram(all_messages,bins=bins, range=range)

        if person=='all':
            for p,entries in self.people:
                messages = entries[is_message_or_media(entries)]['ordinal_time']
                n_person, bins_person, patches_person = ax.hist(messages, bins=bins, **kwargs)
                center_person = 0.5*(bins_person[:-1] + bins_person[1:])
                ax_rate.plot(center_person, n_person/n_all_messages, label=p)
        elif person=='total':
            ax.hist(all_messages, bins=bins)
        else:
            for p in person:
                entries = self.people.get_group(p)
                messages = entries[is_message_or_media(entries)]['ordinal_time']
                n_person, bins_person, patches_person = ax.hist(messages, bins=bins, **kwargs)
                center_person = 0.5*(bins_person[:-1] + bins_person[1:])
                ax_rate.plot(center_person, n_person/n_all_messages, label=p)

        ax_rate.legend()
        x_ticks = ax.get_xticks()
        ax.set_xticks(x_ticks)
        xlabels = [datetime.fromordinal(int(x)).strftime('%Y-%m-%d') for x in x_ticks]
        ax.set_xticklabels(xlabels)
