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
#   Parser/parser.py
# Author: 
#   Kehinde Akinsanya
# Created:
#   October 28, 2021
# Description:
#   This file contains the parser for the language.


from os import access, error, path
from re import split
from types import NoneType

from Parser.stringsWithArrows import *
from Token.token import Token
from Token import tokenList
from Lexer.lexer import Lexer
import sys
import re
sys.path.append('./Parser/')
# def match(pattern, text, pos_start, pos_end):
#     matches = []
#     if len(pattern) == 0:
#         return matches
#     if len(text) == 0:
#         return matches
#     for i in len(text):
#         if pattern[0] == text[i]:
#             string = text.substring(i, i+1)
#             if len(pattern) == 1:
#                 matches.append(string)
#             else:
#                 matches.append(match(pattern[1:], text[i+1:], i+1, i+1))
#     return matches

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
        def sub(self, pattern, text):
            return self.pattern.sub(pattern, text)

def lower(text):
    return text.islower()

def isOnlyLetters(text):
    return text.isalpha()

def isFirstLetterUpper(text):
    return text[0].isupper()               


def has_at_symbol(text):
    if len(text) == 0:
        return False
    if text[0] == "@":
        return True
    return False



operation_methods = {
    'PLUS_EQ': 'add',
    'MINUS_EQ': 'sub',
    'MUL_EQ': 'mul',
    'DIV_EQ': 'div',
    'FLOOR_DIV_EQ': 'floor_div',
    'MOD_EQ': 'mod',
    'POWER_EQ': 'pow'
}    


class Program:
    def error():
        def Default(detail):
            if detail['exit']:
                Program.printErrorExit(Program.asString(detail))
            else:
                Program.printError(Program.asString(detail))

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
            error = f'RuntimeError: {options["originator"]}, line {options["line"]}'
            Program.printErrorExit(error)
            
        def NameError(detail):
            isDetail = {
                'name': 'NameError',
                'type': 'name error',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))
            
        def KeyError(detail):
            isDetail = {
                'name': 'KeyError',
                'type': 'key error',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))
                
        def ValueError(detail):
            isDetail = {
                'name': 'ValueError',
                'type': 'value error',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))
        methods = {
            'Default': Default,
            'Syntax': Syntax,
            'Runtime': Runtime,
            'NameError': NameError,
            'KeyError': KeyError,
            'ValueError': ValueError,
        }
        return methods

    def printWithType(*args):
        for arg in args:
            print(str(type(arg)) + " <===> " + str(arg))

    def printError(arg):
        print(arg)

    def printErrorExit(arg):
        print(arg)
        sys.exit(1)

    def asString(detail):
        result = f'\nFile {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}'
        result += '\n\n' +  \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        result += f'\n{detail["name"]}: {detail["message"]}'
        return result


class StatementsNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end


class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.id = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok, arg=None):
        self.name = tok
        self.tok = tok
        self.id = tok
        self.arg = arg
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringInterpNode:
    def __init__(self, expr, values_to_replace, string_to_interp, pos_start, pos_end, inter_pv=None):
        self.expr = expr
        self.values_to_replace = values_to_replace
        self.string_to_interp = string_to_interp
        self.inter_pv = inter_pv
        self.pos_start = pos_start
        self.pos_end = pos_end
        
    def __repr__(self):
        return f'{self.values_to_replace}'


class ListNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end


class PairNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

       
class PipeNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end 
    

class VarAssignNode:
    def __init__(self, variable_name_token, value_node, variable_keyword_token):
        self.variable_keyword_token = variable_keyword_token
        self.variable_name_token = variable_name_token
        self.id = variable_name_token
        self.value_node = value_node
        if type(self.variable_name_token).__name__ == "tuple":
            for t in self.variable_name_token:
                self.pos_start = t.pos_start
                self.pos_end = t.pos_end
        elif type(self.variable_name_token).__name__ == "list":
             for t in self.variable_name_token:
                self.pos_start = t.pos_start
                self.pos_end = t.pos_end


class VarAccessNode:
    def __init__(self, name, type=None):
        self.name = name
        self.id = name
        self.type = type
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class VarReassignNode:
    def __init__(self, name, value=None, operation=None, property=None):
        res = ParseResult()
        self.name = name
        self.id = name
        self.value = value
        self.operation = operation
        self.property = property
        
        if self.name == "" or self.name == None:
            pass
        else:
            self.pos_start = self.name.pos_start
            self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class PropertyNode:
    def __init__(self, name, property):
        self.name = name
        self.value = name.value if hasattr(name, 'value') else name
        self.id = name
        self.property = property
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end
        
    def __repr__(self):
        return f'{self.property}'
    

class PropertySetNode:
    def __init__(self, name, property, value, type_=None):
        self.name = name
        self.id = name
        self.property = property
        self.value = value
        self.type_ = type_
        self.pos_start = self.name.pos_start
        self.pos_end = self.value.pos_end if self.value != None else self.name.pos_end
        
    def __repr__(self):
        return f'{self.name}'


class IndexNode:
    def __init__(self, name, index, value=None,type_=None):
        self.name = name
        self.id = name
        self.index = index
        self.value = value
        self.type = type_
        self.pos_start = self.name.pos_start
        if index == None or index == "":
            res = ParseResult()
            return res.failure(Program.error()['Syntax']({
                    'pos_start': self.name.pos_start,
                    'pos_end': self.name.pos_end,
                    'message': "Expected index or slice expression",
                    'exit': False
                }))
        else:
            self.pos_end = self.index.pos_end
        
    def __repr__(self):
        return f'{self.name}'        
 
    
class SliceNode:
    def __init__(self, name, start, end, step=None, type=None):
        self.name = name
        self.id = name
        self.start = start
        self.end = end
        self.step = step
        self.type = type
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end if self.end is None else self.end.pos_end
        
    def __repr__(self):
        return f'{self.name}'


class SpreadNode:
    def __init__(self, assign_token, name, value, pos_start, pos_end, _type=None):
        self.assign_token = assign_token
        self.name = name
        self.id = name
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
        self._type = _type
        
    def __repr__(self):
        return f'{self.name}'


class ExportModuleNode:
    def __init__(self, modules):
        self.modules = modules
        if isinstance(self.modules[0], dict):
            self.pos_start = self.modules[0]['pos_start']
            self.pos_end = self.modules[-1]['pos_end']
        else:
            self.pos_start = self.modules[0].pos_start
            self.pos_end = self.modules[-1].pos_end
        
    def __repr__(self):
        return f'{self.modules}'


class ModuleExport:
    def __init__(self, name, value):
        self.name = name
        self.id = name
        self.value = value
        self.pos_start = self.name.pos_start
        self.pos_end = self.value.pos_end
    

class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        self.value = self.tok.value
        if tok.value == 'true':
            self.value = True
        elif tok.value == 'false':
            self.value = False
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'
    
    
class NoneNode:
    def __init__(self, tok):
        self.tok = tok
        self.id = tok
        self.value = self.tok.value
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'   


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        res = ParseResult()
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        if self.left_node == '' or self.right_node == '' or self.op_tok == '':
            res.failure(Program.error()['Syntax']({
                'message': 'Invalid syntax',
                'pos_start': self.op_tok.pos_start,
                'pos_end': self.op_tok.pos_end,
                'exit': False
            }))
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (
            self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

    def __repr__(self):
        return f'IfNode'


class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node, return_null):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class InNode:
    def __init__(self, iterable_node, iterators, body_node, return_null):
        self.iterable_node = iterable_node
        self.iterators = iterators
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.iterable_node.pos_start
        self.pos_end = self.body_node.pos_end    
        
    
