#!/usr/bin/env python3.8
# @generated by pegen from mcpy.gram

import ast
import sys
import tokenize

from typing import Any, Optional

from pegen.parser import memoize, memoize_left_rec, logger, Parser

import itertools

import malast
from malast_types import Code

# Keywords and soft keywords are listed at the end of the parser definition.
class GeneratedParser(Parser):

    @memoize
    def start(self) -> Optional[Any]:
        # start: file
        mark = self._mark()
        if (
            (file := self.file())
        ):
            return file;
        self._reset(mark)
        return None;

    @memoize
    def file(self) -> Optional[malast . Module]:
        # file: statements? $
        mark = self._mark()
        if (
            (a := self.statements(),)
            and
            (self.expect('ENDMARKER'))
        ):
            return malast . Module ( body = a or [] );
        self._reset(mark)
        return None;

    @memoize
    def statements(self) -> Optional[list]:
        # statements: statement+
        mark = self._mark()
        if (
            (a := self._loop1_1())
        ):
            return list ( itertools . chain . from_iterable ( a ) );
        self._reset(mark)
        return None;

    @memoize
    def statement(self) -> Optional[list]:
        # statement: simple_stmts
        mark = self._mark()
        if (
            (a := self.simple_stmts())
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def simple_stmts(self) -> Optional[list]:
        # simple_stmts: simple_stmt !';' NEWLINE | ';'.simple_stmt+ ';'? NEWLINE
        mark = self._mark()
        if (
            (a := self.simple_stmt())
            and
            (self.negative_lookahead(self.expect, ';'))
            and
            (self.expect('NEWLINE'))
        ):
            return [a];
        self._reset(mark)
        if (
            (a := self._gather_2())
            and
            (self.expect(';'),)
            and
            (self.expect('NEWLINE'))
        ):
            return a;
        self._reset(mark)
        return None;

    @memoize
    def simple_stmt(self) -> Optional[Any]:
        # simple_stmt: expression | 'nop' | &'assert' assert_stmt
        mark = self._mark()
        if (
            (expression := self.expression())
        ):
            return malast . Expression ( expression , lineno = 1 , col_offset = 0 );
        self._reset(mark)
        if (
            (literal := self.expect('nop'))
        ):
            return literal;
        self._reset(mark)
        if (
            (self.positive_lookahead(self.expect, 'assert'))
            and
            (assert_stmt := self.assert_stmt())
        ):
            return assert_stmt;
        self._reset(mark)
        return None;

    @memoize
    def assert_stmt(self) -> Optional[ast . Assert]:
        # assert_stmt: 'assert' expression [',' expression]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('assert'))
            and
            (a := self.expression())
            and
            (b := self._tmp_4(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Assert ( test = a , msg = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def expression(self) -> Optional[Any]:
        # expression: expr
        mark = self._mark()
        if (
            (expr := self.expr())
        ):
            return expr;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def expr(self) -> Optional[Any]:
        # expr: expr '+' term | expr '-' term | term
        mark = self._mark()
        if (
            (expr := self.expr())
            and
            (self.expect('+'))
            and
            (term := self.term())
        ):
            return malast . BinOp ( expr , malast . Add ( ) , term );
        self._reset(mark)
        if (
            (expr := self.expr())
            and
            (self.expect('-'))
            and
            (term := self.term())
        ):
            return malast . BinOp ( expr , malast . Sub ( ) , term );
        self._reset(mark)
        if (
            (term := self.term())
        ):
            return term;
        self._reset(mark)
        return None;

    @memoize_left_rec
    def term(self) -> Optional[Any]:
        # term: term '*' factor | term '/' factor | factor
        mark = self._mark()
        if (
            (l := self.term())
            and
            (self.expect('*'))
            and
            (r := self.factor())
        ):
            return malast . BinOp ( l , malast . Mult ( ) , r );
        self._reset(mark)
        if (
            (term := self.term())
            and
            (self.expect('/'))
            and
            (factor := self.factor())
        ):
            return malast . BinOp ( term , malast . Div ( ) , factor );
        self._reset(mark)
        if (
            (factor := self.factor())
        ):
            return factor;
        self._reset(mark)
        return None;

    @memoize
    def factor(self) -> Optional[Any]:
        # factor: '(' expr ')' | atom
        mark = self._mark()
        if (
            (self.expect('('))
            and
            (expr := self.expr())
            and
            (self.expect(')'))
        ):
            return expr;
        self._reset(mark)
        if (
            (atom := self.atom())
        ):
            return atom;
        self._reset(mark)
        return None;

    @memoize
    def atom(self) -> Optional[Any]:
        # atom: NAME | 'True' | 'False' | 'None' | STRING | NUMBER | '...' | '`' STRING '`'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Name ( id = a . string , ctx = malast . Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.string())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = malast . literal_eval ( a . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = malast . literal_eval ( a . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('...'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = Ellipsis , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (self.expect('`'))
            and
            (self.string())
            and
            (self.expect('`'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = Code ( malast . literal_eval ( a . string ) ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def fstring_mid(self) -> Optional[Any]:
        # fstring_mid: fstring_replacement_field | FSTRING_MIDDLE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (fstring_replacement_field := self.fstring_replacement_field())
        ):
            return fstring_replacement_field;
        self._reset(mark)
        if (
            (t := self.fstring_middle())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = t . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def fstring_replacement_field(self) -> Optional[Any]:
        # fstring_replacement_field: '{' (expr) "="? fstring_conversion? fstring_full_format_spec? '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect('{'))
            and
            (a := self.expr())
            and
            (debug_expr := self.expect("="),)
            and
            (conversion := self.fstring_conversion(),)
            and
            (format := self.fstring_full_format_spec(),)
            and
            (self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . FormattedValue ( value = a , conversion = ( conversion . decode ( ) [0] if conversion else ( b'r' [0] if debug_expr else - 1 ) ) , format_spec = format , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def fstring_conversion(self) -> Optional[int]:
        # fstring_conversion: "!" NAME
        mark = self._mark()
        if (
            (conv_token := self.expect("!"))
            and
            (conv := self.name())
        ):
            return self . check_fstring_conversion ( conv_token , conv );
        self._reset(mark)
        return None;

    @memoize
    def fstring_full_format_spec(self) -> Optional[Any]:
        # fstring_full_format_spec: ':' fstring_format_spec*
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.expect(':'))
            and
            (spec := self._loop0_5(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . JoinedStr ( values = spec if spec and ( len ( spec ) > 1 or spec [0] . value ) else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , );
        self._reset(mark)
        return None;

    @memoize
    def fstring_format_spec(self) -> Optional[Any]:
        # fstring_format_spec: FSTRING_MIDDLE | fstring_replacement_field
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (t := self.fstring_middle())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return malast . Constant ( value = t . string , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        if (
            (fstring_replacement_field := self.fstring_replacement_field())
        ):
            return fstring_replacement_field;
        self._reset(mark)
        return None;

    @memoize
    def fstring(self) -> Optional[Any]:
        # fstring: FSTRING_START fstring_mid* FSTRING_END
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (self.fstring_start())
            and
            (b := self._loop0_6(),)
            and
            (self.fstring_end())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . JoinedStr ( values = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset );
        self._reset(mark)
        return None;

    @memoize
    def strings(self) -> Optional[Any]:
        # strings: fstring | STRING
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (fstring := self.fstring())
        ):
            return fstring;
        self._reset(mark)
        if (
            (string := self.string())
        ):
            return string;
        self._reset(mark)
        return None;

    @memoize
    def _loop1_1(self) -> Optional[Any]:
        # _loop1_1: statement
        mark = self._mark()
        children = []
        while (
            (statement := self.statement())
        ):
            children.append(statement)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_3(self) -> Optional[Any]:
        # _loop0_3: ';' simple_stmt
        mark = self._mark()
        children = []
        while (
            (self.expect(';'))
            and
            (elem := self.simple_stmt())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _gather_2(self) -> Optional[Any]:
        # _gather_2: simple_stmt _loop0_3
        mark = self._mark()
        if (
            (elem := self.simple_stmt())
            is not None
            and
            (seq := self._loop0_3())
            is not None
        ):
            return [elem] + seq;
        self._reset(mark)
        return None;

    @memoize
    def _tmp_4(self) -> Optional[Any]:
        # _tmp_4: ',' expression
        mark = self._mark()
        if (
            (self.expect(','))
            and
            (z := self.expression())
        ):
            return z;
        self._reset(mark)
        return None;

    @memoize
    def _loop0_5(self) -> Optional[Any]:
        # _loop0_5: fstring_format_spec
        mark = self._mark()
        children = []
        while (
            (fstring_format_spec := self.fstring_format_spec())
        ):
            children.append(fstring_format_spec)
            mark = self._mark()
        self._reset(mark)
        return children;

    @memoize
    def _loop0_6(self) -> Optional[Any]:
        # _loop0_6: fstring_mid
        mark = self._mark()
        children = []
        while (
            (fstring_mid := self.fstring_mid())
        ):
            children.append(fstring_mid)
            mark = self._mark()
        self._reset(mark)
        return children;

    KEYWORDS = ('False', 'None', 'True', 'assert', 'nop')
    SOFT_KEYWORDS = ()


if __name__ == '__main__':
    from pegen.parser import simple_parser_main
    simple_parser_main(GeneratedParser)
