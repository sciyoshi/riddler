"""
A horological pyromaniacal puzzle.
"""

import attr
import copy
import click
import itertools
from fractions import Fraction
from collections import Counter

def splits(l):
	"""
	Returns an iterator over all subsets of a multiset represented as a `Counter`.
	"""
	for s in itertools.product(*([(k, c) for c in range(v + 1)] for k, v in l.items())):
		yield Counter(dict(s))

sups = dict(zip('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
subs = dict(zip('0123456789', '₀₁₂₃₄₅₆₇₈₉'))

def improper(f):
	"""
	Formats a `Fraction` as an improper fraction.
	"""
	base = int(f)
	frac = f - base

	num = ''.join(sups.get(c, c) for c in str(frac.numerator))
	den = ''.join(subs.get(c, c) for c in str(frac.denominator))

	return str(base or '') + (f'{num}\u2044{den}' if frac else '')

@attr.s
class State:
	"""
	Represents a possible current system state.
	"""
	full = attr.ib()
	half = attr.ib()
	left = attr.ib()
	time = attr.ib()

	def __bool__(self):
		return bool(self.full) or bool(self.half) or bool(self.left)

	def burn(self, t):
		self.full = Counter({k - t * 2: c for k, c in self.full.items() if k > t * 2})
		self.half = Counter({k - t: c for k, c in self.half.items() if k > t})
		self.time += t
		return self

	def burns(self):
		for t in self.full:
			yield copy.copy(self).burn(t / 2)
		for t in self.half:
			yield copy.copy(self).burn(t)

	def next(self):
		for c1 in splits(self.left):
			for c2 in splits(self.left - c1):
				for c3 in splits(self.half):
					s = State(
						full=self.full + c1 + c3,
						half=self.half + c2 - c3,
						left=self.left - c1 - c2,
						time=self.time
					)

					yield from s.burns()

	def expand(self):
		for item in self.next():
			if not item:
				yield item.time
			else:
				yield from item.expand()

def possible_times(ropes):
	initial = State(full=Counter(), half=Counter(), left=Counter({Fraction(60, 1): ropes}), time=0)

	return list(sorted(set(initial.expand())))

@click.command()
@click.argument('count', type=int, default=0)
def ropes(count):
	if not count:
		for count in range(2, 8):
			print(f'{count} ropes: {len(possible_times(count))}')
	else:
		result = possible_times(count)

		print(f'{count} ropes: {len(result)} times')
		print(', '.join(improper(time) for time in result))

if __name__ == '__main__':
	ropes()
