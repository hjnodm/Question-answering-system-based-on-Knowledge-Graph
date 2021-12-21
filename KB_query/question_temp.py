# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: question_temp.py

@time: 2017/12/20 15:30

@desc:
设置问题模板，为每个模板设置对应的SPARQL语句。demo提供如下模板：

1. 某演员演了什么电影
2. 某电影有哪些演员出演
3. 演员A和演员B合作出演了哪些电影
4. 某演员参演的评分大于X的电影有哪些
5. 某演员出演过哪些类型的电影
6. 某演员出演的XX类型电影有哪些。
7. 某演员出演了多少部电影。
8. 某演员是喜剧演员吗。
9. 某演员的生日/出生地/英文名/简介
10. 某电影的简介/上映日期/评分

读者可以自己定义其他的匹配规则。
"""
from refo import finditer, Predicate, Star, Any, Disjunction
import re

# TODO SPARQL前缀和模板
SPARQL_PREXIX = u"""
PREFIX : <http://www.kgdemo.com#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""
SPARQL_ROOM_PREXIX =u"""
PREFIX : <http://www.kgdemo.com#>
PREFIX : <http://www.semanticweb.org/11707/ontologies/2021/9/untitled-ontology-2#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

SPARQL_SELECT_TEMP =u"{prefix}\n" + \
             u"SELECT DISTINCT {select} WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_SELECT_TEM = u"{prefix}\n" + \
             u"SELECT DISTINCT {select} WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_COUNT_TEM = u"{prefix}\n" + \
             u"SELECT COUNT({select}) WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_ASK_TEM = u"{prefix}\n" + \
             u"ASK {{\n" + \
             u"{expression}\n" + \
             u"}}\n"


class W(Predicate):
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token)
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition_num, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action
        self.condition_num = condition_num

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])

        return self.action(matches), self.condition_num


class KeywordRule(object):
    def __init__(self, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])
        if len(matches) == 0:
            return None
        else:
            return self.action()


class QuestionSet:
    def __init__(self):
        pass


    @staticmethod
    def person_hometown_question(word_objects):
        """
        某人的家乡是
        :param word_objects:
        :return:
        """
        select = u"?x"
        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u":{college} :家乡 ?place.\n"\
                    u"?place :名称 ?x".format(college=w.token)

                sparql = SPARQL_SELECT_TEMP.format(prefix=SPARQL_ROOM_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        print(sparql)
        return sparql

    @staticmethod
    def hometown_person_question(word_objects):
        """
        来自某地的寝室人员有谁/家乡为某地的寝室人员
        :param word_objects:
        :return:
        """
        select = u"?x"
        sparql = None
        for w in word_objects:
            if w.pos == pos_place:
                e = u"?person :家乡 :{place}."\
                    u"?person :名称 ?x".format(place=w.token)

                sparql = SPARQL_SELECT_TEMP.format(prefix=SPARQL_ROOM_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        print(sparql)
        return sparql

    @staticmethod
    def roommate_info(word_objects):
        """
        某室友的昵称/身高/爱好/擅长的游戏/室友为：
        :param word_objects:
        :return:
        """

        select = u"?x"
        e = None
        person = None
        keyword = None
        sparql = None
        for r in base_info_rule:
            e = r.apply(word_objects)
            if e is not None:
                print(e)
                break


        for w in word_objects:
            if w.pos == pos_person:
                person = w.token
            if w.pos == "n":
                keyword = w.token

        if person is not None and keyword is not None and e is not None:
            if "keyword" in e:
                e = e.format(person=person, keyword=keyword)
            else:
                e = e.format(person=person)



            sparql = SPARQL_SELECT_TEMP.format(prefix=SPARQL_ROOM_PREXIX,
                                               select=select,
                                               expression=e)

        print(sparql)
        return sparql

    @staticmethod
    def CCF_grade(word_objects):
        """
        寝室人员CCF成绩大于X的人
        :param word_objects:
        :return:
        """
        select = u"?x"

        com_item = None
        number = None
        keyword = None
        sparql = None

        for r in compare_keyword_rules:
            keyword = r.apply(word_objects)
            if keyword is not None:
                break

        for w in word_objects:
            if w.pos == pos_number:
                number = w.token
            if w.pos == "n":
                com_item = w.token

        if com_item is not None and number is not None and keyword is not None:
            e = u"?who :名称 ?x." \
                u"?who :{com_item} ?v." \
                u"filter(?v {mark} {number})".format(com_item=com_item, number=number,
                                                     mark=keyword)

            sparql = SPARQL_SELECT_TEMP.format(prefix=SPARQL_ROOM_PREXIX,
                                               select=select,
                                               expression=e)

        return  sparql


    @staticmethod
    def A_and_B_same_hobby(word_objects):
        """
        室友A和B爱好相同吗
        :param word_objects:
        :return:
        """
        person1 = None
        person2 = None
        keyword = None
        e = None

        for w in word_objects:
            if w.pos == pos_person:
                if person1 is None:
                    person1 = w.token
                else:
                    person2 = w.token
            if w.pos == "n":
                keyword = w.token

        for r in ask_keyword_rules:
            e = r.apply(word_objects)
            if e is not None:
                break



        if e is not None:
            e = e.format(person1=person1, person2=person2, keyword=keyword)

            return SPARQL_ASK_TEM.format(prefix=SPARQL_ROOM_PREXIX,
                                          expression=e)
        else:
            return None

    @staticmethod
    def count_roomate(word_objects):
        """
        某人的室友/爱好有几个人
        :param word_objects:
        :return:
        """

        select = u"?x"
        sparql = None
        person = None
        keyword = None

        for r in count_keyword_rules:
            keyword = r.apply(word_objects)
            if keyword is not None:
                break

        for w in word_objects:
            if w.pos == pos_person:
                person = w.token

        if person is not None and keyword is not None:
            e = u":{person} :{keyword} ?x.".format(person=person,keyword=keyword)
            sparql = SPARQL_COUNT_TEM.format(prefix=SPARQL_ROOM_PREXIX, select=select, expression=e)

        return sparql


class PropertyValueSet:
    def __init__(self):
        pass

    @staticmethod
    def return_higher_value():
        return u'>'

    @staticmethod
    def return_lower_value():
        return u'<'

    @staticmethod
    def return_higher_and_equal_value():
        return u'>='

    @staticmethod
    def return_lower_and_equal_value():
        return u'<='

    @staticmethod
    def return_info_select():
        return u":{person} :{keyword} ?x."

    @staticmethod
    def retrun_hobby_select():
        return u":{person} :拥有 ?ho." \
                u"?ho ?p :{keyword}." \
                u"?ho :名称 ?x"

    @staticmethod
    def return_relation_select():
        return u":{person} :互为室友 ?who.\n" \
                u"?who :名称 ?x."

    @staticmethod
    def return_count_roommate():
        return '互为室友'

    @staticmethod
    def return_count_hobby():
        return '拥有'

    @staticmethod
    def return_ask_info():
        return u":{person1} :{keyword} ?x.\n" \
                u":{person2} :{keyword} ?x"

    @staticmethod
    def return_ask_hobby():
        return u":{person1} :拥有 ?s.\n" \
                u"?s ?p :{keyword}.\n" \
                u"?s :名称 ?x.\n" \
                u":{person2} :拥有 ?ss.\n" \
                u"?ss ?p :{keyword}.\n" \
                u"?ss :名称 ?x\n"

    @staticmethod
    def return_ask_hometown():
        return u":{person1} :{keyword} ?s.\n" \
                u"?s :名称 ?x.\n" \
                u":{person2} :{keyword} ?ss.\n" \
                u"?ss :名称 ?x\n"



# TODO 定义关键词
pos_person = "nr"
pos_properNum = "nz"
pos_place = "ns"
pos_number = "m"
pos_comma = "x"

person_entity = W(pos=pos_person)
game_entity = (W(pos=pos_properNum))
province_entity = W(pos=pos_place)
comma_entity = W(pos=pos_comma)
number_entity = (W(pos=pos_number))


male_college = (W("寝室人员") | W("室友") | W("男大学生"))

place = (W("家乡") | W("省份"))
positive = (W('是') | W('为'))
come_from = W('来自')

info_property = (W("身高") | W("CCF成绩") | W("昵称"))
hobby = (W("爱好") | W("喜好"))
gamer = W("擅长的游戏")
roommate_relation = W("室友")
base_info = ( info_property | hobby | gamer | roommate_relation )

conjunction = (W("和") | W("与") | W(',') | W('，'))
both = (W("两人") | W("两者") )

higher = (W("大于") | W("高于"))
lower = (W("小于") | W("低于"))
higher_and_equal = (W('大于等于') | W('高于等于'))
lower_and_equal = (W('小于等于') | W('低于等于'))
compare = (higher | lower | higher_and_equal|lower_and_equal )

same = (W('相同') | W('一样'))
several = (W("多少") | W("几人") | W('几个'))

when = (W("何时") | W("时候"))
where = (W("哪里") | W("哪儿") | W("何地") | W("何处") | W("在") + W("哪") | W('某地'))

# TODO 问题模板/匹配规则
"""
1.某人的家乡是
2.来自某地的寝室人员有谁/家乡为某地的寝室人员
3.某室友的昵称/身高/爱好/擅长的游戏/室友为
4.寝室人员CCF成绩大于Ｘ的人
5.室友Ａ和室友Ｂ爱好/CCF成绩/擅长的游戏相同吗
6.某人的室友/爱好有几个
"""
rules = [
    Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + place + Star(Any(), greedy=False), action=QuestionSet.person_hometown_question),
    Rule(condition_num=2, condition=((place + positive + province_entity + Star(Any(), greedy=False) + male_college + Star(Any(), greedy=False)) | (come_from + province_entity + Star(Any(), greedy=False) + male_college + Star(Any(), greedy=False))) , action=QuestionSet.hometown_person_question),
    Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + base_info + Star(Any(), greedy=False), action=QuestionSet.roommate_info),
    Rule(condition_num=3, condition=person_entity + base_info + compare + number_entity + Star(Any(), greedy=False), action=QuestionSet.CCF_grade),
    Rule(condition_num=4, condition=person_entity + Star(Any(), greedy=False) + base_info + comma_entity + person_entity + Star(Any(), greedy=False) + base_info + same + Star(Any(), greedy=False), action=QuestionSet.A_and_B_same_hobby),
    Rule(condition_num=4, condition=person_entity + Star(Any(), greedy=False) + (hobby | roommate_relation) + Star(Any(), greedy=False) + several + Star(Any(), greedy=False), action=QuestionSet.count_roomate),
]

compare_keyword_rules = [
    KeywordRule(condition=person_entity + base_info + higher + number_entity + Star(Any(), greedy=False), action=PropertyValueSet.return_higher_value),
    KeywordRule(condition=person_entity + base_info + lower + number_entity + Star(Any(), greedy=False), action=PropertyValueSet.return_lower_value),
    KeywordRule(condition=person_entity + base_info + higher_and_equal + number_entity + Star(Any(), greedy=False), action=PropertyValueSet.return_higher_value),
    KeywordRule(condition=person_entity + base_info + lower_and_equal + number_entity + Star(Any(), greedy=False), action=PropertyValueSet.return_lower_value)
]

base_info_rule = [
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + info_property + Star(Any(), greedy=False), action=PropertyValueSet.return_info_select),
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + (gamer | hobby) + Star(Any(), greedy=False), action=PropertyValueSet.retrun_hobby_select),
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + roommate_relation + Star(Any(), greedy=False), action=PropertyValueSet.return_relation_select),
]

count_keyword_rules =[
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + roommate_relation + Star(Any(), greedy=False) + several + Star(Any(), greedy=False), action=PropertyValueSet.return_count_roommate),
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + hobby + Star(Any(), greedy=False) + several + Star(Any(), greedy=False), action=PropertyValueSet.return_count_hobby),
]
ask_keyword_rules = [
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + info_property + comma_entity + person_entity + Star(Any(), greedy=False) + info_property + same + Star(Any(), greedy=False),action=PropertyValueSet.return_ask_info),
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + (gamer | hobby) + comma_entity + person_entity + Star(Any(), greedy=False) + (gamer | hobby) + same + Star(Any(), greedy=False),action=PropertyValueSet.return_ask_hobby),
    KeywordRule(condition=person_entity + Star(Any(), greedy=False) + info_property + comma_entity + person_entity + Star(Any(), greedy=False) + info_property + same + Star(Any(), greedy=False),action=PropertyValueSet.return_ask_hometown),
]
