import pytest

from sysloghandler import SyslogHandler


def test_deserialize_message_with_fabx_message():
    # given
    msg = "<14>1 2022-12-19T13:52:13Z 9560aded6366 dev_fabx-dev_1 243434 - - 2022-12-19 13:52:13,067 DEBUG [eventLoopGroupProxy-4-2] c.f.f.WebApp: 200 OK (0.128383ms): GET - /actuator/health"
    testee = SyslogHandler()

    # when
    result = testee.deserialize_message(msg)

    # then
    assert result.pri_and_version == "<14>1"
    assert result.timestamp == "2022-12-19T13:52:13Z"
    assert result.hostname == "9560aded6366"
    assert result.app_name == "dev_fabx-dev_1"
    assert result.procid == "243434"
    assert result.msgid == "-"
    assert result.structured_data == "-"
    assert result.msg == "2022-12-19 13:52:13,067 DEBUG [eventLoopGroupProxy-4-2] c.f.f.WebApp: 200 OK (0.128383ms): GET - /actuator/health"
    assert result.timestamp2 == "2022-12-19 13:52:13,067"
    assert result.level == "DEBUG"
    assert result.thread == "[eventLoopGroupProxy-4-2]"
    assert result.clazz == "c.f.f.WebApp"
    assert result.msg2 == "200 OK (0.128383ms): GET - /actuator/health"


def test_deserialize_message_with_other_message():
    # given
    msg = "<11>1 2022-12-18T10:21:57Z 4511aaa38c23 dev_logspout_1 243651 - - some message"
    testee = SyslogHandler()

    # when
    result = testee.deserialize_message(msg)

    # then
    assert result.timestamp == "2022-12-18T10:21:57Z"
    assert result.hostname == "4511aaa38c23"
    assert result.app_name == "dev_logspout_1"
    assert result.procid == "243651"
    assert result.msgid == "-"
    assert result.structured_data == "-"
    assert result.msg == "some message"
    assert result.timestamp2 is None
    assert result.level is None
    assert result.thread is None
    assert result.clazz is None
    assert result.msg2 is None


@pytest.mark.parametrize(
    ("msg", "expected_result"),
    [
        (
                "<14>1 2022-12-19T13:52:13Z 9560aded6366 dev_fabx-dev_1 243434 - - 2022-12-19 13:52:13,067 DEBUG [eventLoopGroupProxy-4-2] c.f.f.WebApp: 200 OK (0.128383ms): GET - /actuator/health",
                False
        ),
        (
                "<11>1 2022-12-18T10:21:59Z 9560aded6366 dev_fabx-dev_1 243434 - - INFO: Successfully released change log lock",
                False
        ),
        (
                "<14>1 2022-12-18T10:21:57Z 9560aded6366 dev_fabx-dev_1 243434 - - 2022-12-18 10:21:57,517 INFO [main] c.f.f.App: bla bla",
                True
        ),
        (
                "<11>1 2022-12-18T10:21:57Z 4511aaa38c23 dev_logspout_1 243651 - - 2022/12/18 10:21:57 # logspout v3.2.14 by gliderlabs",
                False
        ),
        (
                "<11>1 2022-12-18T10:21:57Z 4511aaa38c23 dev_logspout_1 243651 - - 2022/12/18 10:21:57 InFO",
                True
        ),
    ]
)
def test_info_filter(msg: str, expected_result: bool):
    # given
    testee = SyslogHandler()
    message = testee.deserialize_message(msg)

    # when
    result = testee.info_filter(message)

    # then
    assert result == expected_result


@pytest.mark.parametrize(
    ("msg", "expected_result"),
    [
        (
                "<14>1 2022-12-19T13:52:13Z 9560aded6366 dev_fabx-dev_1 243434 - - 2022-12-19 13:52:13,067 WARN [eventLoopGroupProxy-4-2] c.f.f.WebApp: 200 OK (0.128383ms): GET - /actuator/health",
                True
        ),
        (
                "<11>1 2022-12-18T10:21:59Z 9560aded6366 dev_fabx-dev_1 243434 - - Info: Successfully released change log lock",
                False
        ),
        (
                "<14>1 2022-12-18T10:21:57Z 9560aded6366 dev_fabx-dev_1 243434 - - 2022-12-18 10:21:57,517 INFO [main] c.f.f.App: bla bla",
                False
        ),
        (
                "<11>1 2022-12-18T10:21:57Z 4511aaa38c23 dev_logspout_1 243651 - - 2022/12/18 10:21:57 # logspout v3.2.14 by gliderlabs",
                False
        ),
        (
                "<11>1 2022-12-18T10:21:57Z 4511aaa38c23 dev_logspout_1 243651 - - 2022/12/18 10:21:57 ErRoR",
                True
        ),
    ]
)
def test_alert_filter(msg: str, expected_result: bool):
    # given
    testee = SyslogHandler()
    message = testee.deserialize_message(msg)

    # when
    result = testee.alert_filter(message)

    # then
    assert result == expected_result
