# 使用计算式

AWS Tag Tools 支持使用 Python 简单表达式的计算结果作为标签的键/值。计算式格式为：

```text
${in-line-python-expression}$
```

考虑到使用 Python `eval` 方法存在安全风险，因此在表达式中仅支持使用以下 Python 方法:

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

除此之外，在表达式中还可以使用内置变量 `env` 来访问环境变量中以 `AWSTT_`开头的参数，以及使用内置变量 `spec`
来访问资源特定的规格参数，具体参考 [规格说明](SPEC.md)
