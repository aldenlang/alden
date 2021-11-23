import os
from Parser.stringsWithArrows import *
from Token.token import Token
import Token.tokenList as tokenList
from Memory.memory import Record
import sys
import re
import time

regex = '[+-]?[0-9]+\.[0-9]+'

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


def isEmptyString(value):
    return value == ""
            
class TypeOf:
    def __init__(self, type):
        self.type = type

    def getType(self):
        result = ''
        if self.type == 'true':
            result = 'boolean'
        elif self.type == 'false':
            result = 'boolean'
        elif self.type == 'none':
            result = 'none'
        elif self.type == 'str':
            result = 'string'
        elif self.type == 'tuple':
            result = 'pair'
        elif isinstance(self.type, Number):
            if re.match(regex, str(self.type)):
                result = 'float'
            else:
                result = 'int'
        else:
            if isinstance(self.type, str) or isinstance(self.type, String):
                result = 'string'
            elif isinstance(self.type, tuple):
                result = 'pair'
            elif isinstance(self.type, dict):
                result = 'object'
            elif isinstance(self.type, bool) or isinstance(self.type, Boolean):
                result = 'boolean'
            elif isinstance(self.type, list) or isinstance(self.type, List):
                result = 'list'
            else:
                result = type(self.type).__name__
        return result


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbolTable = None


def setNumber(token):
    value = "none"
    if not token and token != 0:
        value = 0
    if token == 'true':
        value = 1
    elif token == 'false':
        value = 0
    elif token == 'none':
        value = 0
    else:
        value = token
    if hasattr(token, 'value'):
        if token.value == 'true':
            value = 1
        elif token.value == 'false':
            value = 0
        elif token.value == 'none':
            value = 0
        else:
            value = token.value
    return value


