import sys
from Token import tokenList
from Token.token import Token
from Parser.stringsWithArrows import *
import re

#  Copyright (c) 2021, Alden Authors.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of Alden Org. nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# File:
#   Lexer\lexer.py
# Author: 
#   Kehinde Akinsanya
# Created:
#   October 28, 2021
# Description:
#   This file contains the lexer class which is responsible for tokenizing the input file.


class Regex:
        def __init__(self):
            self.value = None

        def parse(self, text, pos_start, pos_end):
            wildcard_token = Token(tokenList.TT_WILDCARD, None, pos_start, pos_end)
            start_token = Token(tokenList.TT_START, None, pos_start, pos_end)
            end_token = Token(tokenList.TT_END, None, pos_start, pos_end)
            comma_token = Token(tokenList.TT_COMMA, None, pos_start, pos_end)
            arrow_token = Token(tokenList.TT_ARROW, None, pos_start, pos_end)
            plus_token = Token(tokenList.TT_PLUS, None, pos_start, pos_end)
            star_token = Token(tokenList.TT_STAR, None, pos_start, pos_end)
            question_token = Token(tokenList.QUESTION, None, pos_start, pos_end)
            pipe_token = Token(tokenList.TT_PIPE, None, pos_start, pos_end)
            
        def compile(self, pattern):
            self.pattern = re.compile(pattern)
            return self
        def match(self, text):
            return self.pattern.findall(text)
