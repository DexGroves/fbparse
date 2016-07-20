import json
import os
from lxml import html


class FacebookParser(object):
    """
    Parse the horrible Facebook data messages.htm into something more useful.
    Produces tab-delimited conversation logs in outpath.
    """

    def __init__(self, path, outpath='parsed_convos', lower_size_limit=500):
        self.lower_size_limit = lower_size_limit
        self.max_filename_len = 80
        self.outpath = outpath + '/'
        self.xmlp = XmlParser()

        self.create_output_dir_if_necessary(self.outpath)

        html_string = self.xmlp.get_html_string(path)
        tree = self.xmlp.get_xpath_tree(html_string)
        convos = self.xmlp.get_conversations(tree)

        conv_lists = [self.parse_convo(convo) for convo in convos]
        conv_dict = self.reduce_convos_by_authors(conv_lists)

        self.save_all_convos_to_files(conv_dict)

    def parse_convo(self, convo):
        parsed_convo = zip(self.xmlp.get_msg_author(convo),
                           self.xmlp.get_msg_txt(convo))
        return [(self.xmlp.delist(msg), self.xmlp.delist(txt))
                for [msg, txt] in parsed_convo]

    def reduce_convos_by_authors(self, conv_lists):
        convo_dict = {}
        for i in range(len(conv_lists)):
            convo = list(reversed(conv_lists[i]))
            author_str = self.get_convo_authors(convo)
            if author_str in convo_dict.keys():
                convo_dict[author_str] = convo_dict[author_str] + convo
            else:
                convo_dict[author_str] = convo
        return convo_dict

    def save_all_convos_to_files(self, conv_dict):
        for filename, convo in conv_dict.iteritems():
            if len(convo) > self.lower_size_limit:
                filename = self.reduce_filename_to_initials(filename)
                filepath = self.outpath + filename + '.json'
                filepath = self.increment_filename_if_exists(filepath)
                self.save_convo_to_file(convo, filepath)

    def reduce_filename_to_initials(self, filename):
        initials = '-'.join([self.get_initials(author)
                            for author in filename.split("-")])
        if len(initials) > self.max_filename_len - 7:
            return initials[:self.max_filename_len - 7] + '..'
        else:
            return initials

    @staticmethod
    def increment_filename_if_exists(filepath):
        if os.path.exists(filepath):
            filepath = filepath.replace('.json', '')
            incr = 2
            while os.path.exists(filepath + str(incr) + '.json'):
                incr += 1
            filepath = filepath + str(incr) + '.json'
        return filepath

    @staticmethod
    def save_convo_to_file(parsed_convo, filepath):
        with open(filepath, 'w') as outfile:
            json.dump(parsed_convo, outfile,  indent=4)

    @staticmethod
    def get_initials(author):
        return ''.join([w[0] for w in author.split(" ")])

    @staticmethod
    def get_convo_authors(convo):
        authors = [author for (author, msg) in convo if "@" not in author]
        authors = set(authors)
        return '-'.join(sorted(authors))

    @staticmethod
    def create_output_dir_if_necessary(output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)


class XmlParser(object):
    """Low-level utilities to parse messages.htm"""

    def __init__(self):
        pass

    @staticmethod
    def get_html_string(path):
        with open(path) as fb_html:
            html_string = fb_html.read()
        return html_string

    @staticmethod
    def get_xpath_tree(html_string):
        return html.fromstring(html_string)

    @staticmethod
    def get_conversations(tree):
        return tree.xpath('//div[@class="thread"]')

    @staticmethod
    def get_msg_author(convo):
        msgs = convo.xpath('div[@class="message"]' +
                           '/div[@class="message_header"]')
        return [msg.xpath('span[@class="user"]/text()') for msg in msgs]

    @staticmethod
    def get_msg_txt(convo):
        ps = convo.xpath('p')
        return [p.xpath('text()') for p in ps]

    @staticmethod
    def delist(xml_entry):
        if xml_entry == []:
            return ''
        return xml_entry[0]