class Program:
    def error():
        def Default(detail):
            error = f"\n{detail['name']}: {detail['message']}\n"
            if detail['exit']:
                Program.printErrorExit(error)
            else:
                Program.printError(error)
                
        def Error(detail):
            isDetail = {
                'name': detail['name'],
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def IllegalCharacter(options):
            error = f'\nIllegal character: {options["originator"]}\n\nin File: {options["pos_start"].fileName} at line {options["pos_start"].line + 1}\n'
            Program.printErrorExit(error)

        def Syntax(detail):
            isDetail = {
                'name': 'SyntaxError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def Runtime(detail):
            isDetail = {
                'name': 'RuntimeError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
     

        def Type(detail):
            isDetail = {
                'name': 'TypeError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
                
        def KeyError(detail):
            isDetail = {
                'name': 'KeyError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
                
        def ValueError(detail):
            isDetail = {
                'name': 'ValueError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        methods = {
            'Default': Default,
            'Error': Error,
            'IllegalCharacter': IllegalCharacter,
            'Syntax': Syntax,
            'Runtime': Runtime,
            'Type': Type,
            'KeyError': KeyError,
            'ValueError': ValueError
        }
        return methods

    def NoneValue():
        return 'none'

    def print(*args):
        for arg in args:
            print(arg)

    def printWithType(*args):
        for arg in args:
            print(str(type(arg)) + " <===> " + str(arg))

    def printError(*args):
        for arg in args:
            print(arg)

    def printErrorExit(*args):
        for arg in args:
            print(arg)
        sys.exit(1)

    def asString(detail):
        result = f'\n{detail["name"]}: {detail["message"]}\n'
        result += f'\nin File {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}'
        result += '\n\n' + \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        return result

    def asStringTraceBack(detail):
        result = Program.generateTraceBack(detail)
        result += f'\n{detail["name"]}: {detail["message"]}\n'
        result += '\n\n' + \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        return result

    def generateTraceBack(detail):
        result = ''
        pos = detail['pos_start']
        context = detail['context']

        while context:
            result += f'\nFile {detail["pos_start"].fileName}, line {str(pos.line + 1)}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        return '\nStack trace (most recent call last):\n' + result


class RuntimeResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_continue = False
        self.loop_break = False

    def register(self, res):
        if hasattr(res, 'value' and 'error' and 'func_return_value' and 'loop_break' and 'loop_continue'):
            self.error = res.error
            self.func_return_value = res.func_return_value
            self.loop_continue = res.loop_continue
            self.loop_break = res.loop_break
            return res.value
        else:
            return res
    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def noreturn(self):
        self.reset()
        return self

    def should_return(self):
        return (
            self.error or
            self.func_return_value or
            self.loop_continue or
            self.loop_break
        )


class Value:
    def __init__(self):
        self.setPosition()
        self.setContext()

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self
    
    def setTrueorFalse(self, value):
        return "true" if value else "false"
        #return self


    def added_to(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def subtracted_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def multiplied_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def divided_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def powred_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def modulo(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def get_comparison_eq(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def get_comparison_ne(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def get_comparison_lt(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def get_comparison_gt(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def get_comparison_lte(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def get_comparison_gte(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context,
        })

    def and_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def or_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context
        })

    def notted(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context,
            'exit': False
        })

    def execute(self, args):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(args).getType()}",
            'context': self.context
        }
        return RuntimeResult().failure(self.illegal_operation_typerror(error))

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return "false"

    def illegal_operation(self, error, other=None):
        if not other:
            other = self
        if hasattr(other, 'value'):
            return Program.error()["Syntax"]({
                'message': error['message'] if error['message'] else f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit'] if 'exit' in error else True
            })
        else:
            return Program.error()["Syntax"]({
                'message': f"Illegal operation",
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit']
            })
            
    def key_error(self, error, property):
            return Program.error()["Syntax"]({
                'message': error['message'],
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit'] if 'exit' in error else True
            })

    def none_value(self):
        return Program.NoneValue()

    def illegal_operation_typerror(self, error, other=None):
        errorDetail = {
            'pos_start': error['pos_start'],
            'pos_end': error['pos_end'],
            'message': error['message'],
            'context': error['context'],
            'exit': error['exit'] if 'exit' in error else False
        }
        if not other:
            other = self
        if not 'message' in error:
            if hasattr(other, 'value'):
                errorDetail['message'] = f'Illegal operation for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}'
                return Program.error()['Syntax'](errorDetail)
            else:
                errorDetail['message'] = f"illegal operation"
                return Program.error()['Syntax'](errorDetail)
        return Program.error()['Type'](errorDetail)


class Statement(Value):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else []
        self.value = self.elements

    def copy(self):
        copy = Statement(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        for element in self.elements:
            if element == None:
                return ""
            else:
                return str(element)
        return ''


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        self.value = "true" if value else "false"
        return self

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't add {TypeOf(self.value).getType()} to {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(self, Number) and isinstance(other, Number):
            return Number(self.value + other.value), None
        if isinstance(other, Number):
            if self.value == "none" or other.value == "none":
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
                return None, self.illegal_operation_typerror(error)
        else:
            return None, self.illegal_operation_typerror(error)

    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't subtract {TypeOf(self.value).getType()} from {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't subtract {TypeOf(self.value).getType()} from {TypeOf(other.value).getType()}",
                    'context': self.context
                }
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't multiply {TypeOf(self.value).getType()} with {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if self.value == "none" or other.value == "none":
            return None, self.illegal_operation_typerror(error)
        if hasattr(other, 'value'):
            if other.value == "true" or self.value == "true":
                return String(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
            elif other.value == "false" or self.value == "false":
                return String(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None

        if isinstance(other, Number):
            if other.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't multiply '{type(self.value).__name__}' of type 'none'",
                    'context': self.context,
                    'exit': False
                }
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def divided_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't divide {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                return None, self.illegal_operation_typerror(error)
            if other.value == 0:
                return None, Program.error()['Runtime']({
                    'pos_start': other.pos_start,
                    'pos_end': other.pos_end,
                    'message': 'division by zero',
                    'context': self.context,
                    'exit': False
                })
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def powred_by(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't power {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def modulo(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't perform modulo on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def get_comparison_eq(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        elif other.value == "none":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        elif other.value == "none":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) >= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def and_by(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)), None
        elif other.value == "none" or self.value == "none":
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't perform and on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                'context': self.context
            }
            return None, self.illegal_operation_typerror(error)
        if isinstance(other, String):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def or_by(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def notted(self):
        return self.setTrueorFalse(self.value).setContext(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def is_true(self):
        return self.value == "true" if self.value else "false"

    def __repr__(self):
        return str(self.value)


class String(Value):
    def __init__(self, value, arg=None):
        super().__init__()
        self.value = value
        self.id = value
        if arg:
            self.value = value + str(arg)
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        self.value = "true" if value else "false"
        return self

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform concatenation on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}" if hasattr(other, 'value') and hasattr(self, 'value') else f"can't perform concatenation on type none",
            'context': self.context,
            'exit': False
        }
        if hasattr(other, 'value') and hasattr(self, 'value'):
            if other.value == "true" or other.value == "false" or other.value == "none" or self.value == "true" or self.value == "false" or self.value == "none":
                return None, self.illegal_operation_typerror(error, other)
        if isinstance(other, Number):
            return None, self.illegal_operation_typerror(error, other)
        if isinstance(other, String):
            return String(setNumber(str(self.value)) + setNumber(str(other.value))).setContext(self.context), None
        else:
            return "none", self.illegal_operation(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform multiplication on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if other.value == "true":
            return String(setNumber(str(self.value)) * setNumber(str(other.value))).setContext(self.context), None
        elif other.value == "false":
            return String(setNumber(str(self.value)) * setNumber(str(other.value))).setContext(self.context), None
        elif other.value == "none" or self.value == "none":
            return None, self.illegal_operation_typerror(error)
        if isinstance(other, String):

            return None, self.illegal_operation_typerror(error)

        if isinstance(other, Number):
            return String(setNumber(str(self.value)) * setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(self, error, other)

    def and_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None

    def get_comparison_eq(self, other):
        return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
    
    
    def get_comparison_ne(self, other):
        return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None

    def copy(self):
        copy = String(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def is_true(self):
        return "true" if len(self.value) > 0 else "false"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"'{self.value}'"


class Boolean(Value):
    def __init__(self, value):
        super().__init__()
        if value == True or value == "true":
            self.value = "true"
        elif value == False or value == "false":
            self.value = "false"
        self.setPosition(0, 0)
        self.setContext(None)

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def copy(self):
        copy = Boolean(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'


class NoneType(Value):
    def __init__(self):
        super().__init__()
        self.value = 'none'
        self.setPosition(0, 0)
        self.setContext("none")

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def copy(self):
        copy = NoneType()
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def get_comparison_eq(self, other):
        return self.setTrueorFalse(other.value == "none"), None
    
    def get_comparison_ne(self, other):
        return self.setTrueorFalse(other.value != "none"), None
    
    def and_by(self, other):
        return self.setTrueorFalse(other.value == "none"), None
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'


Boolean.true = Boolean("true")
Boolean.false = Boolean("false")
NoneType.none = NoneType()




class Pair(Value):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else ()
        self.value = self.elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements += other
        return new_list, None

    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on pair",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements = new_list.elements[:-other.value]
                return new_list, None
            except:
                return None, "none"
        else:
            return None, self.illegal_operation(error, other)

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on pair",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, self.none_value()
        else:
            error['message'] = f"Pair index must be a number not {TypeOf(other).getType()}"
            return None, self.illegal_operation(error, other)
        
    def len(self):
        return Number(len(self.elements))

    def copy(self):
        copy = Pair(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        try:
            return f'({", ".join([str(x) for x in self.elements])})'
        except:
            return "()"


class List(Value):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else []
        self.value = self.elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on list",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, "none"
        else:
            return None, self.illegal_operation(error, other)

    def divided_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Did you mean to use the `:` operator to get the element at a certain index?",
            'context': self.context,
            'exit': False
        }
        return None, self.illegal_operation_typerror(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on list",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, self.illegal_operation(error, other)

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on list",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, self.none_value()
        else:
            return None, self.illegal_operation(error, other)

    def get_element_at(self, index):
        return self.elements[index]

    def set_element_at(self, index, value):
        self.elements[index] = value
        return self

    def length(self):
        return len(self.elements)

    def copy(self):
        copy = List(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    
    def __str__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

   
class Object(Value):
    def __init__(self, name, properties):
        super().__init__()
        self.properties = properties if properties is not None else {}
        self.value = self.properties
        self.id = name
        self.name = name
        self.get_property = self.get_property
       
    def set_property(self, key, value):
        self.properties[key] = value
        return self
    
    def get_property(self, obj, key):
        value = ""
        if type(key).__name__ == "String":
            if key.value in obj.properties:
                value = obj.properties[key.value]
                return value
            else:
                return NoneType.none
        return value
    
    def get_key(self, key):
        if key.value in self.properties:
            return self.properties[key.value]
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"Key '{key}' not found in {self.name}",
                'context': self.context,
                'exit': False
            }
        return None, self.key_error(error, key)
    
    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on object",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                list_values = list(self.properties)
                return self.properties[list_values[other.value]], None
            except:
                return None, self.none_value()
        else:
            return None, self.illegal_operation(error, other)
            
    def get_comparison_eq(self, other):
        return Boolean(self.setTrueorFalse(self.value == other.value)), None
    
    def get_comparison_ne(self, other):
        return Boolean(self.setTrueorFalse(self.value != other.value)), None
        
    def get_comparison_lt(self, other):
        return Boolean(self.setTrueorFalse(self.value < other.value)), None
        
    def get_comparison_gt(self, other):
        return Boolean(self.setTrueorFalse(self.value > other.value)), None
    
    def get_comparison_lte(self, other):
        return Boolean(self.setTrueorFalse(self.value <= other.value)), None
    
    def get_comparison_gte(self, other):
        return Boolean(self.setTrueorFalse(self.value >= other.value)), None
        
    
    
    def copy(self):
        copy = Object(self.name, self.properties)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    def __str__(self):
        try:
            return f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
        except:
            return "{}"
    
    def __repr__(self):
        return "<Object {}>".format(self.name)
        
        
class ObjectGet(Value):
    def __init__(self, obj, key):
        super().__init__()
        self.obj = obj
        self.key = key
        self.get_property = self.get_property
        self.value = self.get_property
        self.get_type = "ObjectGetNode"
        
    def get_property(self, obj, key):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Property '{key}' does not exist on object '{obj}'",
            'context': self.context,
            'exit': False
        }
        value  = ""
        if type(key).__name__ == "String":
            if hasattr(obj, "properties"):
                if key.value in obj.properties:
                    value = obj.properties[key.value]
                    return value
                else:
                    return NoneType.none
            else:
                return NoneType.none
            
        elif type(key).__name__ == "Number":
            if hasattr(obj, "properties"):
                if str(key.value) in obj.properties:
                    value = obj.properties[str(key.value)]
                    return value
                else:
                    return NoneType.none
            else:
                return NoneType.none
        else:
            return None, self.illegal_operation(error, key)
  
    
class ObjectRefNode(Value):
    def __init__(self, value, arg=None):
        super().__init__()
        self.id = value
        self.value = value
        if arg:
            self.value = value + str(arg)

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        self.value = "true" if value else "false"
        return self
    
    def copy(self):
        copy = ObjectRefNode(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"'{self.value}'"


class BaseTask(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbolTable = Record(new_context.parent.symbolTable)
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()
    
        if len(args) > len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args)} argument(s) given, but {self.name}() expects {len(arg_names)}",
                'context': self.context,
                'exit': False
            }))

        if len(args) < len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args)} few argument(s) given, but {self.name if self.name != 'none' else 'annonymous'}() expects {len(arg_names)}",
                'context': self.context,
                'exit': False
            }))
        return res.success(None)

    def populate_args(self, arg_names, args, exec_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.setContext(exec_context)
            exec_context.symbolTable.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Task(BaseTask):
    def __init__(self, name, body_node, arg_names, implicit_return, ref=None):
        super().__init__(name)
        self.id = name
        self.name = name
        self.body_node = body_node
        self.arg_names = arg_names
        self.implicit_return = implicit_return
        self.args = arg_names
        self.ref = ref
    
       
        
    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        self.args = args
        res.register(self.check_and_populate_args(
            self.arg_names, args, exec_context))
        if res.should_return():
            return res
        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.should_return() and res.func_return_value == None:
            return res
        return_value = (
            value if self.implicit_return else None) or res.func_return_value or NoneType.none
        return res.success(return_value)


    def run(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        self.args = args
        res.register(self.run_check_and_populate_args(
            self.arg_names, args, exec_context))
        if res.should_return():
            return res
        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.should_return() and res.func_return_value == None:
            return res
        return_value = (
            value if self.implicit_return else None) or res.func_return_value or NoneType.none
        return res.success(return_value)
    
    def run_check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.run_populate_args(arg_names, args, exec_ctx)
        return res.success(None)
    
    def run_populate_args(self, arg_names, args, exec_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.setContext(exec_context)
            exec_context.symbolTable.set(arg_name, arg_value)

    def copy(self):
        copy = Task(self.name, self.body_node,
                    self.arg_names, self.implicit_return)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<Task {str(self.name) if self.name != 'none' else 'annonymous'}()>, {self.arg_names if len(self.arg_names) > 0 else '[no args]'}"


class Class(BaseTask):
    def __init__(self, class_name, constructor_args, inherit_class_name, inherit_class, methods):
        super().__init__(class_name)
        self.id = class_name
        self.class_name = class_name
        self.constructor_args = constructor_args
        self.inherit_class_name = inherit_class_name
        self.inherit_class = inherit_class
        self.methods = methods if methods else {}
        self.body_node = None
        
        
    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        new_context = self.generate_new_context()
        self.check_args(self.constructor_args, args)
        self.populate_args(self.constructor_args, args, self.context)
        
        # inject args into each method context
        for method_name, method in self.methods.items():
            method.setContext(self.context)
            # add constructor args names and values to method context
            for i in range(len(self.constructor_args)):
                arg_name = self.constructor_args[i]
                arg_value = args[i]
                method.context.symbolTable.set(arg_name.value, arg_value)
        
        return res.success(self)
        

    def set_method(self, key, value):
        self.methods[key] = value
        return self

    def get_method(self, method_name):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Method '{method_name}' does not exist on class '{self.class_name}'",
            'context': self.context,
            'exit': False
        }
        if isinstance(method_name, String):
            result = []
            for key, value in self.properties:
                if key == method_name.value:
                    result.append(value)
                    if len(result) == 0:
                        return None, self.key_error(error, method_name)
                    return value, None
            return "none", self.key_error(error, method_name)

    def copy(self):
        copy = Class(self.class_name, self.constructor_args,
                     self.inherit_class_name, self.inherit_class, self.methods)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __str__(self):
        try:
            return f"{{{', '.join([f'{k}: {v}' for k, v in self.methods.items()])}}}"
        except:
            return "{}"

    def __repr__(self):
        return f"<Class {str(self.class_name)}>"


class ClassGet(Value):
    def __init__(self, obj, key):
        super().__init__()
        self.obj = obj
        self.key = key
        print(type(key).__name__, key.value, "type")
        
        
    def get_method(self, obj, key):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Method '{key}' does not exist on class '{obj}'",
            'context': self.context,
            'exit': False
        }
        value  = ""
        if  type(key).__name__ == "ObjectRef":
            if hasattr(obj, "methods"):
                if key.value in obj.methods:
                    value = obj.methods[key.value]
                    return value
                else:
                    return NoneType.none
            else:
                return NoneType.none
        
            
        if type(key).__name__ == "String":
            if hasattr(obj, "methods"):
                if key.value in obj.methods:
                    value = obj.methods[key.value]
                    return value
                else:
                    return NoneType.none
            return NoneType.none
            
        elif type(key).__name__ == "Number":
            if hasattr(obj, "methods"):
                if str(key.value) in obj.methods:
                    value = obj.methods[str(key.value)]
                    return value
                else:
                    return NoneType.none
            else:
                return NoneType.none
        else:
            return None, self.illegal_operation(error, key)
        
    def copy(self):
        copy = ClassGet(self.obj, self.key)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
        
    def __repr__(self):
        return f"<ClassGet {str(self.obj)} {str(self.key)}>"

    
class BuiltInTask(BaseTask):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RuntimeResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visiit)

        res.register(self.check_and_populate_args(
            method.arg_names, args, exec_context))
        if res.should_return():
            return res

        return_value = res.register(method(exec_context))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visiit(self, node, exec_context):
        res = RuntimeResult()
        return res.failure(Program.error()['Runtime']({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name} is not a supported built-in task",
            'context': self.context,
            'exit': False
        }))

    def execute_len(self, exec_context):
        res = RuntimeResult()
        value = exec_context.symbolTable.get("value")
        if isinstance(value, Number):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"type {TypeOf(value).getType()} is not supported",
                'context': self.context,
                'exit': False
            }))
        if isinstance(value, List):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, String):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, Pair):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, Object):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, NoneType):
            return res.success(Number(0).setPosition(self.pos_start, self.pos_end).setContext(self.context))
    execute_len.arg_names = ["value"]
    
    
    

    def execute_append(self, exec_context):
        res = RuntimeResult()
        list = exec_context.symbolTable.get("list")
        value = exec_context.symbolTable.get("value")
        if isinstance(list, List):
            list.elements.append(value)
            return res.success(List(list.elements).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'append' must be a list.",
                'context': self.context,
                'exit': False
            }))
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_context):
        res = RuntimeResult()
        list = exec_context.symbolTable.get("list")
        index = exec_context.symbolTable.get("index")
        if isinstance(list, List):
            try:
                list.elements.pop(index.value)
                return res.success(List(list.elements).setPosition(self.pos_start, self.pos_end).setContext(self.context))
            except:
                return res.failure(Program.error()['Runtime']({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"Element at index {index.value} could not be removed from list because index is out of bounds",
                    'context': self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'pop' must be a list.",
                'context': self.context,
                'exit': False
            }))
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_context):
        res = RuntimeResult()
        list = exec_context.symbolTable.get("list")
        value = exec_context.symbolTable.get("value")
        if isinstance(list, List):
            list.elements.extend(value.value)
            return res.success(List(list.elements).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'extend' must be a list.",
                'context': self.context
            }))
    execute_extend.arg_names = ["list", "value"]

    def copy(self):
        copy = BuiltInTask(self.name)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<{str(self.name)}()>, [ built-in task ]"
  
    
