# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import string
import numbers
import functools

try:
    from deep_neural_network.face_classifier import detect_and_predict_face_emotion
except ImportError:
    detect_and_predict_face_emotion = None

try:
    basestring
except NameError:
    basestring = (str, bytes)


TRUE_STRINGS = {
    'true', 'yes', 'on', 'yeah', 'yup', 'yarp',
    'oui',  # French
    'ja',   # German, Danish, Dutch, Afrikaans, Swedish, Norwegian
    'sim',  # Portuguese
    'sea',  # Irish
    'jes',  # Esperanto
    u'نعم'.lower(), # Arabic
}
FALSE_STRINGS = {
    'false', 'no', 'off', 'nope', 'nah', 'narp',
    'non',   # French
    'nein',  # German
    'nej',   # Danish
    'nee',   # Dutch
    u'ﻷ',    # Arabic
}
STRIP_CHARS = string.whitespace + string.punctuation

HAPPY_STRINGS = {
    'happy',
    'happy-face',
    'joyful',
}
ANGRY_STRINGS = {
    'angry',
    'anger',
    'grrr',
}
SAD_STRINGS = {
    'sad',
    'depressed',
    'emo',
}
SURPRISE_STRINGS = {
    'surprise',
    'shock',
    'omg',
    'omfg',
    'amazeballs',
}
NEUTRAL_STRINGS = {
    'neutral',
}


class UnIshable(Exception):
    def __init__(self, value):
        super(UnIshable, self).__init__('{!r} can not be ished!'.format(value))


class Maybe(ValueError):
    def __init__(self, value):
        super(Maybe, self).__init__('Maybe! ({!r} is not recognised)'.format(value))


def normalize_string(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8', 'replace')
    return s.strip(STRIP_CHARS).lower()


class BaseIsh(object):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return '{!r}-{!r}'.format(self._value, ish)


class BoolIsh(BaseIsh):
    def _check_string(self, s):
        normalized = normalize_string(s)

        try:
            return bool(int(normalized))
        except ValueError:
            pass

        if normalized in TRUE_STRINGS:
            return True
        if normalized in FALSE_STRINGS:
            return False

        raise Maybe(s)

    def __eq__(self, other):
        result = bool(other)

        if result and isinstance(other, basestring):
            result = self._check_string(other)

        return result == self._value


@functools.total_ordering
class NumberIsh(BaseIsh):
    def __init__(self, value, precision=0.20001):
        super(NumberIsh, self).__init__(value)

        self._min = value - precision
        self._max = value + precision

    def _to_number(self, obj):
        if isinstance(obj, numbers.Real):
            return obj
        try:
            return float(obj)
        except (TypeError, ValueError):
            try:
                return int(obj)
            except (TypeError, ValueError):
                raise Maybe(obj)

    def __eq__(self, other):
        return self._min <= self._to_number(other) <= self._max

    def __lt__(self, other):
        return self._min < self._to_number(other)


class EmotionIsh(BaseIsh):
    def __init__(self, value):
        if detect_and_predict_face_emotion:
            super(EmotionIsh, self).__init__(value)
            normalized = normalize_string(value)
            for (type, keywords) in ((0, ANGRY_STRINGS),
                                     (3, HAPPY_STRINGS),
                                     (4, SAD_STRINGS),
                                     (5, SURPRISE_STRINGS),
                                     (6, NEUTRAL_STRINGS)):
                if normalized in keywords:
                    self._type = type
                    return

        raise UnIshable(value)

    def _is_image(self, img):
        try:
            shape = img.shape
            if len(shape) == 3 and shape[2] == 3:
                return True
            if len(shape) == 2:
                return True
        except Exception:
            return False

    def __eq__(self, other):
        if self._is_image(other):
            return detect_and_predict_face_emotion(other) == self._type
        raise Maybe(other)


class Ish(object):
    _module = sys.modules[__name__]

    UnIshable = UnIshable
    Maybe = Maybe

    def __rsub__(self, other):
        if other is True:
            return BoolIsh(True)
        if other is False:
            return BoolIsh(False)
        if isinstance(other, numbers.Real):
            return NumberIsh(other)
        if isinstance(other, basestring):
            return EmotionIsh(other)
        raise UnIshable(other)

    def __repr__(self):
        return 'ish'


ish = ish.ish = sys.modules[__name__] = Ish()


if __name__ == '__main__':
    print('Yup' == True-ish)
    print('Nope' == True-ish)
    print('False' == False-ish)
    print('Yeah' == False-ish)
    print('Whatever' == True-ish)
