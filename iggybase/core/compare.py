import re, logging


class Compare:
    @staticmethod
    def evaluate_value(comparison_string, value):
        if comparison_string.startswith('<='):
            temp = re.match(r'^(<=)(.*)', comparison_string)
            try:
                return float(value) <= float(temp.group(2))
            except:
                return False
        elif comparison_string.startswith('>='):
            temp = re.match(r'^(>=)(.*)', comparison_string)
            try:
                return float(value) >= float(temp.group(2))
            except:
                return False
        elif comparison_string.startswith('!='):
            temp = re.match(r'^(!=)(.*)', comparison_string)
            if temp.group(2) == 'None':
                return value is not None
            else:
                try:
                    return float(value) != float(temp.group(2))
                except:
                    return value != temp.group(2)
        elif comparison_string.startswith('>'):
            temp = re.match(r'^(>)(.*)', comparison_string)
            try:
                return float(value) > float(temp.group(2))
            except:
                return False
        elif comparison_string.startswith('<'):
            temp = re.match(r'^(<)(.*)', comparison_string)
            try:
                return float(value) < float(temp.group(2))
            except:
                return False
        elif comparison_string.startswith('='):
            temp = re.match(r'^(=)(.*)', comparison_string)
            if temp.group(2) == 'None':
                return value is None
            else:
                try:
                    return float(value) == float(temp.group(2))
                except:
                    return value == temp.group(2)
        elif comparison_string.startswith('like'):
            temp = re.match(r'^(like) (.*)', comparison_string)
            return value in temp.group(2)
        elif comparison_string.startswith('not like'):
            temp = re.match(r'^(not like) (.*)', comparison_string)
            return value not in temp.group(2)
        elif comparison_string.startswith('starts with'):
            temp = re.match(r'^(starts with) (.*)', comparison_string)
            return value.startswith(temp.group(2))
        elif comparison_string.startswith('ends with'):
            temp = re.match(r'^(ends with) (.*)', comparison_string)
            return value.endswith(temp.group(2))
        else:
            if comparison_string == 'None':
                return value is None
            else:
                try:
                    return float(value) == float(comparison_string)
                except:
                    return value == comparison_string
