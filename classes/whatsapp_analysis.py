"""
This is the fundamental set of classes and functions for the analysis of whatsapp conversations.
"""

import numpy as np  # fundamental data analysis and plotting packages
import pylab as plt
import pandas as pd
import datetime as datetime  # package to deal with the dates and times of the messages


class WhatsappConversation:
    def __init__(self, file_name):
        self.file_name = file_name  # The file name of the exported whatsapp conversation.

        self.conversation = []
        names = []
        with open(self.file_name, 'r') as ins:
            for line in ins:
                datetime_str = line[:17]
                try:
                    time = datetime.strptime(datetime_str, '%d/%m/%Y, %H:%M')
                    NewMessage = True
                except ValueError:
                    NewMessage = False

                if NewMessage:
                    main_part = line[20:]
                    main_part_separated = main_part.split(':', 1)
                    if len(main_part_separated) == 2:
                        message = {
                            'time': time,
                            'name': main_part_separated[0].strip(),
                            'text': main_part_separated[1].strip(),
                            'type': 'message'
                        }
                        names.append(message['name'])

                        self.conversation.append(message)
                    else:
                        message = {
                            'time': time,
                            'text': main_part_separated[0].strip(),
                            'type': 'event'
                        }
                        self.conversation.append(message)
                else:
                    additional_text = line
                    self.conversation[-1]['text'] = (self.conversation[-1]['text'] + ' ' + additional_text).strip()

        self.names = np.unique(names)
