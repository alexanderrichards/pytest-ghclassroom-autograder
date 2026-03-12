import pytest
from pytest_jsonreport.plugin import JSONReport

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from base64 import b64encode
import json

class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"

@dataclass
class Test:
    name: str
    status: Status = Status.PASS
    message: str = ""
    test_code: str = ""
    task_id: int = 0
    filename: str = ""
    line_no: int = 0
    duration: float = 0.0
    score: float = 0.0

@dataclass
class Results:
    max_score: int = 0
    status: Status = Status.PASS
    tests: list[Test] = field(default_factory=list)

    def add(self, test: Test) -> None:
        """
        Add a Test to the list of tests.
        """
        match test.status:
            case Status.FAIL if self.status is Status.PASS:
                self.status = Status.FAIL
            case Status.ERROR if self.status is not Status.ERROR:
                self.status = Status.ERROR
                self.message = test.message
      
        self.tests.append(test)

    def json(self):
        return json.dumps(asdict(self), separators=(",", ":")).encode("utf-8")

status_lookup = {"passed": Status.PASS,
                 "failed": Status.FAIL,
                 "error": Status.ERROR}

plugin = JSONReport()
pytest.main(['--json-report-file=none', '-vv', "./tests"], plugins=[plugin])

report = plugin.report
n_tests = report['summary'].get("collected", 0)  # could use total instead of collected
result = Result(max_score=n_tests)
for test in report["tests"]:
    status = status_lookup.get(test["outcome"], Status.ERROR)
    score = 1 if status is Status.PASS else 0
    message = test['call']['stdout']  # lots of options here, check out https://pypi.org/project/pytest-json-report/#format
    result.add(Test(name=test["nodeid"],
                    status=status,
                    message=message,
                    score=score))


print(b64encode(result.json()).decode("utf-8"))

plugin.save_report('my_report.json')
