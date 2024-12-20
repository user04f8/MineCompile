#!/usr/bin/env python3.8
# @generated by pegen from data/expr.gram

import ast
import sys
import tokenize

from typing import Any, Optional

from pegen.parser import memoize, memoize_left_rec, logger, Parser

import itertools

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
    def file(self) -> Optional[ast . Module]:
        # file: statements? $
        mark = self._mark()
        if (
            (a := self.statements(),)
            and
            (self.expect('ENDMARKER'))
        ):
            return ast . Module ( body = a or [] , type_ignores = [] );
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
        # simple_stmt: expr
        mark = self._mark()
        if (
            (expr := self.expr())
        ):
            return ast . Expression ( expr , lineno = 1 , col_offset = 0 );
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
            return ast . BinOp ( expr , ast . Add ( ) , term );
        self._reset(mark)
        if (
            (expr := self.expr())
            and
            (self.expect('-'))
            and
            (term := self.term())
        ):
            return ast . BinOp ( expr , ast . Sub ( ) , term );
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
            return ast . BinOp ( l , ast . Mult ( ) , r );
        self._reset(mark)
        if (
            (term := self.term())
            and
            (self.expect('/'))
            and
            (factor := self.factor())
        ):
            return ast . BinOp ( term , ast . Div ( ) , factor );
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
        # atom: NAME | NUMBER | '`' NAME '`'
        mark = self._mark()
        if (
            (name := self.name())
        ):
            return ast . Name ( id = name . string , ctx = ast . Load ( ) );
        self._reset(mark)
        if (
            (number := self.number())
        ):
            return ast . Constant ( value = ast . literal_eval ( number . string ) );
        self._reset(mark)
        if (
            (self.expect('`'))
            and
            (name := self.name())
            and
            (self.expect('`'))
        ):
            return ast . Constant ( value = name . string );
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

    KEYWORDS = ()
    SOFT_KEYWORDS = ()


if __name__ == '__main__':
    from pegen.parser import simple_parser_main
    simple_parser_main(GeneratedParser)