def BuiltInTask_Print(args, node):
    res = RuntimeResult()
    for arg in args:
        value = str(arg)
        print(value, end="")
    return res.success(String(str(NoneType.none)).setPosition(node.pos_start, node.pos_end))


def BuiltInTask_PrintLn(args, node):
    res = RuntimeResult()
    for arg in args:
        value = str(arg)
        print(value)
    return res.success(String(str(NoneType.none)).setPosition(node.pos_start, node.pos_end))


def BuiltInTask_Input(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but input() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        try:
            input_value = input()
            return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
        except KeyboardInterrupt:
            return res.failure("KeyboardInterrupt")
    if len(args) == 1:
        if isinstance(args[0], String):
            try:
                input_value = input(args[0].value)
            except KeyboardInterrupt:
                return res.failure("KeyboardInterrupt")
            return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0]} is not a valid argument for input()",
                "context": context,
                'exit': False
            }))

def BuiltInTask_InputInt(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputInt() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        try:
            input_value = int(input())
        except KeyboardInterrupt:
            return res.failure("KeyboardInterrupt")
        return res.success(Number(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
    if len(args) == 1:
        if isinstance(args[0], String):
            while True:
                text = input(args[0].value)
                try:
                    number = int(text)
                    break
                except ValueError:
                    print("Invalid input, please try again")
                except KeyboardInterrupt:
                    return res.failure("KeyboardInterrupt")
            return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for inputInt()",
                "context": context,
                'exit': False
            }))

