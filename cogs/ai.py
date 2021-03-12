from discord.ext import commands
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
import nltk
import discord as ds
from functions import *
import difflib
import random
import json


class AI(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.bot_func = bot_functions()
        self.stemmer = LancasterStemmer()
        self.valid_channels = [self.bot.bot_commands_test_chan, self.bot.bot_commands_chan]
        self.last_response_tag = ''

        # settings
        with open("intents.json") as file:
            self.phrase_data = json.load(file)
        self.similarity_req = self.phrase_data['settings']['similarity_req']
        self.debug = self.phrase_data['settings']['debug']

        # load stop words
        with open("stopwords.txt", "r") as f:
            self.stopwords = set(f.read())


    def simpilify_phrase(self, sentence):
        '''
        Uses NLTK and a stopwords list to stem and shorten
        the inputted sentence to remove unneeded information.

        Arguments:

        sentence -- sentence is simplified
        '''
        sentence = self.stemmer.stem(sentence.lower())
        word_tokens = word_tokenize(sentence)
        filtered_sentence = [w for w in word_tokens if not w in self.stopwords]
        filtered_sentence = []
        for w in word_tokens:
            if w not in self.stopwords:
                filtered_sentence.append(w)
        return filtered_sentence


    def phrase_matcher(self, phrase):
        '''Matches phrases to patterns in intent.json

        Arguments:

        phrase -- phrase that is checked for best match
        '''
        intents = self.phrase_data['intents']
        # switch to giving max_similarity self.similarity_req
        max_similarity = 0
        matched_pattern = ''
        best_response = ''
        prepped_phrase = self.simpilify_phrase(phrase)
        for item in intents:
            for pattern in item['patterns']:
                prepped_pattern = self.simpilify_phrase(pattern)
                similarity = difflib.SequenceMatcher(None, prepped_pattern, prepped_phrase).ratio()
                if similarity > max_similarity and similarity > self.similarity_req:
                    max_similarity = similarity
                    matched_pattern = pattern.lower()
                    best_response = item
        if best_response == '':
            return
        if self.debug:
            print(phrase)
            print(f'Final pick is: {best_response["tag"]} with similarity: {max_similarity}\n{matched_pattern}\n')
        return best_response


    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        On message reaction.
        '''
        bot_id = str(812257484734988299)
        if message.author == self.bot.user:  # Ignore messages made by the bot
            return
        if message.channel.id in self.valid_channels or bot_id in message.content:
            data_dict = self.phrase_matcher(message.clean_content)
            if data_dict == None:
                return
            if 'context_set' in data_dict.keys():
                if data_dict['context_set'] != self.last_response_tags:
                    return
            if 'tag' in data_dict.keys():
                self.last_response_tags = data_dict['tag']
            if len(data_dict['responses']) > 1:
                if 'weighted' in data_dict.keys():
                    response = random.choices(data_dict['responses'], weights=(data_dict['weighted']))[0]
                else:
                    response = random.choice(data_dict['responses'])
            elif len(data_dict['responses']) == 1:
                response = data_dict['responses'][0]
            else:
                print('No responses.')
                return
            # sends message
            if '@' in response:
                response = response.replace('@', str(message.author.display_name))
            if response != '':
                await message.channel.send(response)


def setup(bot):
    bot.add_cog(AI(bot))