class Program:
    def error():
        def IllegalCharacter(options):
            error = f"\nFile: {options['pos_start'].fileName} at line {options['pos_start'].line + 1}\n\nSyntaxError: Illegal character unexpected  '{options['originator']}'\n"
            Program.printError(error)

        def Syntax(detail):
            isDetail = {
                'name': 'SyntaxError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))

        def Runtime(options):
            error = f'Runtime error {options["originator"]} at line {options["line"]}'
            Program.printError(error)
        methods = {
            'IllegalCharacter': IllegalCharacter,
            'Syntax': Syntax,
            'Runtime': Runtime
        }
        return methods

    def print(*args):
        for arg in args:
            print(arg)

    def printWithType(*args):
        for arg in args:
            print(str(type(arg)) + " <===> " + str(arg))

    def printError(*args):
        for arg in args:
            print(arg)
        #sys.exit(1)
        
    def printErrorExit(*args):
        for arg in args:
            print(arg)
        sys.exit(1)

    def asString(detail):
        result = f'\nFile {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}'
        result += '\n\n' +  \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        result += f'\n{detail["name"]}: {detail["message"]}'
        return result


class Lexer:
    def __init__(self, fileName, fileText, position=None, environment=None, module_name=None, fm_string=None):
        self.fileName = fileName
        self.fileText = fileText
        self.position = position
        self.environment = environment
        self.module_name = module_name
        self.fm_string = fm_string
        self.pos = Position(self.environment,
                            -1, 0, -1, fileName, fileText, "inter_p", self.position, self.module_name, self.fm_string)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.fileText[self.pos.index] if self.pos.index < len(self.fileText) else None

    def make_tokens(self, token=None):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == '#':
                self.make_comment()
            elif self.current_char in '\n':
                tokens.append(Token(tokenList.TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in tokenList.DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in tokenList.LETTERS_SYMBOLS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_double_string())
            elif self.current_char == "'":
                tokens.append(self.make_single_string())
            elif self.current_char == "`":
                tokens.append(self.make_backtick_string())
            elif self.current_char == '+':
                tokens.append(self.make_plus_or_plus_equal())
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow_or_minus_equal())
            elif self.current_char == '*':
                tokens.append(self.make_mul_or_mul_equal())
            elif self.current_char == '/':
                tokens.append(self.make_div_or_div_equal())
            elif self.current_char == '%':
                tokens.append(self.make_mod_or_mod_equal())
            elif self.current_char == '^':
                tokens.append(self.make_power_or_power_equal())
            elif self.current_char == ':':
                tokens.append(self.make_colon_or_type_assoc())
            elif self.current_char == '|':
                tokens.append(self.make_pipe_merge())
            elif self.current_char == '.':
                tokens.append(Token(tokenList.TT_DOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(tokenList.TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(tokenList.TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(tokenList.TT_LSQBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(tokenList.TT_RSQBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(tokenList.TT_LBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(tokenList.TT_RBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '~':
                tokens.append(Token(tokenList.TT_TILDE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '&':
                tokens.append(self.make_and())
            elif self.current_char == '!':
                tok, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == ',':
                    tokens.append(Token(tokenList.TT_COMMA, pos_start=self.pos))
                    self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], Program.error()['IllegalCharacter'](
                    {
                        'originator': char,
                        'pos_start': pos_start
                    })
        tokens.append(Token(tokenList.TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in tokenList.DIGITS + '.':
            
                
            if self.current_char == '.':
                
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
                
            else:
                
                num_str += self.current_char
                
            self.advance()
            # check for _ in the number, _ makes it easy to read long numbers e.g. 1_000_000
            if self.current_char == '_':
                num_str += self.current_char
                self.advance()
            # check if binary number
            if self.current_char == 'b':
                num_str += self.current_char
                self.advance()
                while self.current_char != None and self.current_char in '01':
                    num_str += self.current_char
                    self.advance()
                    # if self.current_char is not a valid binary number
                    if self.current_char not in '01':
                        if self.current_char in tokenList.LETTERS_DIGITS_SYMBOLS:
                            return None, Program.error()['Syntax']({
                            'pos_start': pos_start,
                            'pos_end': self.pos,
                            'message': 'Invalid binary number',
                            'exit': False
                        })
                            
                return Token(tokenList.TT_BINARY, int(num_str, 2), pos_start, self.pos)
            
        if dot_count == 0:
            return Token(tokenList.TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(tokenList.TT_FLOAT, float(num_str), pos_start, self.pos)
        
    def make_identifier(self):
        identifier_str = ''
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in tokenList.LETTERS_DIGITS_SYMBOLS:
            identifier_str += self.current_char
            self.advance()
        if identifier_str in tokenList.KEYWORDS:
            token_type = tokenList.TT_KEYWORD
        else:
            token_type = tokenList.TT_IDENTIFIER
        return Token(token_type, identifier_str, pos_start, self.pos)

    def make_dot(self):
        object_ref = ""
        pos_start = self.pos.copy()
        self.advance()
        while self.current_char != None and self.current_char in tokenList.LETTERS_DIGITS_SYMBOLS:
            object_ref += self.current_char
            self.advance() 
        return Token(tokenList.TT_OBJECT_REF, object_ref, pos_start, self.pos)
    
    def make_plus_or_plus_equal(self):
        tok_type = tokenList.TT_PLUS
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '+':
            self.advance()
            tok_type = tokenList.TT_PLUS_PLUS
        elif self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_PLUS_EQ
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_minus_or_arrow_or_minus_equal(self):
        tok_type = tokenList.TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            self.advance()
            tok_type = tokenList.TT_ARROW
        elif self.current_char == '-':
            self.advance()
            tok_type = tokenList.TT_MINUS_MINUS
        elif self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_MINUS_EQ
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_mul_or_mul_equal(self):
        tok_type = tokenList.TT_MUL
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_MUL_EQ
        elif self.current_char == '*':
            self.advance()
            tok_type = tokenList.TT_SPREAD
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_div_or_div_equal(self):
        tok_type = tokenList.TT_DIV
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_DIV_EQ
        elif self.current_char == '/':
            self.advance()
            if self.current_char == '=':
                self.advance()
                tok_type = tokenList.TT_FLOOR_DIV_EQ
            else:
                tok_type = tokenList.TT_FLOOR_DIV
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_mod_or_mod_equal(self):
        tok_type = tokenList.TT_MOD
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_MOD_EQ
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_power_or_power_equal(self):
        tok_type = tokenList.TT_POWER
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_POWER_EQ
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(tokenList.TT_NEQ, pos_start=pos_start, pos_end=self.pos), None
        # else if an identifier
        # elif self.current_char in tokenList.LETTERS_DIGITS_SYMBOLS:
        #     identifier = self.make_identifier()
        #     if identifier.matches(tokenList.TT_KEYWORD, 'in'):
        #         return Token(tokenList.TT_NOT_IN, pos_start=pos_start, pos_end=self.pos), None
        #     else:
        #         return None, Program.error()['Syntax']({
        #             'pos_start': pos_start,
        #             'pos_end': self.pos,
        #             'message': 'Invalid identifier',
        #             'exit': False
        #         })
        self.advance()
        return None, Program.error()['Syntax']({
            'pos_start': pos_start,
            'pos_end': self.pos,
            'message': 'invalid syntax',
            'exit': False
        })

    def make_equals(self):
        tok_type = tokenList.TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_EQEQ
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = tokenList.TT_LT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_LTE
        elif self.current_char == '<':
            self.advance()
            tok_type = tokenList.TT_LSHIFT
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = tokenList.TT_GT
        pos_start = self.pos.copy()
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_GTE
        elif self.current_char == '>':
            self.advance()
            tok_type = tokenList.TT_RSHIFT
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_and(self):
        tok_type = tokenList.TT_AND
        pos_start = self.pos.copy()
        self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_double_string(self):
        string = ''
        string_concat = ''
        character = True
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()
        escape_characters = {
            '\\': '\\',
            'n': '\n',
            't': '\t',
            '\es': "\\"
        }
        
        while self.current_char != None and (self.current_char != '"' or escape_character):
            if self.current_char == '\\':
                self.advance()
                if self.current_char in escape_characters:
                    string += escape_characters[self.current_char]
                else:
                    if self.current_char == '"':
                        string += '"'
                    else:
                        string += self.current_char
                        # Program.error()['Syntax']({
                        #     'pos_start': pos_start,
                        #     'pos_end': self.pos,
                        #     'message': 'Invalid escape character',
                        #     'exit': False
                        # })
                    
            else:
                if character:
                    if self.current_char == '\n':
                        return None, Program.error()['Syntax']({
                            'pos_start': pos_start,
                            'pos_end': self.pos,
                            'message': 'String literal is not closed',
                            'exit': False
                        })
                    string += self.current_char
                else:
                    string = ''
                    return Token(tokenList.TT_DOUBLE_STRING, string, pos_start, self.pos)
            self.advance()
            escape_character = False 
        if self.current_char == None:
            return None, Program.error()['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.pos,
                'message': "unterminated string literal",
                'exit': False
            })
        self.advance()
        return Token(tokenList.TT_DOUBLE_STRING, string, pos_start, self.pos)
   
    def make_single_string(self):
        string = ''
        character = True
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()
        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != "'" or escape_character):
            if self.current_char == '\\':
                self.advance()
                if self.current_char in escape_characters:
                    string += escape_characters[self.current_char]
                else:
                    character = False
                    if self.current_char == '"':
                        string += '"'
                    else:
                        string += self.current_char

            else:
                if character:
                    if self.current_char == '\n':
                        return None, Program.error()['Syntax']({
                            'pos_start': pos_start,
                            'pos_end': self.pos,
                            'message': 'String literal is not closed',
                            'exit': False
                        })
                    string += self.current_char
                else:
                    string = ''
                    return Token(tokenList.TT_SINGLE_STRING, string, pos_start, self.pos)
            self.advance()
            escape_character = False 
            
        if self.current_char == None:
            return None, Program.error()['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.pos,
                'message': "unterminated string literal",
                'exit': False
            })
        self.advance()
        return Token(tokenList.TT_SINGLE_STRING, string, pos_start, self.pos)

    def make_backtick_string(self):
        string = ''
        character = True
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()
        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '`' or escape_character):
            if self.current_char == '\\':
                self.advance()
                if self.current_char in escape_characters:
                    string += escape_characters[self.current_char]
                else:
                    if self.current_char == '"':
                        string += '"'
                    else:
                        string += self.current_char

            else:
                if character:
                    if self.current_char == '\n':
                        return None, Program.error()['Syntax']({
                            'pos_start': pos_start,
                            'pos_end': self.pos,
                            'message': 'String literal is not closed',
                            'exit': False
                        })
                    string += self.current_char
                else:
                    string = ''
                    return Token(tokenList.TT_BACKTICK_STRING, string, pos_start, self.pos)
            self.advance()
            escape_character = False 
            
        if self.current_char == None:
            return None, Program.error()['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.pos,
                'message': "unterminated string literal",
                'exit': False
            })
        self.advance()
        return Token(tokenList.TT_BACKTICK_STRING, string, pos_start, self.pos)    
      
    def make_colon_or_type_assoc(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == ':':
            self.advance()
            return Token(tokenList.TT_DOUBLE_COLON, '::', pos_start, self.pos)
        else:
            return Token(tokenList.TT_COLON, ':', pos_start, self.pos)
      
    def make_pipe_merge(self):
        tok_type = tokenList.TT_PIPE
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_MERGE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_comment(self):
        self.advance()
        while self.current_char != None and self.current_char != '\n':
            self.advance()



class Position:
    def __init__(self, environment, index, line, column, fileName, fileText, type=None, position=None, module_name=None, fm_string=None):
        self.environment = environment
        self.index = index
        self.line = line
        self.column = column
        self.fileName = fileName
        self.fileText = fileText
        self.type = type
        self.position = position
        self.module_name = module_name
        self.fm_string = fm_string
        if self.type == "inter_p" and self.position != None:
            self.line = self.position.line
            self.column = self.position.column - [ '\n' for i in range(self.position.column - self.index) ].count('\n') if self.position.column - [ '\n' for i in range(self.position.column - self.index) ].count('\n') == -1 else self.position.column
    def __repr__(self):
        return str({
            'index': self.index,
            'line': self.line,
            'column': self.column,
            'fileName': self.fileName,
            'fileText': self.fileText
        })

    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == '\n':
            self.line += 1
            self.column = 0

        return self

    def copy(self):
        return Position(self.environment,self.index, self.line, self.column, self.fileName, self.fileText, self.type, self.position, self.module_name, self.fm_string)