def BuiltInTask_InputFloat(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputFloat() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        try:
            input_value = float(input())
        except KeyboardInterrupt:
            return res.failure("KeyboardInterrupt")
        return res.success(Number(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
    if len(args) == 1:
        if isinstance(args[0], String):
            while True:
                text = input(args[0].value)
                try:
                    number = float(text)
                    break
                except ValueError:
                    print("Invalid input, please try again")
                except KeyboardInterrupt:
                    return res.failure("KeyboardInterrupt")
            return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for inputFloat()",
                "context": context,
                'exit': False
            }))

def BuiltInTask_InputBool(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputBool() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        input_value = bool(input())
        return res.success(Boolean(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
    if len(args) == 1:
        if isinstance(args[0], String):
            while True:
                text = input(args[0].value)
                try:
                    number = bool(text)
                    break
                except ValueError:
                    print("Invalid input, please try again")
            return res.success(Boolean(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for inputBool()",
                "context": context,
                'exit': False
            }))

def BuiltInType_Str(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but str() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], String):
        return res.success(args[0])
    if isinstance(args[0], Number):
        return res.success(String(str(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], Boolean):
        return res.success(String(str(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for str()",
        "context": context,
        'exit': False
    }))
    
    
#print(range(10))
    
def BuiltInType_Range(args, node, context):
    res = RuntimeResult()
    # built in range takes 1 or 3 arguments eg range(5) or range(1, 5) or range(1, 5, 2)
    #print(args)
    if len(args) not in [1, 3]:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but range() takes 1 or 3 arguments",
            "context": context,
            'exit': False
        }))
    if len(args) == 1:
        if isinstance(args[0], Number):
            return res.success(Number(range(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0].value} is not a valid argument for range()",
            "context": context,
            'exit': False
        }))

