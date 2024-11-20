# Use Expression

AWS Tag Tools supports using the computed result of a Python simple expression as the key/value of a tag. The expression
format is:

```text
${in-line-python-expression}$
```

Considering the security risks of using the Python `eval` method, only the following Python methods are supported in the
expression:

- `abs()`
- `int()`
- `str()`
- `float()`
- `math.*`
- `now()` (alias of datetime.datetime.now)
- `date()` (alias of datetime.datetime.date)
- `time()` (alias of datetime.datetime.time)
- `today()` (alias of datetime.datetime.today)
- `timedelta()` (alias of datetime.timedelta)

Additionally, the built-in variable `env` can be used in the expression to access environment variables. Note that
any environment variables starting with `'AWS_'` are excluded to prevent sensitive information leakage.

Additionally, the built-in variable `env` can be used in the expression to access environment variables starts
with `AWSTT_`. The built-in variable `spec` can be used to access resource-specific specification parameters.
For details, please refer to [Spec Description](SPEC.md).