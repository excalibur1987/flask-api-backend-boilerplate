import re
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from flask import Request


class TypedUserInfo(TypedDict):
    ip_address: str
    platform: str
    browser: str


def extract_request_info(request: "Request") -> TypedUserInfo:
    user_agent_regex = r".*\\(((windows|iphone|linux|macintosh|android|mobile|compatible).*(\\d|X))\\).*"
    os_reg = re.compile(user_agent_regex, re.IGNORECASE)

    return {
        "ip_address": request.remote_addr,
        "platform": request.user_agent.platform
        or (
            os_reg.match(request.user_agent.string).groups()[0]
            if os_reg.match(request.user_agent.string)
            else None
        ),
        "browser": request.user_agent.browser,
    }


def mobile_checker(mobile: str):
    return re.match(r"\+?\d*", mobile)