class WhileNode:
    def __init__(self, condition_node, body_node, return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class MatchNode:
    def __init__(self, expression, cases, default_case):
        self.expression = expression
        self.cases = cases
        self.default_case = default_case

        self.pos_start = self.expression.pos_start
        if self.default_case:
            self.pos_end = self.default_case['pos_end']
        else:
            self.pos_end = self.cases[len(self.cases) - 1]['pos_end'] if self.cases else self.expression.pos_end


class RaiseNode:
    def __init__(self, expression):
        self.expression = expression
        self.pos_start = self.expression.pos_start
        self.pos_end = self.expression.pos_end
     

class DelNode:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
        self.pos_start = self.identifier.pos_start
        self.pos_end = self.identifier.pos_end     
   

class AttemptNode:
    def __init__(self, attempt_statement, catches, finally_statement, pos_start, pos_end):
        self.attempt_statement = attempt_statement
        self.catches = catches
        self.finally_statement = finally_statement
        self.pos_start = pos_start
        self.pos_end = pos_end
        

class FunctionNode:
    def __init__(self, def_name_token, args_name_tokens, body_node, implicit_return, default_values, type=None):
        self.def_name_token = def_name_token
        self.id = def_name_token
        self.args_name_tokens = args_name_tokens
        self.body_node = body_node
        self.implicit_return = implicit_return
        self.default_values = default_values
        self.type = type
        if self.def_name_token:
            self.pos_start = self.def_name_token.pos_start
        elif len(self.args_name_tokens) > 0:
            self.pos_start = self.args_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end


class ObjectNode:
    def __init__(self, object_name, properties, other=None):
        self.object_name = object_name
        self.id = object_name
        self.other = other
        if self.other != None and self.other['name'] == "module":
            self.type = "module"
            self.as_name = self.other['as_name']
        object_properties = []
        for prop in properties:
            object_properties.append(prop)
            if hasattr(prop['value'], 'pos_end'):
                self.pos_end = prop['value'].pos_end if len(
                properties) != 0 else self.object_name.pos_end
            else:
                self.pos_end = self.object_name.pos_end
        self.properties = object_properties
        self.pos_start = self.object_name.pos_start
        self.object = {
            'name': self.object_name.value,
            'properties': self.
            properties
        }
 
 
class DictNode:
    def __init__(self, properties, keys,values, pos_start, pos_end):
        self.properties = properties
        self.keys = keys
        self.values = values
        self.pos_start = pos_start
        self.pos_end = pos_end
 
 
class ModuleObject:
    def __init__(self, object_name, properties, other):
        self.object_name = object_name
        self.id = object_name
        self.other = other
        self.as_name = self.other['as_name']
        object_properties = []
        for prop in properties:
            object_properties.append(prop)
            if hasattr(prop['value'], 'pos_end'):
                self.pos_end = prop['value'].pos_end if len(
                properties) != 0 else self.object_name.pos_end
            else:
                self.pos_end = self.object_name.pos_end
        self.properties = object_properties
        self.pos_start = self.object_name.pos_start
        self.object = {
            'name': self.object_name.value,
            'properties': self.
            properties
        }       


class ClassNode:
    def __init__(self,class_name,inherits_class_name, methods, class_fields_modifiers):
        self.id = class_name
        self.class_name = class_name
        self.inherits_class_name = inherits_class_name
        self.methods = methods
        self.class_fields_modifiers = class_fields_modifiers
        self.pos_start = self.class_name.pos_start
        self.pos_end = self.class_name.pos_end
        self.class_object = {
            'name': self.class_name.value,
            'properties': self.methods
        }
        
    def __repr__(self):
        return f'{self.class_name}'


class CallNode:
    def __init__(self, node_to_call, args_nodes, keyword_args_list=None):
        self.id = node_to_call
        self.node_to_call = node_to_call
        self.args_nodes = args_nodes
        self.keyword_args_list = keyword_args_list
        self.pos_start = self.node_to_call.pos_start
        self.pos_end = self.node_to_call.pos_end
        
    def __repr__(self):
        return f'{self.node_to_call}({self.args_nodes})'


class GetNode:
    def __init__(self, module_name, module_path):
        self.id = module_name
        self.module_name = module_name
        self.module_path = module_path
        self.pos_start = self.module_name.pos_start
        self.pos_end = self.module_name.pos_end
        
    def __repr__(self):
        return f'{self.module_name}'
    
    
class GetModuleNode:
    def __init__(self, module_name, module_path):
        self.id = module_name
        self.module_name = module_name
        self.module_path = module_path
        self.pos_start = self.module_name.pos_start
        self.pos_end = self.module_name.pos_end
        
    def __repr__(self):
        return f'{self.module_name}'


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count if res else 0
        self.advance_count += res.advance_count if res else 0
        if res:
            if res.error:
                self.error = res.error
        else:
            self.error = ''
        return res.node if res else ''

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self
    
    def noreturn(self):
        return self



class Parser:
    
    def __init__(self, tokens, file_name, position=None):
        self.tokens = tokens
        self.file_name = file_name
        self.position = position
        # get file name without extension
        #self.file_name_no_ext = self.file_name.split('/')[2].split('.')[0]
        self.tok_index = -1
        self.error = Program.error()
        self.error_detected = False
        self.advance()

    def advance(self):
        self.tok_index += 1
        self.update_current_tok()
        return self.current_token
        # if hasattr(self, 'current_token'):
        #     return self.current_token
        # else:
        #     sys.exit(1)

    def peek(self, step=1):
        self.tok_index += step
        if self.tok_index < len(self.tokens):
            self.update_current_tok()
            return self.current_token
        return self.current_token
        
    def reverse(self, count=1):
        self.tok_index -= count
        self.update_current_tok()
        return self.current_token
        # if hasattr(self, 'current_token'):
        #     return self.current_token
        # else:
        #     sys.exit(1)

    def update_current_tok(self):
        if self.tok_index >= 0 and self.tok_index < len(self.tokens):
            self.current_token = self.tokens[self.tok_index]
        else:
            self.current_token = None

    def parse(self):
        res = self.statements()
        try:
            error = {
                'name': '',
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'exit': False
            }
                
            if not res.error and self.current_token.type != tokenList.TT_EOF:
                tok_detected = self.current_token
                error['name'] = 'SynaxError'
                error['message'] = "Invalid syntax or unknown token"
                if tok_detected:
                    if self.error_detected != True:
                        self.error_detected = True
                        return res.failure(self.error['Default'](error))
            return res
        except:
            pass
        
    def property(self, tok):
        res = ParseResult()
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        prop_name = self.current_token
        res.register_advancement()
        self.advance()
        return res.success(PropertyNode(tok, prop_name))
    
    def skipLines(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

    def statements(self):
        try:
            res = ParseResult()
            statements = []
            pos_start = self.current_token.pos_start.copy()

            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

            statement = res.register(self.statement())
            if res.error:
                return res
            statements.append(statement)

            more_statements = True

            while True:
                newline_count = 0
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    newline_count += 1
                if newline_count == 0:
                    more_statements = False

                if not more_statements: break
                statement = res.try_register(self.statement())
                if not statement:
                    self.reverse(res.to_reverse_count)
                    more_statements = False
                    continue
                statements.append(statement)
            return res.success(ListNode(statements, pos_start, self.current_token.pos_end.copy()))

        except:
            pass

    def statement(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        values = ()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'return'):
            res.register_advancement()
            self.advance()
            expr = res.try_register(self.expr())
            values = (expr,)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                values += (res.try_register(self.expr()),)
                expr = PairNode(values, pos_start, self.current_token.pos_end.copy())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(tokenList.TT_KEYWORD, 'continue'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(tokenList.TT_KEYWORD, 'break'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_token.pos_end.copy()))
        expr = res.register(self.expr())
        if res.error:
            return res.failure(self.error['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.current_token.pos_start,
                'message': "invalid syntax",
                'exit': False
            }))
        return res.success(expr)
    
    def expr(self):
        res = ParseResult()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'let') or self.current_token.matches(tokenList.TT_KEYWORD, 'final'):
            res.register_advancement()
            variable_keyword_token = "let" if self.current_token.matches(
                tokenList.TT_KEYWORD, 'let') else "final"
            self.advance()
            
            if(self.current_token.value in tokenList.KEYWORDS):
                if self.current_token.value == "fm":
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Invalid syntax or unknown token, possibly you meant to use 'fm' instead of 'fm' as an identifier?",
                        'exit': False
                    }))
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Cannot use keyword '{self.current_token.value}' as an identifier",
                    'exit': False
                }))
            if self.current_token.type == tokenList.TT_LPAREN:
                expr = res.register(self.expr())
                if res.error: return res
                values = expr.elements
                for val in values:
                    if isinstance(val, StringNode):
                        single_check_for_rest_operator = val.name.value.split('*')
                        if len(single_check_for_rest_operator) > 1 and single_check_for_rest_operator[0] == "":
                            self.error_detected = False
                    elif not isinstance(val, VarAccessNode):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': val.pos_start,
                            'pos_end': val.pos_end,
                            'message': "expected an identifier",
                            'exit': False
                        }))
                var_values = ()
                if self.current_token.type != tokenList.TT_EQ:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected '='",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                for value in values:
                    var_values += (value,)
                return res.success(VarAssignNode(var_values, expr, variable_keyword_token))
            
            if self.current_token.type == tokenList.TT_LSQBRACKET:
                expr = res.register(self.expr())
                if res.error:
                    return res
                values = expr.elements
                for val in values:
                    if isinstance(val, StringNode):
                        single_check_for_rest_operator = val.name.value.split('*')
                        if len(single_check_for_rest_operator) > 1 and single_check_for_rest_operator[0] == "":
                            self.error_detected = False
                    elif not isinstance(val, VarAccessNode):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': val.pos_start,
                            'pos_end': val.pos_end,
                            'message': "expected an identifier",
                            'exit': False
                        }))
                var_values = []
                if self.current_token.type != tokenList.TT_EQ:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected '='",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                for value in values:
                    var_values.append(value)
                return res.success(VarAssignNode(var_values, expr, variable_keyword_token))
            
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))
            var_name = self.current_token
            res.register_advancement()
            self.advance()
            if len(var_name.value) > 255:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Identifier too long",
                    'exit': False
                }))
           
           
            while self.current_token.type == tokenList.TT_COMMA:
                identifiers = [VarAccessNode(var_name)]
                values = []
                res.register_advancement()
                self.advance()
                comma_token = self.current_token
                if self.current_token.type == tokenList.TT_IDENTIFIER:
                    identifiers.append(VarAccessNode(self.current_token))
                    res.register_advancement()
                    self.advance()
                    while self.current_token.type == tokenList.TT_COMMA:
                        comma_token = self.current_token
                        res.register_advancement()
                        self.advance()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start':comma_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "Expected an identifier after ','",
                                'exit': False
                            }))
                        while self.current_token.type == tokenList.TT_IDENTIFIER:
                            identifiers.append(VarAccessNode(self.current_token))
                            res.register_advancement()
                            self.advance()
                    if self.current_token.type == tokenList.TT_EQ:
                        res.register_advancement()
                        self.advance()
                        new_values = []
                        expr = res.register(self.expr())
                        values.append(expr)
                        if isinstance(expr, PairNode) or isinstance(expr, ListNode):
                            for val in expr.elements:
                                new_values.append(val)
                                values = new_values
                        else:
                            values = expr
                            
                        if  self.current_token.type == tokenList.TT_COMMA:
                            while self.current_token.type == tokenList.TT_COMMA:
                                res.register_advancement()
                                self.advance()
                                comma_token = self.current_token
                                values = []
                                values.append(res.register(self.expr()))
                                for v in values:
                                    if v == '':
                                        values.remove(v)
                            values_list = ListNode(values, comma_token.pos_start, comma_token.pos_end)
                            if isinstance(expr, DictNode) or isinstance(expr, ObjectNode):
                                values_list = expr
                            return res.success(VarAssignNode(identifiers, values_list, variable_keyword_token))
                        else:
                            values = expr
                            return res.success(VarAssignNode(identifiers, values, variable_keyword_token))
                    else:
                        none_values = []
                        tok = Token(tokenList.TT_KEYWORD, 'none', None, None)
                        for i in range(len(identifiers)):
                            none_values.append(tok)
                        values_list = ListNode(none_values, comma_token.pos_start, comma_token.pos_end)
                        return res.success(VarAssignNode(identifiers, values_list, variable_keyword_token))
                else:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': comma_token.pos_start,
                        'pos_end': comma_token.pos_end,
                        'message': "Expected an identifier after ','",
                        'exit': False
                    }))
                # res.register_advancement()
                # self.advance()
                if res.error:
                    return res
               # return res.success(VarAssignNode(var_name, expr, variable_keyword_token))
            
            
            if self.current_token.type == tokenList.TT_RSHIFT:
                res.register_advancement()
                self.advance()
            
            if self.current_token.type != tokenList.TT_EQ:
                if variable_keyword_token == "let":
                    tok = Token(tokenList.TT_KEYWORD, 'none', None, None)
                    return res.success(VarAssignNode(var_name, tok, variable_keyword_token))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected '='",
                        'exit': False
                    }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_SPREAD:
                spread_expr = res.register(self.spread_expr(var_name, variable_keyword_token))
                return res.success(spread_expr)
            expr = res.register(self.expr())
            if expr == "":
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an expression",
                    'exit': False
                }))
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr, variable_keyword_token))
        node = res.register(self.binaryOperation(
            self.comp_expr, ((tokenList.TT_KEYWORD, 'and'), (tokenList.TT_KEYWORD, 'or'), (tokenList.TT_KEYWORD, 'in'), (tokenList.TT_KEYWORD, 'notin'))))
        if res.error:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "invalid syntax or unexpected token",
                'exit': False
            }))
        return res.success(node)
    
    def comp_expr(self):
        res = ParseResult()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'not'):
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))
        node = res.register(self.binaryOperation(
            self.arith_expr, (tokenList.TT_EQEQ, tokenList.TT_NEQ, tokenList.TT_LT, tokenList.TT_GT, tokenList.TT_RSHIFT, tokenList.TT_LSHIFT, tokenList.TT_LTE, tokenList.TT_GTE, tokenList.TT_AND)))

        if res.error:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'exit': False
            }))

        return res.success(node)
                
    def arith_expr(self):
        return self.binaryOperation(self.term, (tokenList.TT_PLUS, tokenList.TT_MINUS, tokenList.TT_FLOOR_DIV))

    def term(self):
        return self.binaryOperation(self.factor, (tokenList.TT_MUL, tokenList.TT_DIV, tokenList.TT_MOD, tokenList.TT_MERGE))
    
    def factor(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_PLUS, tokenList.TT_MINUS, tokenList.TT_FLOOR_DIV):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            if tok and not factor: # if tok and factor is None
                self.error_detected = True
                self.error['Syntax']({
                    'message': 'Invalid syntax',
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'exit': False
                })
            return res.success(UnaryOpNode(tok, factor))
        return self.power()
    
    def increment_or_decrement(self, atom):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_PLUS_PLUS, tokenList.TT_MINUS_MINUS):
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                identifier = res.register(self.atom())
                return res.success(UnaryOpNode(tok, identifier))

            return res.success(BinOpNode(atom, tok, atom))

        
        return res.success(atom)
    
    def power(self):
        return self.binaryOperation(self.set_node_expr, (tokenList.TT_POWER, ), self.factor)
    
    def set_node_expr(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:  return res
        while True:
            if self.current_token.type == tokenList.TT_LPAREN:
                atom = res.register(self.finish_call(atom))
            elif self.current_token.type == tokenList.TT_DOT:
                res.register_advancement()
                self.advance()
                name = self.current_token
                if atom == '':
                    # then we want to make it a floating point number e.g. .5 == 0.5
                    if name != '' and isinstance(name.value, int):
                        tok = Token(tokenList.TT_FLOAT, float(
                            '0.' + str(name.value)), name.pos_start, name.pos_end)
                        res.register_advancement()
                        self.advance()
                        return res.success(NumberNode(tok))
                    else:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Invalid syntax or unknown token",
                            'exit': False
                        }))
                else:
                    atom = res.register(self.access_property(atom))
                    if res.error: return res
                    if name.type != tokenList.TT_IDENTIFIER and name.type != tokenList.TT_KEYWORD:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': name.pos_start,
                            'pos_end': name.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
            elif self.current_token.type == tokenList.TT_LSQBRACKET:
                atom = res.register(self.index_get(atom))
            elif self.current_token.type == tokenList.TT_PLUS_PLUS:
                atom = res.register(self.increment_or_decrement(atom))
            elif self.current_token.type == tokenList.TT_MINUS_MINUS:
                atom = res.register(self.increment_or_decrement(atom))
            elif self.current_token.type != None and self.current_token.type in operation_methods:
                operator = self.current_token
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_IDENTIFIER:
                    identifier = res.register(self.expr())
                    return res.success(VarReassignNode(atom, identifier, operation_methods[operator.type]))
                elif self.current_token.type in (tokenList.TT_INT, tokenList.TT_FLOAT, tokenList.TT_BINARY, tokenList.TT_HEX, tokenList.TT_OCTAL):
                    value = res.register(self.atom())
                    return res.success(VarReassignNode(atom, value, operation_methods[operator.type]))
                elif self.current_token == None or self.current_token.type == tokenList.TT_NEWLINE or self.current_token.type == tokenList.TT_EOF:
                    self.error_detected = True
                    self.error['Syntax']({
                        'message': "invalid syntax",
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'exit': False
                    })
                else:
                    expr  = res.register(self.expr())
                    return res.success(VarReassignNode(atom, expr, operation_methods[operator.type]))
                    
            else:
                break
        
                
        return res.success(atom)
            
    def finish_call(self, atom):
        res = ParseResult()
        arg_nodes = []
        keyword_args = {}
        keyword_args_list = []
        if self.current_token.type == tokenList.TT_LPAREN:
            self.skipLines()
            if self.current_token.type == tokenList.TT_RPAREN:
                self.skipLines()
                
            else:
                # keyword arguments
                if self.current_token.type == tokenList.TT_IDENTIFIER:
                    keyword_args = {
                        'name': self.current_token.value,
                        'value': ''
                    }
                    self.skipLines()
                    if self.current_token.type == tokenList.TT_EQ:
                        self.skipLines()
                        keyword_args['value'] = res.register(self.expr())
                        if res.error: return res
                        keyword_args_list.append(keyword_args)
                        
                        if keyword_args['value'] == None or keyword_args['value'] == '':
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "invalid syntax",
                                'exit': False
                            }))
                        if res.error: return res
                        self.reverse()
                    else:
                        self.reverse()
                        
                        
                expr = res.register(self.expr())
                arg_nodes.append(expr)
                if res.error:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"Expected ')'",
                        'exit': False
                    }))
                    
                while self.current_token.type == tokenList.TT_COMMA:
                    self.skipLines()
                    if self.current_token.type == tokenList.TT_IDENTIFIER:
                        keyword_args = {
                            'name': self.current_token.value,
                            'value': ''
                        }
                        self.skipLines()
                        if self.current_token.type == tokenList.TT_EQ:
                            self.skipLines()
                            keyword_args['value'] = res.register(self.expr())
                            if res.error: return res
                            keyword_args_list.append(keyword_args)
                            if keyword_args['value'] == None or keyword_args['value'] == '':
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "invlaid syntax",
                                    'exit': False
                                }))
                            if res.error: return res
                            duplicate_key = None
                            is_duplicate = False
                            keys_count = []
                            for key in keyword_args_list:
                                first_key = key['name']
                                keys_count.append(first_key)
                            for key in keys_count:
                                if keys_count.count(key) > 1:
                                    duplicate_key = key
                                    is_duplicate = True
                                    break
                            if is_duplicate:
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': f"repeated keyword argument: '{duplicate_key}'",
                                    'exit': False
                                }))
                            self.reverse()
                        else:
                            if len(keyword_args_list) > 0:
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "positional argument cannot follow keyword argument",
                                    'exit': False
                                }))
                            self.reverse()
                    else:
                        if len(keyword_args_list) > 0:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "positional argument cannot follow keyword argument",
                                'exit': False
                            }))
                        for arg in arg_nodes:
                            if arg == None or arg == '':
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "invlaid syntax",
                                    'exit': False
                                }))
                    arg_nodes.append(res.register(self.expr()))
                    
                
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ',' or ')'",
                        'exit': False
                    }))
                
                self.skipLines()
                
                
              
        return res.success(CallNode(atom, arg_nodes, keyword_args_list))
                
                
                # if self.current_token.type != tokenList.TT_NEWLINE and self.current_token.type != tokenList.TT_RPAREN and self.current_token.type != tokenList.TT_EOF:
                #     return res.failure(self.error['Syntax']({
                #         'pos_start': self.current_token.pos_start,
                #         'pos_end': self.current_token.pos_end,
                #         'message': "Statements must be separated by a newline",
                #         'exit': False
                #     }))
                # if self.current_token.type == tokenList.TT_RPAREN:
                #     return res.failure(self.error['Syntax']({
                #         'pos_start': self.current_token.pos_start,
                #         'pos_end': self.current_token.pos_end,
                #         'message': "Unmatched ')'",
                #         'exit': False
                #     }))
         
    def atom(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_INT, tokenList.TT_FLOAT, tokenList.TT_BINARY, tokenList.TT_HEX, tokenList.TT_OCTAL):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == tokenList.TT_DOUBLE_STRING or tok.type == tokenList.TT_SINGLE_STRING or tok.type == tokenList.TT_BACKTICK_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == tokenList.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_EQ:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                return res.success(VarReassignNode(tok, expr))
            else:
                return res.success(VarAccessNode(tok))
        elif tok.value == 'true' or tok.value == 'false':
            res.register_advancement()
            self.advance()
            return res.success(BooleanNode(tok))
        elif tok.value == 'none':
            res.register_advancement()
            self.advance()
            return res.success(NoneNode(tok))
        elif tok.type == tokenList.TT_LPAREN:
            pair_expr = res.register(self.pair_expr())
            if res.error: return res
            return res.success(pair_expr)
        elif tok.type == tokenList.TT_RPAREN:
            return res.failure(self.error['Syntax']({
                'pos_start': tok.pos_start,
                'pos_end': tok.pos_end,
                'message': f"invalid syntax or unexpected token",
                'exit': False
            }))
        elif tok.type == tokenList.TT_LSQBRACKET:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)
        elif tok.type == tokenList.TT_LBRACE:
            dict_expr = res.register(self.dict_expr())
            if res.error:
                return res
            return res.success(dict_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'if'):
            if_expression = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expression)
        elif tok.matches(tokenList.TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'in'):
            in_expr = res.register(self.in_expr())
            if res.error:
                return res
            return res.success(in_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'def'):
            function_expr = res.register(self.function_expr())
            if res.error:
                   return res
            return res.success(function_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'object'):
            object_expr = res.register(self.object_def())
            if res.error:
                return res
            return res.success(object_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'class'):
            class_expr = res.register(self.class_def())
            if res.error:
                return res
            return res.success(class_expr)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'match'):
            match_expr = res.register(self.match_expr())
            if res.error:
                return res
            return res.success(match_expr)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'attempt'):
            attempt_expr = res.register(self.attempt_expr())
            if res.error:
                return res
            return res.success(attempt_expr)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'raise'):
            raise_expr = res.register(self.raise_expr())
            if res.error:
                return res
            return res.success(raise_expr)

        elif tok.matches(tokenList.TT_KEYWORD, 'fm'):
            string_interp = res.register(self.string_interp())
            if res.error:
                return res
            return res.success(string_interp)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'del'):
            del_expr = res.register(self.del_expr())
            if res.error:
                return res
            return res.success(del_expr)

        elif tok.matches(tokenList.TT_KEYWORD, 'get'):
            get_expr = res.register(self.get_expr())
            if res.error:
                return res
            return res.success(get_expr)

        elif tok.matches(tokenList.TT_KEYWORD, 'module'):
            module_expr = res.register(self.module_expr())
            if res.error:
                return res
            return res.success(module_expr)

        elif tok.matches(tokenList.TT_KEYWORD, 'export'):
            export_expr = res.register(self.export_expr())
            if res.error:
                return res
            return res.success(export_expr)
    
    def access_property(self,owner):
        res = ParseResult()
        name = self.current_token
        res.register_advancement()
        self.advance()
        arg_nodes = []
        
        if self.current_token.type == tokenList.TT_LPAREN:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_RPAREN:
                res.register_advancement()
                self.advance()
                call_node = res.success(CallNode(name, arg_nodes))
                name = res.register(call_node)
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"Expected ')'",
                        'exit': False
                    }))
                    
                    
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                    
                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ',' or ')'",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                call_node = res.success(CallNode(name, arg_nodes))
                name = res.register(call_node)
        
        if self.current_token.type == tokenList.TT_PLUS_PLUS:
            res.register_advancement()
            self.advance()
            return res.success(PropertySetNode(owner, name, None, "++"))

        elif self.current_token.type == tokenList.TT_MINUS_MINUS:
            res.register_advancement()
            self.advance()
            return res.success(PropertySetNode(owner, name, None, "--"))
        
        elif self.current_token.type != None and self.current_token.type in operation_methods:
            operator = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                value = res.register(self.expr())
                return res.success(VarReassignNode(owner, value, operation_methods[operator.type], name))
            elif self.current_token.type in (tokenList.TT_INT, tokenList.TT_FLOAT, tokenList.TT_BINARY, tokenList.TT_HEX, tokenList.TT_OCTAL):
                value = res.register(self.atom())
                return res.success(VarReassignNode(owner, value, operation_methods[operator.type], name))
            elif self.current_token == None or self.current_token.type == tokenList.TT_NEWLINE or self.current_token.type == tokenList.TT_EOF:
                self.error_detected = True
                self.error['Syntax']({
                    'message': "invalid syntax",
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'exit': False
                })
            else:
                expr  = res.register(self.expr())
                return res.success(VarReassignNode(owner, expr, operation_methods[operator.type], name))

        if self.current_token.type == tokenList.TT_EQ:
            res.register_advancement()
            self.advance()
            value = res.register(self.expr())
            if res.error: return res
            return res.success(PropertySetNode(owner, name, value))
       
        return res.success(PropertyNode(owner, name))
    
    def make_expr(self,atom):
        res = ParseResult()
        name = atom
        arg_nodes = []
        if self.current_token.type == tokenList.TT_LPAREN:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_RPAREN:
                res.register_advancement()
                self.advance()
                call_node = res.success(CallNode(name, arg_nodes))
                name = res.register(call_node)
                
                return res.success(name)
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"Expected ')'",
                        'exit': False
                    }))

                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ',' or ')'",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                call_node = res.success(CallNode(name, arg_nodes))
                name = res.register(call_node)
                return res.success(name)
      
    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('if'))
        if res.error:
            self.error_detected = True
            return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_token.matches(tokenList.TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_COLON:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected ':'",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                start_token = self.current_token
                statements = res.register(self.statements())
                if len(statements.elements) > 0:
                    if statements.elements[0] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax'](
                            {
                                'pos_start': start_token.pos_start,
                                'pos_end': start_token.pos_end,
                                'message': 'Expected an expression',
                                'exit': False
                            }
                        ))
                if res.error:
                    return res
                else_case = (statements, True)
                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()

                else:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'Expected "end"',
                            'exit': False
                        }
                    ))
            else:
                current_token = self.current_token
                expr = res.register(self.statement())
                if self.current_token.type == tokenList.TT_COLON:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "':' is not allowed here",
                            'exit': False
                        }
                    ))
                if expr == "":
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'Expected an expression',
                            'exit': False
                        }
                    ))
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(tokenList.TT_KEYWORD, 'elif'):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                self.error_detected = True
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                self.error_detected = True
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_name):
        res = ParseResult()
        cases = []
        else_case = None
        
        if not self.current_token.matches(tokenList.TT_KEYWORD, case_name):
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected "{}"'.format(case_name),
                    'exit': False
                }
            ))
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if condition == "":
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected an expression',
                    'exit': False
                }
            ))
        if res.error:
            return res

        if self.current_token.type != tokenList.TT_COLON:
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected ":"',
                    'exit': False
                }
            ))
        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            start_token = self.current_token
            statements = res.register(self.statements())
            if len(statements.elements) > 0:
                if statements.elements[0] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': start_token.pos_start,
                            'pos_end': start_token.pos_end,
                            'message': 'Expected an expression',
                            'exit': False
                        }
                    ))
            if res.error:
                return res
            cases.append((condition, statements, True))
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error:
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error:
                self.error_detected = True
                return res
            cases.append((condition, expr, False))
            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                self.error_detected = True
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'for'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'for'"
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))

        var_name_token = self.current_token
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_EQ:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '='",
                'exit': False
            }))
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'to'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'to'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_token.matches(tokenList.TT_KEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if self.current_token.type != tokenList.TT_COLON:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected ':'",
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_NEWLINE:

            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'end'",
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, True))
        body = res.register(self.statement())
        if res.error:
            return res
        # if self.current_token.matches(tokenList.TT_KEYWORD, 'return'):
        #     return res.failure(self.error['Syntax'](
        #         {
        #             'pos_start': self.current_token.pos_start,
        #             'pos_end': self.current_token.pos_end,
        #             'message': 'return is not allowed in for loop',
        #             'exit': False
        #         }
        #     ))

        return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, False))

    def in_expr(self):
        res = ParseResult()
        iterable_name_token = None
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'in'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'in'"
            }))
            
        res.register_advancement()
        self.advance()
        
        
        
        iterable_name_token = res.register(self.expr())
        if iterable_name_token == None or iterable_name_token == '':
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'as'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'as'",
                'exit': False
            }))
            
        res.register_advancement()
        self.advance()
        
        iterator_keys = []
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            expr = res.register(self.expr())
            iterator_keys.append(expr)
            if self.current_token.type == tokenList.TT_COMMA:
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    expr = res.register(self.expr())
                    iterator_keys.append(expr)
                    if res.error: return res
                    if len(iterator_keys) == 0:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    elif len(iterator_keys) > 2:
                        return res.failure(self.error['ValueError']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Too many values, expected 2 or 1 but got {}".format(len(iterator_keys)),
                            'exit': False
                        }))
                    if self.current_token.type != tokenList.TT_COLON:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected ':'",
                            'exit': False
                        }))
                    res.register_advancement()
                    self.advance()
                    
                    if self.current_token.type == tokenList.TT_NEWLINE:
                        res.register_advancement()
                        self.advance()

                        body = res.register(self.statements())
                        if res.error:
                            return res

                        if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "Expected 'end'",
                                'exit': False
                            }))

                        res.register_advancement()
                        self.advance()

                        return res.success(InNode(iterable_name_token, iterator_keys, body, False))
                    
                    else:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected a newline",
                            'exit': False
                        }))
            
            
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ':'",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                body = res.register(self.statements())
                if res.error:
                    return res

                if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected 'end'",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                return res.success(InNode(iterable_name_token, iterator_keys, body, False))
        else:
            expr = res.register(self.expr())
            if not isinstance(expr, PairNode):
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or a pair",
                    'exit': False
                }))
                
            for el in expr.elements:
                iterator_keys.append(el)
                
            if len(iterator_keys) == 0:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a value",
                    'exit': False
                }))
                
            elif len(iterator_keys) > 2:
                self.error_detected = True
                return res.failure(self.error['ValueError']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Too many values, expected 2 or 1 but got {}".format(len(iterator_keys)),
                    'exit': False
                }))
                
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ':'",
                    'exit': False
                }))
                
            res.register_advancement()
            self.advance()
            
            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                
                body = res.register(self.statements())
                if res.error:
                    return res
                
                if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected 'end'",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                
                return res.success(InNode(iterable_name_token, iterator_keys, body, False))
                
                
    
        body = res.register(self.statement())
        return res.success(InNode(iterable_name_token, iterator_keys, body, False)) 
    
    def while_expr(self):
        res = ParseResult()

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'while'):
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'while'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_token.type != tokenList.TT_COLON:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected ':'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'end'",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def function_expr(self):
        res = ParseResult()
        default_values = {}
        default_values_list = []
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'def'):
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'def'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            def_name_token = self.current_token
            if def_name_token.value[0] != '@':
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': def_name_token.pos_start,
                    'pos_end': def_name_token.pos_end,
                    'message': "Expected '@' before function name",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_LPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '('",
                    'exit': False
                }))
        else:
            def_name_token = None
            def_name = self.current_token.value
            if def_name in tokenList.KEYWORDS:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as def name",
                'exit': False
            }))
            if self.current_token.type != tokenList.TT_LPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or '('",
                    'exit': False
                }))
        res.register_advancement()
        self.advance()
        arg_name_tokens = []

        if self.current_token.type == tokenList.TT_IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            default_values ={
                'name': self.current_token.value,
                'value': ''
            }
            
            self.skipLines()
            
            if self.current_token.type == tokenList.TT_EQ:
                self.skipLines()
                default_values['value'] = res.register(self.expr())
                default_values_list.append(default_values)
                if default_values['value'] == None or default_values['value'] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax",
                        'exit': False
                    }))
                if res.error: return res
                
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected an identifier",
                        'exit': False
                    }))
                default_values = {
                    'name': self.current_token.value,
                    'value': ''
                }
                arg_name_tokens.append(self.current_token)
                
                # if len(arg_name_tokens) > 20:
                #     self.error_detected = True
                #     return res.failure(self.error['Syntax']({
                #         'pos_start': self.current_token.pos_start,
                #         'pos_end': self.current_token.pos_end,
                #         'message': "Cannot have more than 12 arguments",
                #         'exit': False
                #     }))
                self.skipLines()
                
                # named arguments cannot be followed by a default value
                if self.current_token.type == tokenList.TT_EQ:
                    self.skipLines()
                    default_values['value'] = res.register(self.expr())
                    default_values_list.append(default_values)
                    if default_values['value'] == None or default_values['value'] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid syntax",
                            'exit': False
                        }))
                    if res.error: return res
                    duplicate_key = None
                    is_duplicate = False
                    keys_count = []
                    for key in default_values_list:
                        first_key = key['name']
                        keys_count.append(first_key)
                    for key in keys_count:
                        if keys_count.count(key) > 1:
                            duplicate_key = key
                            is_duplicate = True
                            break
                    if is_duplicate:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': f"duplicate argument: '{duplicate_key}' in function definition",
                            'exit': False
                        }))
                else:
                    if len(default_values_list) > 0:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "non-default argument cannot be followed by a default argument",
                            'exit': False
                        }))
                        
            if self.current_token.type != tokenList.TT_RPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ',' or ')'",
                    'exit': False
                }))
        else:
            if self.current_token.type != tokenList.TT_RPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or ')'",
                    'exit': False
                }))
        self.skipLines()
        if self.current_token.type == tokenList.TT_ARROW:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an expression",
                    'exit': False
                }))
            body = res.register(self.expr())
            if res.error: return res
            return res.success(FunctionNode(def_name_token, arg_name_tokens, body, True, default_values_list))
        
        
        if self.current_token.type != tokenList.TT_NEWLINE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected  '->', or a newline",
                'exit': False
            }))
            
            
        res.register_advancement()
        self.advance()
        
        
        body = res.register(self.statements())
        if res.error: return res
            
        
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            return res.success(FunctionNode(def_name_token, arg_name_tokens, body, False, default_values_list))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'end'",
                'exit': False
            }))     
  
    def object_def(self):
        res = ParseResult()
        object_properties = []
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'object'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'object'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        
        object_name = self.current_token
        
        if object_name in tokenList.KEYWORDS:
            self.error_detected = True
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as object name",
                'exit': False
            }))
        if isOnlyLetters(object_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use non-letter characters as object name",
                'exit': False
            }))
        if isFirstLetterUpper(object_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Object name must start with a capital letter",
                'exit': False
            }))
        
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_NEWLINE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
                'exit': False
            }))
        
        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                
                object_properties.append({
                    'name': object_name,
                    'value': [],
                    'pos_start': object_name.pos_start,
                    'pos_end': object_name.pos_end
                })
                return res.success(ObjectNode(object_name, object_properties))
            if self.current_token.type != tokenList.TT_IDENTIFIER and str(self.current_token.value) not in tokenList.DIGITS:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))
            
            while self.current_token.type == tokenList.TT_IDENTIFIER or str(self.current_token.value) in tokenList.DIGITS:
                
                obj_name = self.current_token
                if hasattr(obj_name, 'value'):
                    if not isinstance(obj_name.value, str):
                        self.error_detected = True
                        return res.failure(self.error['NameError']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid object property name '{}'".format(obj_name.value),
                            'exit': False
                        }))
                if res.error: return res
                # object property name cannot start with a @ or a symbol
                if obj_name.value[0] == '@' or obj_name.value[0] in tokenList.SYMBOLS:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Object name cannot start with a symbol",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                
                if self.current_token.type != tokenList.TT_COLON:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ':'",
                        'exit': False
                    }))
                
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_IDENTIFIER:
                    
                    if self.current_token.value == 'self':
                        self.current_token.value = object_name.value
                obj_value = res.register(self.expr())
                
                object_properties.append({
                        'name': obj_name,
                        'value': obj_value,
                        'pos_start': obj_name.pos_start,
                        'pos_end': self.current_token.pos_end
                    })
                
                
                
                #return res.success(ObjectNode(object_name, object_properties))
                
                if res.error: return res
                if obj_value == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected property value",
                        'exit': False
                    }))
                if self.current_token.type == tokenList.TT_COMMA:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unexpected token, expected a newline",
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_NEWLINE:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a newline",
                        'exit': False
                    }))
                
                res.register_advancement()
                self.advance()
                
                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()
                    
                    return res.success(ObjectNode(object_name, object_properties))
                if self.current_token.value in tokenList.NOT_ALLOWED_OBJECTS_KEYS:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unterminated object literal, Object key '{}' is not allowed".format(self.current_token.value),
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    while self.current_token.type == tokenList.TT_NEWLINE:
                        res.register_advancement()
                        self.advance()
                        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                            res.register_advancement()
                            self.advance()
                            return res.success(ObjectNode(object_name, object_properties))
                    if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected 'end' or you have forgottem to close a newline",
                        'exit': False
                    }))
                    else:
                        res.register_advancement()
                        self.advance()
                        return res.success(ObjectNode(object_name, object_properties))
            else:
                self.error_detected = True
                return res.failure(self.error['NameError']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid or missing object name",
                    'exit': False
                }))
            return res.success(ObjectNode(object_name, object_properties))   
     
    def dict_expr(self):
        res = ParseResult()
        properties = []
        keys = []
        values = []
        pos_start = self.current_token.pos_start.copy()
        
        if self.current_token.type != tokenList.TT_LBRACE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '{'",
                'exit': False
            }))
          
        self.skipLines()
        
        start_token = self.current_token
        if self.current_token.type == tokenList.TT_RBRACE:
            self.skipLines()
            return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
        else:
            while self.current_token.type == tokenList.TT_NEWLINE:
                self.skipLines()
            if self.current_token.type == tokenList.TT_EOF:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': start_token.pos_start,
                    'pos_end': start_token.pos_end,
                    'message': "Expected ',', '}' or a newline",
                    'exit': False
                }))

            if self.current_token.type == tokenList.TT_IDENTIFIER or tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING:
                properties.append({
                    'key': self.current_token,
                    'value': [],
                    'pos_start': self.current_token.pos_start.copy(),
                    'pos_end': self.current_token.pos_end.copy()
                })
                keys.append(self.current_token)
                self.skipLines()
                
                if self.current_token.type != tokenList.TT_COLON:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "'{' was not closed",
                        'exit': False
                    }))
                    
                self.skipLines()
                
                value = res.register(self.expr())
                if value == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected an expression after ':'",
                        'exit': False
                    }))
                if res.error: return res
                properties[-1]['value'] = value
                values.append(value)
                
                while self.current_token.type == tokenList.TT_NEWLINE:
                    self.skipLines()
                    
                if self.current_token.type == tokenList.TT_RBRACE:
                    self.skipLines()
                    return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                
                while self.current_token.type == tokenList.TT_COMMA:
                    self.skipLines()
                
                    while self.current_token.type == tokenList.TT_NEWLINE:
                        self.skipLines()
                    
                    if self.current_token.type == tokenList.TT_RBRACE:
                        self.skipLines()
                        return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                    
                    if self.current_token.type == tokenList.TT_IDENTIFIER or tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING:
                        properties.append({
                            'key': self.current_token,
                            'value': [],
                            'pos_start': self.current_token.pos_start.copy(),
                            'pos_end': self.current_token.pos_end.copy()
                        })
                        keys.append(self.current_token)
                        self.skipLines()
                        
                        
                        if self.current_token.type != tokenList.TT_COLON:
                            return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                                'message': "'{' was not closed",
                            'exit': False
                        }))
                            
                        self.skipLines()
                        
                        value = res.register(self.expr())
                        if value == '':
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "Expected an expression after ':'",
                                'exit': False
                            }))
                        if res.error: return res
                        properties[-1]['value'] = value
                        values.append(value)
                        
                        while self.current_token.type == tokenList.TT_NEWLINE:
                            self.skipLines()
                        
                        if self.current_token.type == tokenList.TT_RBRACE:
                            self.skipLines()
                            return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                        
                        
                        
                    
                
                    # while self.current_token.type == tokenList.TT_NEWLINE:
                    #     self.skipLines()
                    
                    # print(self.current_token, "is the current token")
                    
                    # if self.current_token.type == tokenList.TT_EOF:
                    #     self.error_detected = True
                    #     return res.failure(self.error['Syntax']({
                    #         'pos_start': self.current_token.pos_start,
                    #         'pos_end': self.current_token.pos_end,
                    #         'message': "Expected '}' or a newline",
                    #         'exit': False
                    #     }))
                    
                    # if self.current_token.type == tokenList.TT_IDENTIFIER or tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING:
                    #     properties.append({
                    #         'key': self.current_token,
                    #         'value': [],
                    #         'pos_start': self.current_token.pos_start.copy(),
                    #         'pos_end': self.current_token.pos_end.copy()
                    #     })
                    #     keys.append(self.current_token)
                    #     self.skipLines()
                    #     print(keys,values, self.current_token)
                    #     if self.current_token.type != tokenList.TT_COLON:
                    #         return res.failure(self.error['Syntax']({
                    #             'pos_start': self.current_token.pos_start,
                    #             'pos_end': self.current_token.pos_end,
                    #             'message': "Expected ':'",
                    #             'exit': False
                    #         }))
                    #     res.register_advancement()
                    #     self.advance()
                    #     value = res.register(self.expr())
                    #     if res.error: return res
                    #     properties[-1]['value'] = value
                    #     values.append(value)
                        
                    #     while self.current_token.type == tokenList.TT_NEWLINE:
                    #         self.skipLines()
                        
                    #     if self.current_token.type == tokenList.TT_RBRACE:                
                    #         self.skipLines()
                    #         return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))

                    # else:
                    #     if self.current_token.type == tokenList.TT_RBRACE:
                    #         self.skipLines()
                    #         return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                    #     else:
                    #         return res.failure(self.error['Syntax']({
                    #             'pos_start': self.current_token.pos_start,
                    #             'pos_end': self.current_token.pos_end,
                    #             'message': "Expected '}' or a newline",
                    #             'exit': False
                    #         }))
                
                if self.current_token.type == tokenList.TT_RBRACE:
                    self.skipLines()
                    return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ',', or '}'",
                        'exit': False
                    }))
                
        return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                          
    def class_def(self):
        res = ParseResult()
        inherit_class_name = None
        class_name = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'class'):
            res.register_advancement()
            self.advance()
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'class'",
                'exit': False
            }))
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a class name",
                'exit': False
            }))
            
            
        class_name = self.current_token
        #class name has to be upper case
        # class name must be only letters
        if  isFirstLetterUpper(class_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Class name must start with a capital letter",
                'exit': False
            }))
        if isOnlyLetters(class_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Class name can only contain letters",
                'exit': False
            }))
        if class_name in tokenList.KEYWORDS:
            self.error_detected = True
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as class name",
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        
        if self.current_token.type == tokenList.TT_LPAREN:
            self.skipLines()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
        
                inherit_class_name = self.current_token
                self.skipLines()
                if self.current_token.type == tokenList.TT_COMMA:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "multiple inheritance not supported",
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ',' or ')'",
                        'exit': False
                    }))
                
                self.skipLines()
                
                
            else:
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ')'",
                        'exit': False
                    }))
                
                self.skipLines()

        
        
        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
                'exit': False
            }))
        self.skipLines()
        
        methods = None
        class_fields_modifiers = None
        
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers))

        
        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers))
            
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                class_fields_modifiers = self.class_fields_modifiers()
            if self.current_token.matches(tokenList.TT_KEYWORD, "def"):
                methods = self.set_methods()
            else:
                while self.current_token.type != tokenList.TT_NEWLINE:
                    self.skipLines()
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_start,
                        'message': "invalid syntax",
                        'exit': False
                    }))
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers))
        
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            class_fields_modifiers = self.class_fields_modifiers()
        
           
        if self.current_token.matches(tokenList.TT_KEYWORD, "def"):
            methods = self.set_methods()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(ClassNode(class_name,inherit_class_name, methods, class_fields_modifiers))
        if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
            res.register_advancement()
            self.advance()
            return res.success(ClassNode(class_name,inherit_class_name, methods, class_fields_modifiers))
        if self.current_token.type == tokenList.TT_EOF:
            return res.success(ClassNode(class_name,inherit_class_name, methods, class_fields_modifiers))
        
        self.error_detected = True
        return res.failure(self.error['Syntax']({
            'pos_start': self.current_token.pos_start,
            'pos_end': self.current_token.pos_end,
            'message': "Expected 'end'",
            'exit': False
        }))
      
    def class_fields_modifiers(self):
        res = ParseResult()
        class_fields = []
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
            
        # class fields must start with @ 
        while self.current_token.type == tokenList.TT_IDENTIFIER:
            name = self.current_token
            # if has_at_symbol(name.value) == False:
            #     self.error_detected = True
            #     return res.failure(self.error['Syntax']({
            #         'pos_start': self.current_token.pos_start,
            #         'pos_end': self.current_token.pos_end,
            #         'message': "Expected '@' before identifier",
            #         'exit': False
            #     }))
                    
            self.skipLines()
            
            field = {
                'name': name,
                'value': None
            }
            class_fields.append(field)
            if self.current_token.type != tokenList.TT_EQ:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '='",
                    'exit': False
                }))
            
            self.skipLines()

            expr = res.register(self.expr())
            if res.error: return res
            field['value'] = expr
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a newline",
                    'exit': False
                }))
            while self.current_token.type == tokenList.TT_NEWLINE:
                self.skipLines()
        return class_fields
          
    def set_methods(self):
        res = ParseResult()
        methods = []
        default_values = {}
        default_values_list = []
        while self.current_token.matches(tokenList.TT_KEYWORD, "def"):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_IDENTIFIER and self.current_token.type != tokenList.TT_KEYWORD:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))
            method_name = self.current_token
            res.register_advancement()
            self.advance()

            if self.current_token.type != tokenList.TT_LPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '('",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            args_list = []
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                default_values = {
                    'name': self.current_token.value,
                    'value': ''
                }
                args_list.append(self.current_token)
                self.skipLines()
                
                if self.current_token.type == tokenList.TT_EQ:
                    self.skipLines()
                    default_values['value'] = res.register(self.expr())
                    default_values_list.append(default_values)
                    if default_values['value'] == None or default_values['value'] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid syntax",
                            'exit': False
                        }))
                    if res.error: return res
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    default_values = {
                        'name': self.current_token.value,
                        'value': ''
                    }
                    args_list.append(self.current_token)
                    
                    self.skipLines()
                    # if len(args_list) > 20:
                    #     self.error_detected = True
                    #     return res.failure(self.error['Syntax']({
                    #     'pos_start': self.current_token.pos_start,
                    #     'pos_end': self.current_token.pos_end,
                    #     'message': "Cannot have more than 12 arguments",
                    #     'exit': False
                    # }))
                    
                    if self.current_token.type == tokenList.TT_EQ:
                        self.skipLines()
                        default_values['value'] = res.register(self.expr())
                        default_values_list.append(default_values)
                        if default_values['value'] == None or default_values['value'] == '':
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "invalid syntax",
                                'exit': False
                            }))
                        if res.error: return res
                        duplicate_key = None
                        is_duplicate = False
                        keys_count = []
                        for key in default_values_list:
                            first_key = key['name']
                            keys_count.append(first_key)
                        for key in keys_count:
                            if keys_count.count(key) > 1:
                                duplicate_key = key
                                is_duplicate = True
                                break
                        if is_duplicate:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': f"duplicate argument: '{duplicate_key}' in method '{method_name.value}'",
                                'exit': False
                            }))
                    else:
                        if len(default_values_list) > 0:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "non-default argument cannot be followed by a default argument",
                                'exit': False
                            }))
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ')'",
                        'exit': False
                    }))
                    
            else:
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ')'",
                        'exit': False
                    }))
            
            
            self.skipLines()
            
            if self.current_token.type == tokenList.TT_ARROW:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "'->' not allowed in class methods",
                    'exit': False
                }))
            
            
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a newline",
                    'exit': False
                }))
            
            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error: return res
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                methods.append({
                    'name': method_name,
                    'value': FunctionNode(method_name, args_list, body, False, default_values_list, "method"),
                    'args': args_list,
                    'pos_start': method_name.pos_start,
                    'pos_end': body.pos_end
                })
                
                if self.current_token.type != tokenList.TT_NEWLINE:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a 'end' or a newline",
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_start,
                    'message': "Expected 'end'",
                    'exit': False
                }))
                
        self.methods = methods
        # ini_args = []
        # for method in self.methods:
        #     if method['name'].value == "init":
        
        return methods
    
    def match_expr(self):
        res = ParseResult()
        cases= []
        default_case = None
        
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'match'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'match'",
                'exit': False
            }))
            
        res.register_advancement()
        self.advance()
        
        expression = res.register(self.expr())
        if expression == "":
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected an expression',
                    'exit': False
                }
            ))
        if res.error: return res
        
        if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected ":"',
                        'exit': False
                    }
                ))
        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_NEWLINE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
                'exit': False
            }))
            
        res.register_advancement()
        self.advance()
        
        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()   
            if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                cases = []
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
            if self.current_token.matches(tokenList.TT_KEYWORD, "case"):
                cases = self.set_cases()
            elif self.current_token.matches(tokenList.TT_KEYWORD, "default"):
                default_case = res.register(self.set_default_case())
        if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                cases = []
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case)) 
            
        if self.current_token.matches(tokenList.TT_KEYWORD, "case"):
            cases = self.set_cases()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
        if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
            res.register_advancement()
            self.advance()
            return res.success(MatchNode(expression, cases, default_case))
        
        if self.current_token.matches(tokenList.TT_KEYWORD, "default"):
            default_case = self.set_default_case()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
        if self.current_token.matches(tokenList.TT_KEYWORD, "case"):
            cases = self.set_cases()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
        return res.failure(self.error['Syntax']({
            'pos_start': self.current_token.pos_start,
            'pos_end': self.current_token.pos_end,
            'message': "invalid syntax for match, expected 'end' or 'case'",
            'exit': False
        }))
        
    def set_cases(self):
        res = ParseResult()
        cases = []
        while self.current_token.matches(tokenList.TT_KEYWORD, "case"):
            res.register_advancement()
            self.advance()
            case_expr = res.register(self.expr())
            if res.error: return res
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected ":"',
                        'exit': False
                    }
                ))
            res.register_advancement()
            self.advance()
            
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a newline",
                    'exit': False
                }))
                
            res.register_advancement()
            self.advance()
            start_token = self.current_token
            statements = res.register(self.statements())
            
            if len(statements.elements) > 0:
                if statements.elements[0] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': start_token.pos_start,
                            'pos_end': start_token.pos_end,
                            'message': 'Expected an expression',
                            'exit': False
                        }
                    ))
            if res.error:
                return res
            cases.append({
                'case': case_expr,
                'body': statements,
                "pos_start": start_token.pos_start,
                "pos_end": statements.pos_end
            })
           
            if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                res.register_advancement()
                self.advance()
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected "end"',
                        'exit': False
                    }
                ))      
        
        
        
        return cases
      
    def set_default_case(self):
        res = ParseResult()
        default_case = {}
        if self.current_token.matches(tokenList.TT_KEYWORD, "default"):
            res.register_advancement()
            self.advance()
            default_case_expr = res.register(self.expr())
            if default_case_expr != "":
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'default case must be an empty expression',
                        'exit': False
                    }
                ))
            if res.error: return res
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected ":"',
                        'exit': False
                    }
                ))
            res.register_advancement()
            self.advance()
            
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a newline",
                    'exit': False
                }))
                
            res.register_advancement()
            self.advance()
            start_token = self.current_token
            statements = res.register(self.statements())
            
            if len(statements.elements) > 0:
                if statements.elements[0] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': start_token.pos_start,
                            'pos_end': start_token.pos_end,
                            'message': 'Expected an expression',
                            'exit': False
                        }
                    ))
            if res.error:
                return res
            default_case = {
                'case': default_case_expr,
                'body': statements,
                'pos_start': start_token.pos_start,
                'pos_end': start_token.pos_end
            }
            if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                res.register_advancement()
                self.advance()
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected "end"',
                        'exit': False
                    }
                ))
                
        return default_case
        
    def spread_expr(self, name, assign_token):
        res = ParseResult()
        res.register_advancement()
        self.advance()
        start_token = self.current_token
        dict_values = []
        if self.current_token.type == tokenList.TT_LBRACE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "cannot use spread operator on type 'dict' or 'object'",
                        'exit': False
                }))
                
        expr = res.register(self.expr())
        if res.error: return res
        if not isinstance(expr, ListNode) and isinstance(expr, PairNode) and isinstance(expr, DictNode) and isinstance(expr, ObjectNode):
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': start_token.pos_start,
                    'pos_end': start_token.pos_end,
                    'message': 'cannot spread a non-iterable',
                    'exit': False
                }
            ))
        spread_node = SpreadNode(assign_token, name, expr, start_token.pos_start, self.current_token.pos_end)
        return res.success(spread_node)
                         
    def list_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()
        
        if self.current_token.type != tokenList.TT_LSQBRACKET:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '['",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        start_token = self.current_token
        if self.current_token.type == tokenList.TT_RSQBRACKET:
            res.register_advancement()
            self.advance()
        else:
            while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                        
                    start_token = self.current_token
            element = res.register(self.expr())
            
            if res.error:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Epected an expression",
                    'exit': False
                }))
            elements.append(element)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    res.register_advancement()
                    self.advance()
                    return res.success(ListNode(elements, pos_start, self.current_token.pos_end))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                if self.current_token.type == tokenList.TT_MUL:
                    res.register_advancement()
                    self.advance()
                    current_token = self.current_token
                    if current_token.type != tokenList.TT_IDENTIFIER:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    rest = res.register(self.expr())
                    if res.error:
                        return res
                    elements.append(StringNode(Token(tokenList.TT_IDENTIFIER, str(
                        "*") + str(rest.name.value), current_token.pos_start, current_token.pos_end)))
                    if self.current_token.type != tokenList.TT_RSQBRACKET:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected ']'",
                            'exit': False
                        }))
                    res.register_advancement()
                    self.advance()
                    return res.success(ListNode(elements, pos_start, self.current_token.pos_end.copy()))
                element = res.register(self.expr())
                if res.error:
                    return res
                elements.append(element)
                
                if element == "":
                    elements.pop()
                    continue
            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    res.register_advancement()
                    self.advance()
                    return res.success(ListNode(elements, pos_start, self.current_token.pos_start.copy()))
            
            
            
            if self.current_token.type != tokenList.TT_RSQBRACKET:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': start_token.pos_start,
                    'pos_end': start_token.pos_end,
                    'message': "Expected an expression, ',', or ']'",
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            for element in elements:
                if element == "":
                    elements.pop()
                    continue
        
            if self.current_token != None and self.current_token.type in operation_methods:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'exit': False
                }))
        
        return res.success(ListNode(elements, pos_start, self.current_token.pos_end.copy()))

    def pair_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LPAREN:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '('",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        start_token = self.current_token
        if self.current_token.type == tokenList.TT_RPAREN:
            res.register_advancement()
            self.advance()
        else:
            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                start_token = self.current_token
            element = res.register(self.expr())
            if res.error:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Epected an expression",
                    'exit': False
                }))
            elements.append(element)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RPAREN:
                    res.register_advancement()
                    self.advance()
                    return res.success(PairNode(elements, pos_start, self.current_token.pos_start.copy()))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                if self.current_token.type == tokenList.TT_MUL:
                    res.register_advancement()
                    self.advance()
                    current_token = self.current_token
                    if current_token.type != tokenList.TT_IDENTIFIER:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    rest = res.register(self.expr())
                    if res.error: return res
                    elements.append(StringNode(Token(tokenList.TT_IDENTIFIER, str("*")+ str(rest.name.value), current_token.pos_start, current_token.pos_end)))
                    if self.current_token.type != tokenList.TT_RPAREN:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected ')'",
                            'exit': False
                        }))
                    res.register_advancement()
                    self.advance()
                    return res.success(PairNode(elements, pos_start, self.current_token.pos_end.copy()))
                
                
                element = res.register(self.expr())
                if res.error: return res
                elements.append(element)
                if element == "":
                    elements.pop()
                    continue
            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RPAREN:
                    res.register_advancement()
                    self.advance()
                    return res.success(PairNode(elements, pos_start, self.current_token.pos_start.copy()))
            
            
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an expression, ',', or ')'",
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            for element in elements:
                if element == "":
                    elements.pop()
                    continue
                
            if self.current_token != None and self.current_token.type in operation_methods:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'exit': False
                }))
        return res.success(PairNode(elements, pos_start, self.current_token.pos_end.copy()))

    def string_interp(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        inter_pv = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'fm'):
            res.register_advancement()
            self.advance()
            string_to_interp = self.current_token.value
            while self.current_token.type == tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING or tokenList.TT_BACKTICK:
                value = self.current_token.value
                regex = Regex().compile('%{(.*?)}')
                # we need to allow escaping of the %{}
                # check if the string has a double % and double { and double }
                regex2 = Regex().compile('%%{{(.*?)}}')
                if regex2.match(value):
                    value = regex2.sub('%{\\1}', value)
                if value.find('{{') != -1:
                    value = value.replace('{{', '{')
                    value = value.replace('}}', '}')
                interp_values = regex.match(value)
                if interp_values:
                    inter_pv = interp_values
                    expr = res.register(self.expr())
                    interpolated_string = self.make_string_expr(
                        inter_pv, expr.pos_start)
                    return res.success(StringInterpNode(expr,  interpolated_string, string_to_interp, pos_start, self.current_token.pos_end.copy(),inter_pv))
                else:
                    expr = res.register(self.expr())
                    return res.success(StringInterpNode(expr, value, string_to_interp, pos_start, self.current_token.pos_end.copy()))
            else:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a string",
                    'exit': False
                }))
        return res.success(StringNode(self.current_token))
    
    def make_string_expr(self, inter_pv, position):
        interpolated = []
        for el in inter_pv:
            lexer = Lexer(self.file_name, el, position)
            token, error = lexer.make_tokens()
            parser = Parser(token, self.file_name, position)
            ast = parser.parse()
            for element in ast.node.elements:
                interpolated.append(element)
                self.string_expr = interpolated
        return self.string_expr
    
    def index_get(self, atom):
        res = ParseResult()
        index = 0
        if self.current_token.type == tokenList.TT_LSQBRACKET:
            res.register_advancement()
            self.advance()
            index = res.register(self.expr())
            if isinstance(index, ListNode) or isinstance(index, PairNode):
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'exit': False
                }))
            if res.error: return res
            
            if self.current_token.type == tokenList.TT_RSQBRACKET:
                self.skipLines()
                if self.current_token.type == tokenList.TT_EQ:
                    res.register_advancement()
                    self.advance()
                    value = res.register(self.expr())
                    if value == "":
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an expression",
                            'exit': False
                        }))

                    if res.error: return res
                    return res.success(IndexNode(atom, index, value,"="))
                return res.success(IndexNode(atom, index))
            
            
            elif self.current_token.type == tokenList.TT_COLON:
                res.register_advancement()
                self.advance()
                start = index if index != "" else None
                end = res.register(self.expr())
                if res.error: return res
                if self.current_token.type == tokenList.TT_COLON:
                    res.register_advancement()
                    self.advance()
                    step = res.register(self.expr())
                    if res.error: return res
                    if self.current_token.type == tokenList.TT_RSQBRACKET:
                        res.register_advancement()
                        self.advance()
                        if end == "":
                            end = None
                        return res.success(SliceNode(atom, start, end, step=step, type="colon"))
                elif self.current_token.type == tokenList.TT_RSQBRACKET:
                    res.register_advancement()
                    self.advance()
                    if end == "":
                        end = None
                    return res.success(SliceNode(atom, start, end, step=None))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ']'",
                        'exit': False
                    }))
            
            elif self.current_token.type == tokenList.TT_DOUBLE_COLON:
                self.skipLines()
                start = index if index != "" else None
                end = res.register(self.expr())
                type_ = "double_colon"
                if res.error: return res
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    self.skipLines()
                    if end == "":
                        end = None
                    return res.success(SliceNode(atom, start, end, step=None, type=type_))
                else:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ']'",
                        'exit': False
                    }))
            
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid index expression",
                    'exit': False
                }))
        
    def raise_expr(self):
        res = ParseResult()
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'raise'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'raise'",
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            _Exception = res.register(self.expr())
            if res.error: return res
            return res.success(RaiseNode(_Exception))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
     
    def del_expr(self):
        res = ParseResult()
        expression = None
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'del'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'del'",
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        identifier = self.current_token
        if identifier == "":
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an expression",
                'exit': False
            }))
        if identifier.type == tokenList.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_DOT:
                res.register_advancement()
                self.advance()
                expression = res.register(self.access_property(identifier))
                return res.success(DelNode(identifier, expression))
            elif self.current_token.type == tokenList.TT_LSQBRACKET:
                expression = res.register(self.expr())
                return res.success(DelNode(identifier, expression))
            else:
                if self.current_token.type != tokenList.TT_NEWLINE and self.current_token.type != tokenList.TT_EOF:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid del expression",
                        'exit': False
                    }))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        if res.error: return res
        return res.success(DelNode(identifier, expression))
              
    def attempt_expr(self):
        res = ParseResult()
        exception = None
        attempt_statement = {}
        catches = []
        catch_statement = {}
        finally_statement = {}
        pos_start = self.current_token.pos_start.copy()
        if not self.current_token.matches(tokenList.TT_KEYWORD, "attempt"):
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected "attempt"',
                    'exit': False
                }
            ))
        start_token = self.current_token   
        res.register_advancement()
        self.advance()
        
        if self.current_token.type != tokenList.TT_COLON:
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected ":"',
                    'exit': False
                }
            ))      
      
        res.register_advancement()
        self.advance()
        attempt_statements = res.register(self.statements())
        attempt_statement = {
            'body': attempt_statements,
            'pos_start': start_token.pos_start,
            'pos_end': attempt_statements.pos_end
        }
        for statement in attempt_statements.elements:
            if statement == None or statement == '':
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': start_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'attempt statement cannot be empty',
                        'exit': False
                    }
                ))
        while self.current_token.type == tokenList.TT_NEWLINE:
            self.skipLines() 
        
        
        while self.current_token.matches(tokenList.TT_KEYWORD, "catch"):
            self.skipLines()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                    exception = {
                        'name': self.current_token,
                        'as': None,
                    }
                    self.skipLines()
                    if self.current_token.matches(tokenList.TT_KEYWORD, "as"):
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            self.error_detected = True
                            return res.failure(self.error['Syntax'](
                                {
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': 'Expected an identifier',
                                    'exit': False
                                }
                            ))
                        exception['as'] = self.current_token
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_COLON:
                            self.error_detected = True
                            return res.failure(self.error['Syntax'](
                                {
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': 'Expected ":"',
                                    'exit': False
                                }
                            ))
                        self.skipLines()
                        statements = res.register(self.statements())
                        catch_statement = {
                            'exception': exception,
                            'body': statements,
                            'pos_start': exception['name'].pos_start,
                            'pos_end': exception['name'].pos_end
                        }
                        catches.append(catch_statement)
                    else:
                        if self.current_token.type != tokenList.TT_COLON:
                            self.error_detected = True
                            return res.failure(self.error['Syntax'](
                                {
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': 'Expected ":"',
                                    'exit': False
                                }
                            ))
                        self.skipLines()
                        statements = res.register(self.statements())
                        catch_statement = {
                            'exception': exception,
                            'body': statements,
                            'pos_start': exception['name'].pos_start,
                            'pos_end': exception['name'].pos_end
                        }
                        catches.append(catch_statement)
            else:   
                if self.current_token.type != tokenList.TT_COLON:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'Expected ":"',
                            'exit': False
                        }
                    ))
                self.skipLines()
                statements = res.register(self.statements())
                catch_statement = {
                    'exception': None,
                    'body': statements,
                    'pos_start': start_token.pos_start,
                    'pos_end': start_token.pos_end
                }
                catches.append(catch_statement)
        
        
        if self.current_token.matches(tokenList.TT_KEYWORD, "finally"):
            self.skipLines()
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected ":"',
                        'exit': False
                    }
                ))
            self.skipLines()
            statements = res.register(self.statements())
            finally_statement = {
                'body': statements,
                'pos_start': start_token.pos_start,
                'pos_end': statements.pos_end
            }
            
        # else:
        #     print("no finally", self.current_token)
        #     self.error_detected = True
        #     return res.failure(self.error['Syntax'](
        #         {
        #             'pos_start': start_token.pos_start,
        #             'pos_end': start_token.pos_end,
        #             'message': 'attempt statement must have a catch or finally clause',
        #             'exit': False
        #         }
        #     ))    
        
                
        while self.current_token.type == tokenList.TT_NEWLINE:
            self.skipLines()
        # if self.current_token.matches(tokenList.TT_KEYWORD, "catch"):
        #     self.error_detected = True
        #     return res.failure(self.error['Syntax']({
        #             'pos_start': self.current_token.pos_start,
        #             'pos_end': self.current_token.pos_end,
        #             'message': 'multiple catch clauses not supported' if self.current_token.matches(tokenList.TT_KEYWORD, "catch") else 'multiple default clauses not supported',
        #             'exit': False
        #         }))
        if  not self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                self.error_detected = True
                if self.current_token.matches(tokenList.TT_KEYWORD, "finally") or self.current_token.matches(tokenList.TT_KEYWORD, "catch"):
                    return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'invalid syntax',
                            'exit': False
                    }))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'Expected "end"',
                        'exit': False
                    }))
        self.skipLines()
        attempt_node = AttemptNode(attempt_statement, catches, finally_statement, pos_start, self.current_token.pos_end)
        return res.success(attempt_node)        
    
    def get_expr(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'get'):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected an identifier",
                    'exit': False
                }))
                
            module_name = self.current_token
            res.register_advancement()
            self.advance()
            
            
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'from'):
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected 'from'",
                    'exit': False
                }))
                
            res.register_advancement()
            self.advance()
            
            if self.current_token.type != tokenList.TT_DOUBLE_STRING and self.current_token.type != tokenList.TT_SINGLE_STRING:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected a string",
                    'exit': False
                }))
                
            module_path = self.current_token

            res.register_advancement()
            self.advance()

            return res.success(GetNode(module_name, module_path))
    
    def module_expr(self):
        res = ParseResult()
        module_properties = []
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'module'):
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'module'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))

        module_name = self.current_token
        if module_name.value != 'Export':
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'Export'",
                'exit': False
            }))
        if module_name in tokenList.KEYWORDS:
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as object name",
                'exit': False
            }))
        if isOnlyLetters(module_name.value) == False:
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use non-letter characters as object name",
                'exit': False
            }))
        if isFirstLetterUpper(module_name.value) == False:
            return res.failure(self.error['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Object name must start with a capital letter",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        # if self.current_token.type == tokenList.TT_EQ:
        #     res.register_advancement()
        #     self.advance()
        #     module_value = self.current_token
        #     if module_value.type != tokenList.TT_IDENTIFIER:
        #         return res.failure(self.error['Syntax']({
        #             'pos_start': self.current_token.pos_start,
        #             'pos_end': self.current_token.pos_end,
        #             'message': "Expected an identifier",
        #             'exit': False
        #         }))
        #     return res.success(ModuleExport(module_name, module_value))
        as_name = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'as'):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_IDENTIFIER and self.current_token.type != tokenList.TT_KEYWORD:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))
            as_name = self.current_token
            res.register_advancement()
            self.advance()
        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
                'exit': False
            }))

        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()

                module_properties.append({
                    'name': module_name,
                    'value': [],
                    'pos_start': module_name.pos_start,
                    'pos_end': module_name.pos_end
                })
                return res.success(ModuleObject(module_name, module_properties))
            if self.current_token.type != tokenList.TT_IDENTIFIER and str(self.current_token.value) not in tokenList.DIGITS:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))

            while self.current_token.type == tokenList.TT_IDENTIFIER or str(self.current_token.value) in tokenList.DIGITS:

                mod_name = self.current_token
                if res.error:
                    return res
                # mod_name cannot start with a @ or a symbol
                if mod_name.value[0] == '@' or mod_name.value[0] in tokenList.SYMBOLS:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Object name cannot start with a symbol",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()

                if self.current_token.type != tokenList.TT_COLON:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ':'",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_IDENTIFIER:

                    if self.current_token.value == 'self':
                        self.current_token.value = module_name.value
                mod_value = res.register(self.expr())
                module_properties.append({
                    'name': mod_name,
                    'value': mod_value,
                    'pos_start': mod_name.pos_start,
                    'pos_end': self.current_token.pos_end
                })

                #return res.success(ModuleObject(module_name, module_properties))

                if res.error:
                    return res
                if mod_value == '':
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected property value",
                        'exit': False
                    }))
                if self.current_token.type == tokenList.TT_COMMA:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unexpected token, expected a newline",
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_NEWLINE:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a newline",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()

                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()
                    object_type = {
                            "name": "module",
                            "as_name": as_name,
                        }
                    return res.success(ModuleObject(module_name, module_properties, object_type))
                if self.current_token.value in tokenList.NOT_ALLOWED_OBJECTS_KEYS:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unterminated object literal, Object key '{}' is not allowed".format(self.current_token.value),
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    while self.current_token.type == tokenList.TT_NEWLINE:
                        res.register_advancement()
                        self.advance()
                        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                            res.register_advancement()
                            self.advance()
                            object_type = {
                                "name": "module",
                                "as_name": as_name,
                            }
                            return res.success(ModuleObject(module_name, module_properties, object_type))
                    if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected 'end' or you have forgottem to close a newline",
                            'exit': False
                        }))
                    else:
                        res.register_advancement()
                        self.advance()
                        
                        object_type = {
                            "name": "module",
                            "as_name": as_name,
                        }
                        return res.success(ModuleObject(module_name, module_properties, object_type))
            
            object_type = {
                "name": "module",
                "as_name": as_name,
            }
            return res.success(ModuleObject(module_name, module_properties, object_type))
    
    def export_expr(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'export'):
            res.register_advancement()
            self.advance()
            modules = []
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                module = self.current_token
                res.register_advancement()
                self.advance()
                modules.append(module)
                if self.current_token.type == tokenList.TT_NEWLINE:
                    return res.success(ExportModuleNode(modules))
                elif self.current_token.type == tokenList.TT_EOF:
                    return res.success(ExportModuleNode(modules))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"Expected a newline",
                        'exit': False
                    }))
                # if self.current_token.type == tokenList.TT_COMMA:
                #     while self.current_token.type == tokenList.TT_COMMA:
                #         res.register_advancement()
                #         self.advance()
                #         current_token = self.current_token
                #         if current_token.type != tokenList.TT_IDENTIFIER:
                #             return res.failure(self.error['Syntax']({
                #                 'pos_start': self.current_token.pos_start,
                #                 'pos_end': self.current_token.pos_end,
                #                 'message': f"Expected an identifier",
                #                 'exit': False
                #             }))
                #         res.register_advancement()
                #         self.advance()
                #         modules.append(current_token)
            # else:
            #     expr = res.register(self.expr())
            #     if isinstance(expr, ListNode):
            #         for element in expr.elements:
            #             if isinstance(element, VarAccessNode) != True:
            #                 return res.failure(self.error['Syntax']({
            #                     'pos_start': self.current_token.pos_start,
            #                     'pos_end': self.current_token.pos_end,
            #                     'message': f"Expected an identifier, or perhaps you forgot to close the list?",
            #                     'exit': False
            #                 }))
            #             modules.append(element)
            #     else:
            #         return res.failure(self.error['Syntax']({
            #             'pos_start': self.current_token.pos_start,
            #             'pos_end': self.current_token.pos_end,
            #             'message': f"Expected an identifier or list of identifiers",
            #             'exit': False
            #         }))
        return res.success(ExportModuleNode(modules))
          
    def binaryOperation(self, func_1, ops, func_2=None):
        if func_2 == None:
            func_2 = func_1

        res = ParseResult()
        left = res.register(func_1())
        if res.error:
            self.error_detected = True
            return res
        
        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(func_2())
            if res.error:
                return res
            try:
                left = BinOpNode(left, op_tok, right)
            except:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Invalid syntax",
                    'exit': False
                }))
        return res.success(left)



            


