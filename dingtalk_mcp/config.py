from typing import Optional
import os


class DingTalkConfig:
    """
    钉钉配置类
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        tenant_id: Optional[str] = None,
        base_url: str = "https://api.dingtalk.com",
        token_cache_ttl: int = 7200,
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self.tenant_id = tenant_id
        self.base_url = base_url
        self.token_cache_ttl = token_cache_ttl


def load_config() -> DingTalkConfig:
    """
    加载配置并进行验证

    Returns:
        DingTalkConfig: 配置对象

    Raises:
        ValueError: 如果缺少必要的配置或配置无效
    """
    import re
    
    # 验证 AppKey 格式
    def validate_app_key(app_key: str) -> bool:
        # 钉钉 AppKey 通常由字母和数字组成，长度约为 20-30 位
        return bool(re.match(r'^[a-zA-Z0-9]{20,30}$', app_key))
    
    # 验证 Appsecret 格式
    def validate_app_secret(app_secret: str) -> bool:
        # 钉钉 AppSecret 通常由字母和数字组成，长度约为 30-40 位
        return bool(re.match(r'^[a-zA-Z0-9]{30,40}$', app_secret))
    app_key = os.environ.get("DINGTALK_APP_KEY")
    app_secret = os.environ.get("DINGTALK_APP_SECRET")
    tenant_id = os.environ.get("DINGTALK_TENANT_ID")
    base_url = os.environ.get("DINGTALK_BASE_URL", "https://api.dingtalk.com")
    token_cache_ttl_str = os.environ.get("DINGTALK_TOKEN_CACHE_TTL", "7200")

    if not app_key:
        raise ValueError("缺少配置: DINGTALK_APP_KEY")
    if not validate_app_key(app_key):
        raise ValueError("无效的 DINGTALK_APP_KEY 格式")
    
    if not app_secret:
        raise ValueError("缺少配置: DINGTALK_APP_SECRET")
    if not validate_app_secret(app_secret):
        raise ValueError("无效的 DINGTALK_APP_SECRET 格式")

    try:
        token_cache_ttl = int(token_cache_ttl_str)
    except ValueError:
        token_cache_ttl = 7200

    return DingTalkConfig(
        app_key=app_key,
        app_secret=app_secret,
        tenant_id=tenant_id,
        base_url=base_url,
        token_cache_ttl=token_cache_ttl,
    )