def BuiltInType_Int(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but int() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Number):
        return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        try:
            return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except ValueError:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for int()",
                "context": context,
                'exit': False
            }))
    if isinstance(args[0], Boolean):
        return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for int()",
        "context": context,
        'exit': False
    }))

def BuiltInType_Float(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but float() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Number):
        return res.success(Number(float(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        try:
            return res.success(Number(float(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except ValueError:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for float()",
                "context": context,
                'exit': False
            }))
    if isinstance(args[0], Boolean):
        return res.success(Number(float(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for float()",
        "context": context,
        'exit': False
    }))

def BuiltInType_Bool(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but bool() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Boolean):
        return res.success(args[0])
    if isinstance(args[0], Number):
        return res.success(Boolean(bool(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        try:
            return res.success(Boolean(bool(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except ValueError:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for bool()",
                "context": context,
                'exit': False
            }))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for bool()",
        "context": context,
        'exit': False
    }))

def BuiltInType_List(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but list() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], List):
        return res.success(args[0])
    if isinstance(args[0], Number):
        return res.success(List([args[0]]).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        return res.success(List([String(f"'{char}'") for char in args[0].value]).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], Boolean):
        return res.success(List([args[0]]).setPosition(node.pos_start, node.pos_end).setContext(context))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for list()",
        "context": context,
        'exit': False
    }))
    
    


def BuiltInTask_Format(args, node):
    string = args[0].value
    values_list = args[1].value
    regex = Regex().compile('{(.*?)}')
    matches = regex.match(string)
    
def BuiltInTask_Clear(args, node, context):
    res = RuntimeResult()
    if len(args) > 0:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but clear() takes no argument",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        return res.success(None)
    
def BuiltInTask_Delay(args, node, context):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but delay() takes 1 argument",
            "context": context,
            'exit': False
        }))

    if isinstance(args[0], Number):
        time.sleep(args[0].value)
        return res.success(None)
    else:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0].value} is not a valid argument for delay()",
            "context": context,
            'exit': False
        }))
    