li = [1,2,3,4,5,6,7,8,9,10]
# print(li[])

# pa = (1,2,3,4,5,6,7,8,9,10)
# print(pa[:2:1])
# di = {'name1':'james', 'name2':'bond'}
# print(di['name1'])
# def getname(name):
#     return di[name]
# print(getname('name1'))
# name = 'james'
# print(name[::-1])

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SYMBOLS = '@_'
num = 123
num2 = 123.456
LETTERS_SYMBOLS = LETTERS + SYMBOLS


# class Test:
#     def test(a, b):
#         return a + b

# test.go = 1
# # print all test attributes
# print(test)
# num = 1
# for i in range(10):
#     num = num + i
#     print(f"num = {num}")
# hello = 'hello'
# world = 'world'
# li += "hello"
# print(li * 2)
# a = 20
# b = 30
# a = b
# print(a)
# num = 16
# # fizzbuzz
# for i in range(num):
#     print(i)
# a = 20
# b = 30
# c = a+1
# d = b+1
# e = a-1
# f = int("40")
# def setnum():
#     return 2

# a += setnum() + 1 # expecting to 23
# b -= setnum() - 1 # expecting to 29
# c /= setnum() / 2 # expecting to 21.0
# d *= setnum() * 2 # expecting to 120
# e %= setnum() % 3 # expecting to 1
# print(f"a = {a}, b = {b}, c = {c}, d = {d}, e = {e}")
# count = 0
# for i in range(1, 10):
#     for j in range(1, 10):
#         for k in range(1, 10):
#             if i != j and i != k and j != k:
#                 count += 1
#                 print(f"{i} * {j} * {k} = {i*j*k}")
# print(count)
# r = 'name'
# li = [1,2,]
# d = {2:1, 3:2, 4:3}
# li2 = [4,5,6]
# new_li = [*li, *li2, 7, 8, 9]
# print(hasattr(d, "2"))
# num1 = 0
# class Test:
#     pass
# def greet(name):
#     pass
# try:
#     print(greet())
# except NameError as e:
#     print(f"Error: {e}")
# except Exception as e:
#     print(f"Exception: {e}")
# except TypeError as TypeError:
#     print(f"TypeError: {TypeError}")
# finally:
#     print("Finally")
# name = "Kenny"
# def greet(name):
#     return f"Hello, {name}"
  
