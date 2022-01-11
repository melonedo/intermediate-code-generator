# intermediate-code-generator
[![CI](https://github.com/melonedo/intermediate-code-generator/actions/workflows/app.yaml/badge.svg)](https://github.com/melonedo/intermediate-code-generator/actions/workflows/app.yaml/)[实验报告](report/编译原理实验报告.md)

2021编译原理实验

## 运行测试
如果使用[pipenv](https://pipenv.pypa.io/en/latest/)，则
```shell
# pip install pipenv
pipenv install --dev
pipenv shell
pytest
```
如果需要卸载虚拟环境
```shell
pipenv --rm
```

另外也提供requirements.txt。

## LR分析表生成器
由于语法有歧义，生成器生成的语法需要手动编辑消除歧义。
```shell
git submodule update
pipenv shell
py intergen/tablegen.py
```

## 不足
- if-else部分采用的消歧义方法使得if实际上不能嵌套，直接用二义语法然后手动消歧义应该会更好。
- 不能自动生成LR分析表需要的产生式表。