def BuiltInTask_Exit(args, node, context):
    res = RuntimeResult()
    if len(args) == 0:
                    sys.exit()
    elif len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but exit() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Number):
        if args[0].value == 0:
            sys.exit(0)
        elif args[0].value == 1:
            sys.exit(1)
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid exit code",
                "context": context,
                'exit': False
            }))
    else:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0]} is not a valid argument for exit()",
            "context": context,
            'exit': False
        }))
    
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visiit)
        return method(node, context)

    def no_visiit(self, node, context):
        return RuntimeResult().success(NoneType.none)

    def visit_StatementsNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for element_node in node.elements:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements.append(element_value)
        return res.success(Statement(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(
            Number(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        return RuntimeResult().success(
            String(node.tok.value, node.arg).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )

    def visit_ObjectRefNode(self, node, context):
        return RuntimeResult().success(
            ObjectRefNode(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )

    
    def visit_StringInterpNode(self, node, context):
        res = RuntimeResult()
        values_to_replace = node.values_to_replace
        string_to_interp = res.register(self.visit(node.expr, context)).value
        value = ""
        if isinstance(values_to_replace, list):
            for value_to_replace in values_to_replace:
                    replace_value = context.symbolTable.get(value_to_replace)
                    if replace_value:
                        value_expr = res.register(self.visit(node.expr, context))
                        value_replaced = str(replace_value)
                        string_to_interp = string_to_interp.replace('{' + value_to_replace + '}', value_replaced)
                        value = String(string_to_interp).setContext(
                            context).setPosition(node.pos_start, node.pos_end)
                    else:
                        value_expr = str(NoneType.none)
                        value_replaced = str(NoneType.none)
                        string_to_interp = string_to_interp.replace('{' + value_to_replace + '}', value_replaced)
                        value = String(string_to_interp).setContext(
                            context).setPosition(node.pos_start, node.pos_end)
                        # return res.failure(Program.error()['Runtime']({
                        #     'pos_start': node.pos_start,
                        #     'pos_end': node.pos_end,
                        #     'message': f"format-variable is only allowed for variables or '{value_to_replace}' is not defined",
                        #     'context': context,
                        #     'exit': False
                        # }))
                        
        else:
            string = values_to_replace
            value = String(string).setContext(context).setPosition(node.pos_start, node.pos_end)
            
        if value:
            return res.success(value)
        else:
            res.noreturn()
    
    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for element_node in node.elements:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements.append(element_value)
        return res.success(List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_BooleanNode(self, node, context):
        return RuntimeResult().success(
            Number(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )
        
    def visit_PairNode(self, node, context):
        res = RuntimeResult()
        elements = ()
        for element_node in node.elements:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements = elements + (element_value,)
        return res.success(Pair(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name.value
        value = context.symbolTable.get(var_name)
        if var_name in context.symbolTable.symbols and value is None:
            value = context.symbolTable.get(NoneType.none)
        elif value is None:
            if var_name == "@":
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"Expected '@' to be followed by an identifier",
                    'context': context,
                    'exit': False
                }))
            Program.error()['Error']({
                'name': 'IdentifierError',
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f'{var_name} is not defined',
                'context': context,
                'exit': True
            })
            return res.noreturn()
        value = value.copy().setPosition(node.pos_start, node.pos_end).setContext(context)
        return res.success(value)
 
    def visit_PropertyNode(self, node, context):
        res = RuntimeResult()
        value = ""
        object_name = res.register(self.visit(node.name, context)) 
        object_key = node.property
        #TODO: check if object_name is not callable
        error = {
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            "message": "",
            "context": context,
            "exit": False
        }
        #print(type(object_name).__name__)
        
        if isinstance(object_name, Class):
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "methods"):
                    if object_key.id.value in object_name.methods:
                        value = object_name.methods[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{object_name.name} has no property {object_key.id.value}"
                        return res.failure(Program.error()["KeyError"](error))
            
            if type(object_key).__name__ == "Token":
                if hasattr(object_name, "methods"):
                    if object_key.value in object_name.methods:
                        value = object_name.methods[object_key.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{object_name.name} has no property {object_key.value}"
                        return res.failure(Program.error()["KeyError"](error))
            
            elif type(object_key).__name__ == "CallNode":
                if hasattr(object_name, "methods"):
                    if object_key.node_to_call.id.value in object_name.methods:
                        value = object_name.methods[object_key.node_to_call.id.value]
                        args_node = object_key.args_nodes
                        args = []
                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        return_value = res.register(value.run(args))
                        if res.should_return():
                                return res
                        if return_value == None or return_value == NoneType.none:
                            return res.success(None)
                        else:
                            return res.success(return_value)
                    else:
                        error["message"] = f"{object_name.name} has no method {object_key.node_to_call.id.value}"
                        return res.failure(Program.error()["KeyError"](error))
                    # else:
                    #     return res.failure(Program.error()["KeyError"](error))
        
        elif isinstance(object_name, Object):
            if type(object_key).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{object_name.name} has no property {object_key.value}"
                        return res.failure(Program.error()["KeyError"](error))
        
        elif isinstance(object_name, Task):
            # task dont have methods or properties
            
            if type(object_key).__name__ == "Token": 
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"{object_name.name} does not have any property {object_key.value}",
                    'context': context,
                    'exit': False
                }))
            else:
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"{object_name.name} does not have any property {object_key.id.value}",
                    'context': context,
                    'exit': False
                }))
          
        elif type(object_name).__name__ == "NoneType":
            
            if type(node.name).__name__ == "CallNode":
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"Undefined property {object_key.value}" if hasattr(object_key, "value") else f"Undefined property {object_key.id.value}",
                    'context': context,
                    'exit': False
                }))
            
        elif type(object_name).__name__ == "PropertyNode":
            print("PropertyNode", "fg")
            print(type(object_key))
        #   return res.failure(Program.error()['Runtime']({
        #         'pos_start': node.pos_start,
        #         'pos_end': node.pos_end,
        #         'message"
        #return res.success(None)
        else:
            print("else", "fg")
      
    def visit_PropertySetNode(self, node, context):
        res = RuntimeResult()
        object_name = res.register(self.visit(node.name, context))
        object_key = node.property
        value = res.register(self.visit(node.value, context))
        #print(object_name, object_key, value)  
    
         
    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.variable_name_token.value if type(node.variable_name_token).__name__ != 'tuple' else ''
        value = res.register(self.visit(node.value_node, context))
        if type(node.variable_name_token).__name__ == "tuple":
            var_name = node.variable_name_token
            if type(value).__name__ == "Pair":
                
                if len(var_name) != len(value.elements):
                    return res.failure(Program.error()['ValueError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"Expected {len(var_name)} values, unable to pair {len(value.elements)} value(s)",
                        'context': context,
                        'exit': False
                    }))
                else:
                    for i in range(len(var_name)):
                        context.symbolTable.set(var_name[i].name.value, value.elements[i])
                        
            elif type(value).__name__ == "List":
                if len(var_name) != len(value.elements):
                    return res.failure(Program.error()['ValueError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"Expected {len(var_name)} values, unable to pair {len(value.elements)} value(s)",
                        'context': context,
                        'exit': False
                    }))
                else:
                    for i in range(len(var_name)):
                        context.symbolTable.set(var_name[i].name.value, value.elements[i])
                        
            elif type(value).__name__ == "Object":
                if len(var_name) != len(value.properties):
                    return res.failure(Program.error()['ValueError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"Expected {len(var_name)} values, unable to pair {len(value.properties)} value(s)",
                        'context': context,
                        'exit': False
                    }))
                else:
                    for i in range(len(var_name)):
                        context.symbolTable.set(var_name[i].name.value, value.properties.get(var_name[i].name.value))
            else:
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"Cannot assign {type(value).__name__} to Pair",
                    'context': context,
                    'exit': False
                }))
        else:
            if res.should_return():
                return res
            if node.variable_keyword_token == "let":
                if value is None:
                    value = NoneType.none
                context.symbolTable.set(var_name, value)
            elif node.variable_keyword_token == "final":
                if value is None:
                    value = NoneType.none
                context.symbolTable.set_final(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RuntimeResult()
        try:
            left = res.register(self.visit(node.left_node, context))
            if res.should_return():
                return res
            right = res.register(self.visit(node.right_node, context))
            if node.op_tok.type == tokenList.TT_PLUS:
                result, error = left.added_to(right)
            elif node.op_tok.type == tokenList.TT_MINUS:
                result, error = left.subtracted_by(right)
            elif node.op_tok.type == tokenList.TT_MUL:
                result, error = left.multiplied_by(right)
            elif node.op_tok.type == tokenList.TT_DIVISION:
                result, error = left.divided_by(right)
            elif node.op_tok.type == tokenList.TT_POWER:
                result, error = left.powred_by(right)
            elif node.op_tok.type == tokenList.TT_MOD:
                result, error = left.modulo(right)
            elif node.op_tok.type == tokenList.TT_COLON:
                result, error = left.get_index(right)
            elif node.op_tok.type == tokenList.TT_GETTER:
                return self.visit_ObjectGetNode(node, context)
            elif node.op_tok.type == tokenList.TT_EQEQ:
                result, error = left.get_comparison_eq(right)
            elif node.op_tok.type == tokenList.TT_NEQ:
                result, error = left.get_comparison_ne(right)
            elif node.op_tok.type == tokenList.TT_LT:
                result, error = left.get_comparison_lt(right)
            elif node.op_tok.type == tokenList.TT_GT:
                result, error = left.get_comparison_gt(right)
            elif node.op_tok.type == tokenList.TT_LTE:
                result, error = left.get_comparison_lte(right)
            elif node.op_tok.type == tokenList.TT_GTE:
                result, error = left.get_comparison_gte(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'and'):
                result, error = left.and_by(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'or'):
                result, error = left.or_by(right)
            if error:
                return res.failure(error)
            else:
                return res.success(result.setPosition(node.pos_start, node.pos_end))
        except AttributeError or TypeError or ValueError:
            return RuntimeResult()

    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res
        error = None

        if node.op_tok.type == tokenList.TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(tokenList.TT_KEYWORD, 'not'):
            number, error = number.notted()
        if error:
            return res.failure(error)
        else:
            return res.success(number.setPosition(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RuntimeResult()
        for condition, expr, return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(NoneType.none if return_null else expr_value)
        if node.else_case:
            expr, return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(NoneType.none if return_null else else_value)

        return res.success(NoneType.none)

    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []
        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res
        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return():
            return res
        if node.step_value_node:
            step_value = res.register(
                self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)
        i = start_value.value

        if step_value.value >= 0:
            if not isinstance(start_value, Number) or not isinstance(end_value, Number) or not isinstance(step_value, Number):
                return res.failure(
                    Program.error()['Syntax']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': 'For loop not supported between ints and strings',
                        'exit': False
                    })
                )
            if type(end_value.value) == float:
                return res.failure(
                    Program.error()['Syntax']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': 'For loop not supported between ints and floats',
                        'exit': False
                    })
                )
                
            if type(end_value.value) == range:
                
                return res.failure(
                    Program.error()['Syntax']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': 'For loop not supported between ints and ranges',
                        'exit': False,
                    })
                )
                
                
            def condition(): return i < end_value.value
        else:
            def condition(): return i > end_value.value

        while condition():
            context.symbolTable.set(node.var_name_token.value, Number(i))
            i += step_value.value
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                return res

            if res.loop_continue:
                continue

            if res.loop_break:
                break

            elements.append(value)
        return res.success(NoneType.none if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()
        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res
            if not condition.is_true():
                break
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                return res

            if res.loop_continue:
                continue

            if res.loop_break:
                break

            elements.append(value)

        return res.success(NoneType.none if node.implicit_return else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_TaskDefNode(self, node, context):
        res = RuntimeResult()
        task_name = node.task_name_token.value if node.task_name_token else "none"
        body_node = node.body_node
        # methods = node.methods
        # #task_methods = []
        # for method in methods:
        #     #task_methods.append(res.register(self.visit(method, context)))
        #     if res.should_return(): return res
        #     method_name = method.task_name_token.value
        #     method_body = method.body_node
        #     method_args = [arg.value for arg in method.args_name_tokens]
        #     task_method = Task(method_name, method_body, method_args, False).setContext(context).setPosition(method.pos_start, method.pos_end)
        #     t = Context(context.symbolTable.set(method_name, task_method))
        #     print(t, "t")
            
        arg_names = [arg_name.value for arg_name in node.args_name_tokens]
        task_value = Task(task_name, body_node, arg_names, node.implicit_return).setContext(
            context).setPosition(node.pos_start, node.pos_end)
        if node.type != 'method':
            context.symbolTable.set(task_name, task_value)

        # if task_name in context.symbolTable.symbols:
        #     return res.failure(Program.error()["Runtime"]({
        #         "pos_start": node.pos_start,
        #         "pos_end": node.pos_end,
        #         "message": "Task with name '{}' already defined".format(task_name),
        #         "context": context
        #     }))
        # print(context.symbolTable.symbols)
        return res.success(task_value)

    def visit_ObjectDefNode(self, node, context):
        res = RuntimeResult()
        object_name = node.object_name.value
        object_value = ""
        properties = {}
        
        for property in node.properties:
            prop_name = property['name'].value
            prop_value = res.register(self.visit(property['value'], context))
            properties = dict(properties, **{str(prop_name): prop_value})
            if res.should_return():
                return res
            object_value = Object(object_name, properties).setContext(
                context).setPosition(node.pos_start, node.pos_end)
            if isinstance(prop_value, NoneType):
                object_value = Object(object_name, {'key': {}, 'value': {}}).setContext(
                    context).setPosition(node.pos_start, node.pos_end)
                already_defined = context.symbolTable.get(object_name)
                if already_defined:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        "message": "Object with name '{}' already defined".format(object_name),
                        "context": context,
                        "exit": False
                    }))
                context.symbolTable.set(object_name, object_value)
            else:
                context.symbolTable.set_object(object_name, object_value)
        return res.success(object_value)

    def visit_ObjectGetNode(self, node, context):
        res = RuntimeResult()
        object_name = res.register(self.visit(node.left_node, context))
        object_key = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res
        if not isinstance(object_name, Object):
            res.success(NoneType.none)
        if object_key == None:
            object_key = node.right_node
            if isinstance(object_name, Object):
                value = ""
                if type(object_key).__name__ == 'CallNode':
                    key = object_key.node_to_call.id.value
                    if key in object_name.properties:
                        value = object_name.properties[key]
                        if not isinstance(value, Task):
                            # if value is an object then the key is not callable
                            return res.failure(Program.error()["Runtime"]({
                                "pos_start": node.pos_start,
                                "pos_end": node.pos_end,
                                "message": "'{}' is not callable".format(key),
                                "context": context,
                                "exit": False
                            }))
                        else:
                            args_node = object_key.args_nodes
                            args = []
                            for arg in args_node:
                                args.append(res.register(self.visit(arg, context)))
                                if res.should_return():
                                    return res
                            return_value = res.register(value.run(args))
                            if res.should_return(): return res
                            if return_value == None or return_value == NoneType.none:
                                return res.success(None)
                            else:
                                return res.success(return_value)
                    else:
                        return res.failure(Program.error()["Runtime"]({
                            "pos_start": node.pos_start,
                            "pos_end": node.pos_end,
                            "message": "'{}' has no property '{}'".format(object_name.name, key),
                            "context": context,
                            "exit": False
                        }))
        if object_key == None:
            key = node.right_node
            if isinstance(object_name, Class):
                value = ""
                if key.node_to_call.id.value in object_name.methods:
                    value = object_name.methods[key.node_to_call.id.value]
                    args = key.args_nodes
                    return_value = res.register(key.node_to_call.id.value.execute(args))
                    #return_value = return_value.copy().setPosition(node.pos_start, node.pos_end).setContext(context)
                    return res.success(return_value)
            
        if isinstance(object_name, Object):
            value = ""
            error = {
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": "'{}' has no property '{}'".format(object_name.name, object_key),
                    "context": context,
                    "exit": False
                }
            if isinstance(object_key, String):
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return value
                    else:
                        return res.failure(Program.error()["KeyError"](error))
                else:
                    error['message'] = "{} has no property '{}'".format(object_name.name, object_key)
                    return res.failure(Program.error()["KeyError"](error))
            
            elif isinstance(object_key, Number):
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[str(object_key.value)]
                        return value
                    else:
                        return res.failure(Program.error()["KeyError"](error))
                else:
                    error['message'] = "{} has no property '{}'".format(object_name.name, object_key)
                    return res.failure(Program.error()["KeyError"](error))
            
            elif isinstance(object_key, ObjectRefNode):
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return value
                    else:
                        return res.failure(Program.error()["KeyError"](error))
                else:
                    error['message'] = "{} has no property '{}'".format(
                        object_name.name, object_key.value)
                    return res.failure(Program.error()["KeyError"](error))
            return res.success(value)
 
        
        elif isinstance(object_name, Class):
            
            value = ""
            error = {
                            "pos_start": node.pos_start,
                            "pos_end": node.pos_end,
                            "message": "'{}' has no method '{}'".format(object_name.name, object_key.value),
                            "context": context,
                            "exit": False
                        }
            if isinstance(object_key, String):
                if hasattr(object_name, "methods"):
                    if object_key.value in object_name.methods:
                        value = object_name.methods[object_key.value]
                        return value
                    else:
                        return res.failure(Program.error()["KeyError"](error))
                else:
                    error['message'] = "{} has no method '{}'".format(object_name.name, object_key.value)
                    return res.failure(Program.error()["KeyError"](error))
            elif isinstance(object_key, Number):
                if hasattr(object_name, "methods"):
                    if object_key.value in object_name.methods:
                        value = object_name.methods[str(object_key.value)]
                        return value
                    else:
                        return res.failure(Program.error()["KeyError"](error))
                else:
                    error['message'] = "{} has no method '{}'".format(object_name.name, object_key.value)
                    return res.failure(Program.error()["KeyError"](error))
            elif isinstance(object_key, ObjectRefNode):
                if hasattr(object_name, "methods"):
                    if object_key.value in object_name.methods:
                        value = object_name.methods[object_key.value]
                        return value
                    else:
                        return res.failure(Program.error()["KeyError"](error))
                else:
                    error['message'] = "{} has no method '{}'".format(object_name.name, object_key.value)
                    return res.failure(Program.error()["KeyError"](error))
                
            elif isinstance(object_key, NoneType):
                return res.success(NoneType.none)
            return res.success(value)


        elif isinstance(object_name, Task):
            value = ""
            error = {
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": "'{}' has no method '{}'".format(object_name.id, object_key.id),
                    "context": context,
                    "exit": False
                }
            return res.failure(Program.error()["KeyError"](error))
        
    
        
        else:
            return res.success(NoneType.none)
           
    
                        
    
    def visit_ClassNode(self, node, context):
        res = RuntimeResult()
        class_name = node.class_name.value
        constructor_args = node.class_constuctor_args
        inherits_class_name = node.inherits_class_name
        inherits_class = node.inherits_class
        class_value = ""
        methods = {}
        if node.methods != '':
            for method in node.methods:
                method_name = method['name'].value
                method_value = res.register(self.visit(method['value'], context))
                if res.should_return():
                    return res
                methods = dict(methods, **{str(method_name): method_value})
                class_value = Class(class_name,constructor_args, inherits_class_name, inherits_class, methods).setContext(context).setPosition(node.pos_start, node.pos_end)
                context.symbolTable.set_object(class_name, class_value)
        else:
            context.symbolTable.set_object(class_name, class_value)
        return res.success(class_value)

    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        try:
            args = []
            value_to_call = res.register(self.visit(
                node.node_to_call, context)) if node.node_to_call else None
            
            if res.should_return():
                return res
            value_to_call = value_to_call.copy().setPosition(node.pos_start, node.pos_end)
            for arg_node in node.args_nodes:
                args.append(res.register(self.visit(arg_node, context)))
                if res.should_return():
                    return res
                
            if len(args) > 0:
                for arg in args:
                    if arg == None:
                        # remove None from args
                        args.remove(arg)
            builtin = value_to_call.name
            
            builtins = {
                'print': BuiltInTask_Print,
                'println': BuiltInTask_PrintLn,
                'input': BuiltInTask_Input,
                'inputInt': BuiltInTask_InputInt,
                'inputFloat': BuiltInTask_InputFloat,
                'format': BuiltInTask_Format,
                'str': BuiltInType_Str,
                'range': BuiltInType_Range,
                'int': BuiltInType_Int,
                'float': BuiltInType_Float,
                'bool': BuiltInType_Bool,
                'list': BuiltInType_List,
                # 'pair' : BuiltInType_Pair,
                # 'object': BuiltInType_Object,
                'clear': BuiltInTask_Clear,
                'delay': BuiltInTask_Delay,
                'exit': BuiltInTask_Exit
            }
            
            if builtin in builtins:
                if builtin == 'print' or builtin == 'println':
                    return builtins[builtin](args,node)
                return builtins[builtin](args, node, context)
            
            return_value = res.register(value_to_call.execute(args))
            
            if res.should_return():
                return res
            return_value = return_value.copy().setPosition(
                node.pos_start, node.pos_end).setContext(context)
            if isinstance(return_value, NoneType):
                return res.noreturn()
            return res.success(return_value)
        except AttributeError or TypeError or ValueError:
            return RuntimeResult()

    def visit_ReturnNode(self, node, context):
        res = RuntimeResult()
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if value is None: value = NoneType.none
            if res.should_return(): return res
        else:
            value = NoneType.none
        if value is None:  value = NoneType.none
        if isinstance(value, NoneType):
            return res.noreturn()
        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RuntimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RuntimeResult().success_break()