# pair = ("a", "e", "i", "o", "u", 'e')
# list = [1,2,3,4,5,6,7,8,9,10]
# dict = {'name': 'Kenny', 'age': 23, 'hobby': 'Playing soccer'}
# strn = "Hello, World!"
# class Employee:
#     def create(self,name):
#         return f"Hello, {name}"
# data = {}
# if data or {}:
#     print("data is empty")
# else:
#     print("data is not empty")

# print(f"'not' operator on true: %{not(True)}")  # false
# print(f"'not' operator on false: %{not(False)}") # true
# print(f"'not' operator on none: %{not(None)}")  # true
# print(f"'not' operator on int: %{not(1)}")     # false
# print(f"'not' operator on float: %{not(1.0)}") # false
# print(f"'not' operator on string: %{not('')}") # true
# print(f"'not' operator on list: %{not([])}")  # false
# print(f"'not' operator on pair: %{not(pair)}") # false
# print(f"'not' operator on dict: %{not(dict)}") # false
# print(f"'not' operator on class: %{not(Employee)}") # false
# print(f"'not' operator on function: %{not(greet)}") # false
# print(f"'not' operator on builtin_function: %{not(print)}") # false
# print(f"'not' operator on builtin_class: %{not(Exception)}") # false
# print(f"'not' operator on builtin_method: %{not(strn.upper)}") # false
# print(f"'not' operator on builtin_type: %{not(strn)}") # false
# print(f"'not' operator on none: %{not(None)}") # false
# l = [1,2,3,4,5,6,7,8,9,10]
# l += {'name': 'Kenny'}
# print(l)
# num = 2
# num **= 0
# print("num is: %d" % num)
# x = range(1,10)
# # for i in x:
# #     print(i)

# employee = Employee()
# print(employee)

class Animal:
    animals = []
    def __init__(self, name):
        self.name = name
    def eat(self):
        print(f"{self.name} is eating")
    def set_animals(self):
        self.animals.append(self.name)
    
    def get_animals(self):
        return self.animals
        
animal = Animal("Dog")
animal2 = Animal("Cat")
animal3 = Animal("Bird")
animal.set_animals()
animal2.set_animals()
animal3.set_animals()
print(animal.get_animals())
print(dict(key="name", value="Bob", age=23))
def greet(name, age=None, email=""):
    print("SENDING EMAIL")
    print(f"Hello, {name}, you are {age} years old and your email is {email}")

greet("John",'21')
