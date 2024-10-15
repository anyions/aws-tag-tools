# 使用计算式

AWS Tag Tools 支持使用 Python 简单表达式的计算结果作为标签的键/值。 考虑到使用 Python `eval` 方法存在安全风险，因此在表达式中仅支持使用以下
Python 方法:

- `abs()`
- `int()`
- `str()`
- `float()`
- `math.*`
- `now()` (datetime.datetime.now 别名)
- `date()` (datetime.datetime.date 别名)
- `time()` (datetime.datetime.time 别名)
- `today()` (datetime.datetime.today 别名)
- `timedelta()` (datetime.timedelta 别名)

除此之外，在表达式中还可以使用内置变量 `env` 来访问环境变量，注意环境变量中不包括任何以 `'AWS_'` 开头的参数以防止敏感信息泄露。
